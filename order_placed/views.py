from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
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



class BettingOrderAPI(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_logged_in_user_profile = Profile.objects.get(user_id=get_logged_in_user)
            get_logged_in_user_name = valid_data['username']
            print(get_logged_in_user)
            print(get_logged_in_user_profile.id)
            print(get_logged_in_user_name)
        except Exception as exception:
            context = {
                "status":status.HTTP_401_UNAUTHORIZED,
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
                    "response":"stake should not be less than zero"
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
            wallet_instance = get_object_or_404(Wallet,user_id=get_logged_in_user_profile.id)
            get_wallet_amount = wallet_instance.amount
            if get_json['placeAmount'] > get_wallet_amount and get_json['placeAmount'] != get_wallet_amount:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "response":"Insufficient credit limit"
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
                    "response":"Successfully Placed Order and Wallet Updated!"
                }
                return Response(context,status = status.HTTP_201_CREATED)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
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
                "response":"Given token not valid for any token type",
                "exception":str(exception)
            }
            return Response(context,status = status.HTTP_401_UNAUTHORIZED)
        betting_instance = Betting.objects.filter(user_id=get_logged_in_user_profile.id)
        serializer = BettingSerializer(betting_instance,many=True)
        context = {
            "status" : status.HTTP_200_OK,
            "response":serializer.data
        }
        return Response(context,status = status.HTTP_200_OK)
        