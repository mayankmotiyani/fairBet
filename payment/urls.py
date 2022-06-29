from django.urls import path
from .views import (
    payment_home, 
    order_payment, 
    callback, 
    RazorPayOrderForm, 
    CallbackView, 
    WalletAPI
)
urlpatterns = [
    path('payment/',payment_home),
    path('order_payment/', order_payment, name="payment"),
    path('callback/', CallbackView.as_view(), name="razorpay-callback"),
    path('razorPay/',RazorPayOrderForm.as_view(),name='razorpay'),
    path('get_wallet/',WalletAPI.as_view(), name="get-wallet"),
]