import os
import random
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse
from .models import Order
from .constants import PaymentStatus, TransactionStatus
import json
from rest_framework.views import APIView
from .serializers import OrderSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.backends import TokenBackend
from dotenv import load_dotenv, find_dotenv
from django.db.models import F, Q, When, Value, Case, Sum, OuterRef, Subquery
from django.db.models.functions import Concat
load_dotenv(find_dotenv())
import pandas as pd
import numpy as np
from .models import (
    Wallet,
    Order
    )
from .serializers import (
    WalletSerializer
    )
from fairbet_auth_app.models import (
    Profile
)
from order_placed.models import (
    Betting
)

from order_placed.helpers import handle_all_betting_

class GetTransactionStatus(APIView):
    def get(self,request, *args, **kwargs):
        get_transaction_status = [value for key,value in vars(TransactionStatus).items() if key.isupper()]
        get_payment_status = [value for key,value in vars(PaymentStatus).items() if key.isupper()]
        status_dict = {}
        status_dict['transaction_status'] = get_transaction_status
        status_dict['payment_status'] = get_payment_status

        context = {
            "status":status.HTTP_200_OK,
            "success":True,
            "response":status_dict
        }
        return JsonResponse(context,status=status.HTTP_200_OK)
        


def home(request):
    orders = Order.objects.all().update(transaction_status="Payment_Gateway To Wallet")
    orders.save()
    # handle_all_betting_("England vs India","England")
    return render(request, 'payment/index.html')

class RazorPayOrderForm(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_logged_in_user_profile = Profile.objects.get(user_id=get_logged_in_user)
            get_logged_in_user_name = valid_data['username']
        except Exception as exception:
            context = {
                "status":status.HTTP_401_UNAUTHORIZED,
                "success":False,
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
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1] 
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
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
        response = request.data
        if "razorpay_signature" in response:
            razorpay_client = razorpay.Client(auth=(os.environ['RAZOR_KEY_ID'], os.environ['RAZOR_KEY_SECRET']))
            data = razorpay_client.utility.verify_payment_signature(response)
            if data:
                payment_object = Order.objects.get(provider_order_id = response['razorpay_order_id'])
                payment_object.payment_id = response['razorpay_payment_id']
                payment_object.signature_id = response['razorpay_signature']
                payment_object.status = PaymentStatus.SUCCESS
                payment_object.transaction_status = TransactionStatus.P_TO_W
                payment_object.save()
                """ Here We will create wallet instance after payment getting successfully """
                if Wallet.objects.filter(user_id=get_logged_in_user_profile.id).exists():
                    wallet_instance = Wallet.objects.get(user_id=get_logged_in_user_profile.id)
                    wallet_instance.amount += payment_object.amount
                    wallet_instance.save()
                else:
                    instance = Wallet.objects.create(user_id=get_logged_in_user_profile.id,amount=payment_object.amount)
                    instance.save()
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


class WalletAPI(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', "").split(' ')[1]
        try:
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_logged_in_user_profile = Profile.objects.get(user_id=get_logged_in_user)
            get_logged_in_user_name = valid_data['username']
            instance = Wallet.objects.get(user_id=get_logged_in_user_profile.id)
            serializer = WalletSerializer(instance)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "data":serializer.data 
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


class OrderHistory(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', "").split(' ')[1]
        try:
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_logged_in_user_profile = Profile.objects.get(user_id=get_logged_in_user)
            get_logged_in_user_name = valid_data['username']
            if request.data:
                get_json = request.data
                instance = Order.objects.filter(user_id=get_logged_in_user_profile.id,created__date__gte=get_json['from'],created__date__lte=get_json['to'],status=get_json['payment_status'],transaction_status__icontains=get_json['transaction_status'])
                serializer = OrderSerializer(instance,many=True)
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":serializer.data
                }
                return Response(context,status=status.HTTP_200_OK)
            else:
                try:
                    instance = Order.objects.filter(user_id=get_logged_in_user_profile.id)
                    serializer = OrderSerializer(instance,many=True)
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response":serializer.data
                    }
                    return Response(context, status=status.HTTP_200_OK)
                except Exception as exception:
                    context = {
                        "status":status.HTTP_400_BAD_REQUEST,
                        "success":False,
                        "response":str(exception)
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
 

class RandomODDS(APIView):
    def get(self, request, *args, **kwargs):
        random_df = {}
        random_df['team1Back'] = float("{:.2f}".format(random.uniform(1.0,3.0)))
        random_df['team1Lay'] = float("{:.2f}".format(random.uniform(1.0,3.0)))
        random_df['team2Back'] = float("{:.2f}".format(random.uniform(1.0,3.0)))
        random_df['team2Lay'] = float("{:.2f}".format(random.uniform(1.0,3.0)))
        context = {
            "status":status.HTTP_200_OK,
            "success":True,
            "response":random_df
        }
        return Response(context,status=status.HTTP_200_OK)
