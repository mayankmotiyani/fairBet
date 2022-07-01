from django.urls import path
from .views import (
    BettingOrderAPI
)

urlpatterns = [

    path('placed_bet/',BettingOrderAPI.as_view(),name='place-bet')
    
]