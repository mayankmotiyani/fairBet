import os
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse
from .models import Order
from .constants import PaymentStatus
import json
from rest_framework.views import APIView
from .serializers import OrderForm
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.backends import TokenBackend
from dotenv import load_dotenv, find_dotenv
from .models import (
    Wallet,
    )
from .serializers import (
    WalletSerializer
    )

from fairbet_auth_app.models import (
    Profile
)

load_dotenv(find_dotenv())



# Create your views here.
def payment_home(request):
    return render(request, 'payment/index.html')

# def verify_signature(response_data):
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#         print(client.utility.verify_payment_signature(response_data))
#         return client.utility.verify_payment_signature(response_data)

#for production
class RazorPayOrderForm(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            print(valid_data)
            get_logged_in_user = valid_data['user_id']
            get_logged_in_user_profile = Profile.objects.get(user_id=get_logged_in_user)
            get_logged_in_user_name = valid_data['username']
        except Exception as exception:
            context = {
                "status":status.HTTP_401_UNAUTHORIZED,
                "response":"Given token not valid for any token type",
                "exception":str(exception)
            }
            return Response(context,status = status.HTTP_401_UNAUTHORIZED)
        amount = request.data["amount"]
        client = razorpay.Client(auth=(os.environ['RAZOR_KEY_ID'], os.environ['RAZOR_KEY_SECRET']))
        razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            user_id=get_logged_in_user_profile.id, amount=amount, provider_order_id=razorpay_order["id"]
        )
        data = {
            "name" : get_logged_in_user_profile.user.username,
            "merchantId": os.environ['RAZOR_KEY_ID'],
            "amount": amount,
            "currency" : 'INR',
            "orderId" : razorpay_order["id"],
        }
        return Response(data,status=status.HTTP_200_OK)

#for production
class CallbackView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', "").split(' ')[1] 
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=True)
            get_logged_in_user = valid_data['user_id']
            get_logged_in_user_profile = Profile.objects.get(user_id=get_logged_in_user)
            get_logged_in_user_name = valid_data['username']
        except Exception as exception:
            context = {
                "status":status.HTTP_401_UNAUTHORIZED,
                "response":"Given token not valid for any token type"
            }
            return Response(context,status = status.HTTP_401_UNAUTHORIZED)
        response = request.data
        if "razorpay_signature" in response:
            razorpay_client = razorpay.Client(auth=(os.environ['RAZOR_KEY_ID'], os.environ['RAZOR_KEY_SECRET']))
            data = razorpay_client.utility.verify_payment_signature(response)
            if data:
                payment_object = Order.objects.get(provider_order_id = response['razorpay_order_id'])
                payment_object.payment_id = response['razorpay_payment_id']
                payment_object.signature_id = response['razorpay_signature']
                payment_object.status = PaymentStatus.SUCCESS
                payment_object.save()
                """ Here We will create wallet instance after payment getting successfully """
                if Wallet.objects.filter(user_id=get_logged_in_user_profile.id).exists():
                    wallet_instance = Wallet.objects.get(user_id=get_logged_in_user_profile.id)
                    wallet_instance.amount+=payment_object.amount
                    wallet_instance.save()
                else:
                    wallet_instance = Wallet.objects.create(user_id=get_logged_in_user_profile.id,amount=payment_object.amount)
                    wallet_instance.save()
                return Response({'status': 'Payment Done'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'Signature Mismatch!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_code = response['error[code]']
            error_description = response['error[description]']
            error_source = response['error[source]']
            error_reason = response['error[reason]']
            error_metadata = json.loads(response['error[metadata]'])
            razorpay_payment = Order.objects.get(provider_order_id=error_metadata['order_id'])
            razorpay_payment.payment_id = error_metadata['payment_id']
            razorpay_payment.signature_id = "None"
            razorpay_payment.status = PaymentStatus.FAILURE
            razorpay_payment.save()
            error_status = {
                'error_code': error_code,
                'error_description': error_description,
                'error_source': error_source,
                'error_reason': error_reason,
            }
            return Response({'error_data': error_status}, status=status.HTTP_401_UNAUTHORIZED)



# for local
def order_payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        client = razorpay.Client(auth=(os.environ['RAZOR_KEY_ID'], os.environ['RAZOR_KEY_SECRET']))
        razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            name=name, amount=amount, provider_order_id=razorpay_order["id"]
        )
        order.save()
        return render(
            request,
            "payment/payment.html",
            {
                "callback_url": "https://" + "fairbet.herokuapp.com" + "/callback/",
                "razorpay_key": os.environ['RAZOR_KEY_ID'],
                "order": order,
            },
        )
    return render(request, "payment.html")

@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(os.environ['RAZOR_KEY_ID'], os.environ['RAZOR_KEY_SECRET']))
        print(client.utility.verify_payment_signature(response_data))
        return client.utility.verify_payment_signature(response_data)
    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return render(request, "payment/callback.html", context={"status": order.status})
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return render(request, "payment/callback.html", context={"status": order.status})
    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()
        return render(request, "payment/callback.html", context={"status": order.status})


class WalletAPI(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', "").split(' ')[1]
        try:
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            print(valid_data['user_id'])
            print(valid_data['username'])
            instance = Wallet.objects.get(user_id=valid_data['user_id'])
            serializer = WalletSerializer(instance)
            return Response({"status":status.HTTP_200_OK,"data":serializer.data},status=status.HTTP_200_OK)
        except Exception as exception:
            return Response(str(exception))

        