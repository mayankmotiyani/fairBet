from django.urls import path
from .views import (
    BettingOrderAPI,
    WalletBalanceCheck
)

urlpatterns = [

    path('placed_bet/',BettingOrderAPI.as_view(),name='place-bet'),
    path('wallet_balance_check/',WalletBalanceCheck.as_view(),name='wallet-balance-check')
    
]