from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
import json
from fairbet_auth_app.models import (
    Profile
)
from .models import (
    Betting
)
from .serializers import (
    BettingSerializer
)

from payment.models import (
    Wallet
)


# Create your views here.


class WalletBalanceCheck(APIView):
    def get(self,request,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_logged_in_user_profile = Profile.objects.get(user_id=get_logged_in_user)
            get_logged_in_user_name = valid_data['username']
            aggregate_betting_amount = Betting.objects.filter(user_id=get_logged_in_user_profile.id).values("user_id").annotate(get_amount = Sum("amount")).values("get_amount")
            get_current_wallet_balance = Wallet.objects.get(user_id=get_logged_in_user_profile.id)
            get_actual_wallet_balance = get_current_wallet_balance.amount - aggregate_betting_amount[0]['get_amount']
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":{
                    "amount" : get_actual_wallet_balance
                }
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_200_OK)



class BettingOrderAPI(APIView):
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
        get_json = request.data['bet_json']
        get_json = json.loads(get_json)
        """ here we will check your wallet balance """
        try:
            if get_json['placeAmount'] <= 0:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response":"stake should not be less than zero"
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
            else:
                get_json['user'] = get_logged_in_user_profile.id
                betting_instance = Betting.objects.create(
                    user_id = get_json['user'],
                    amount = get_json['placeAmount'],
                    bet_on_team = get_json['betOnTeam'],
                    status = get_json['orderStatus'],
                    odds = get_json['Odds'],
                    match = get_json['liveMatch']
                )
                betting_instance.save()
                """ taking wallet instance """
                wallet_instance = Wallet.objects.get(user_id=get_logged_in_user_profile.id)
                wallet_instance.amount -= betting_instance.amount
                wallet_instance.save()
                context = {
                    "status":status.HTTP_201_CREATED,
                    "success":True,
                    "response":"Successfully Placed Order!"
                }
                return Response(context,status = status.HTTP_201_CREATED)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status = status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
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
        betting_instance = Betting.objects.filter(user_id=get_logged_in_user_profile.id)
        serializer = BettingSerializer(betting_instance,many=True)
        context = {
            "status" : status.HTTP_200_OK,
            "success":True,
            "response":serializer.data
        }
        return Response(context,status = status.HTTP_200_OK)
        