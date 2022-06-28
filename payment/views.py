from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .models import Order
from .constants import PaymentStatus
import json
from rest_framework.views import APIView
from .serializers import OrderForm
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
def payment_home(request):
    return render(request, 'payment/index.html')

# def verify_signature(response_data):
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#         print(client.utility.verify_payment_signature(response_data))
#         return client.utility.verify_payment_signature(response_data)


class RazorPayOrderForm(APIView):
    def post(self, request, *args, **kwargs):
        # name = request.data["name"]
        # amount = request.data["amount"]
        name = "Mayank"
        amount = "400"
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            name=name, amount=amount, provider_order_id=razorpay_order["id"]
        )
        data = {
            "name" : name,
            "merchantId": settings.RAZOR_KEY_ID,
            "amount": amount,
            "currency" : 'INR' ,
            "orderId" : razorpay_order["id"],
        }
        return Response(data,status=status.HTTP_200_OK)


class CallbackView(APIView):
    def post(self, request, *args, **kwargs):
        response = request.data
        print(response)
        if "razorpay_signature" in response:
            razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            data = razorpay_client.utility.verify_payment_signature(response)
            if data:
                payment_object = Order.objects.get(provider_order_id = response['razorpay_order_id'])
                payment_object.payment_id = response['razorpay_payment_id']
                payment_object.signature_id = response['razorpay_signature']
                payment_object.status = PaymentStatus.SUCCESS
                payment_object.save()
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


def order_payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
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
                "razorpay_key": settings.RAZOR_KEY_ID,
                "order": order,
            },
        )
    return render(request, "payment.html")

@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
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