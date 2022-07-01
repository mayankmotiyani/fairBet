from django.contrib import admin
from .models import Order, Wallet
# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ['id','user','amount','status','provider_order_id','payment_id','signature_id','created','updated']

class WalletAdmin(admin.ModelAdmin):
    model = Wallet
    list_display = ['id','user','amount']

admin.site.register(Order,OrderAdmin)
admin.site.register(Wallet,WalletAdmin)