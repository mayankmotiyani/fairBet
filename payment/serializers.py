from .models import Order, Wallet
from rest_framework import serializers
from datetime import datetime
from fairbet_auth_app.models import (
    Profile
)

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        depth = True
    
    def to_representation(self,obj):
        instance = super(OrderSerializer,self).to_representation(obj)
        # instance['created'] = datetime.strptime(instance['created'],"%Y-%m-%dT%H:%M:%S.%f+05:30").strftime("%d-%m-%Y %I:%M %p")
        # instance['updated'] = datetime.strptime(instance['updated'],"%Y-%m-%dT%H:%M:%S.%f+05:30").strftime("%d-%m-%Y %I:%M %p")
        del instance['signature_id']
        return instance


class WalletSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.SerializerMethodField()
    class Meta:
        model = Wallet
        fields = ['user','wallet_balance']
        depth = True


    def get_wallet_balance(self,obj):
        wallet_balance = obj.amount
        return wallet_balance

    
    def to_representation(self,obj):
        instance = super(WalletSerializer,self).to_representation(obj)
        instance['user']['username'] = Profile.objects.get(user_id=instance['user']['user']).user.username
        instance['user']['created'] = datetime.strptime(instance['user']['created'],"%Y-%m-%dT%H:%M:%S.%f+05:30").strftime("%d-%m-%Y %I:%M %p")
        instance['user']['updated'] = datetime.strptime(instance['user']['updated'],"%Y-%m-%dT%H:%M:%S.%f+05:30").strftime("%d-%m-%Y %I:%M %p")

        return instance