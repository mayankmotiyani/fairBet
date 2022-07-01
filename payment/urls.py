from django.urls import path
from .views import ( 
    RazorPayOrderForm, 
    CallbackView, 
    WalletAPI,
    OrderHistory,
    home
)
urlpatterns = [
    path('callback/', CallbackView.as_view(), name="razorpay-callback"),
    path('razorPay/',RazorPayOrderForm.as_view(),name='razorpay'),
    path('get_wallet/',WalletAPI.as_view(), name="get-wallet"),
    path('get_history/',OrderHistory.as_view(),name='get-history'),
    path('index',home)
]