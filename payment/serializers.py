from .models import Order, Wallet
from rest_framework import serializers
from datetime import datetime

class OrderForm(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class WalletSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.SerializerMethodField()
    class Meta:
        model = Wallet
        fields = ['user','wallet_balance']
        depth = 1


    def get_wallet_balance(self,obj):
        wallet_balance = obj.amount
        return wallet_balance

    
    def to_representation(self,obj):
        instance = super(WalletSerializer,self).to_representation(obj)
        # 2022-06-29T14:38:15.161915+05:30
        instance['user']['created'] = datetime.strptime(instance['user']['created'],"%Y-%m-%dT%H:%M:%S.%f+05:30").strftime("%d-%m-%Y %I:%M %p")
        instance['user']['updated'] = datetime.strptime(instance['user']['updated'],"%Y-%m-%dT%H:%M:%S.%f+05:30").strftime("%d-%m-%Y %I:%M %p")

        return instance