from django.urls import path
from .views import ( 
    RazorPayOrderForm, 
    CallbackView, 
    WalletAPI,
    OrderHistory,
    RandomODDS,
    GetTransactionStatus,
    home
)
urlpatterns = [
    path('payment/',home,name='home'),
    path('callback/',CallbackView.as_view(), name="razorpay-callback"),
    path('razorPay/',RazorPayOrderForm.as_view(),name='razorpay'),
    path('get_wallet/',WalletAPI.as_view(), name="get-wallet"),
    path('get_history/',OrderHistory.as_view(),name='get-history'),
    path('get_random_odds/',RandomODDS.as_view(),name='get-random-odds'),
    path('get_status/',GetTransactionStatus.as_view(),name='get-status')
]