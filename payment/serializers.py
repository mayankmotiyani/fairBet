from .models import Order, Wallet
from rest_framework import serializers


class OrderForm(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
