""" Here we will create algorithm for updating the loss and profit of each user """
import pandas as pd
import numpy as np
from django_pandas.io import read_frame
from .models import Betting
from django.db.models import F, Q, When, Value, Case, Sum
from payment.models import Wallet

def handle_all_betting_(matchName,winningTeam):
    """ will filter according to match_name and Case When Conditional Statement """

    betting_instance = Betting.objects.filter(
        match = matchName
    ).update(
        loss_profit = Case(
            When(
                status = "B",
                bet_on_team = winningTeam,
                winning_team = winningTeam,
                then = F('amount') * F("odds") - F("amount")),
            When(
                ~Q(bet_on_team = winningTeam),
                status = "B",
                winning_team = winningTeam,
                then = -F('amount')),
             When(
                status = "L",
                bet_on_team = winningTeam,
                winning_team = winningTeam,
                then = F('amount') * - F("odds") + F("amount")),
             When(
                 ~Q(bet_on_team = winningTeam),
                status = "L",
                winning_team = winningTeam,
                then = F('amount')),
            default=F("loss_profit")
            )
        )
    
    df = read_frame(Betting.objects.filter(match=matchName,winning_team=winningTeam).values("user__id","user_id","user_id__wallet__amount").annotate(loss_or_profit = Sum("loss_profit")))
    df['total'] = df['user_id__wallet__amount'] + df['loss_or_profit']
    wallet_dict = df.transpose().to_dict()
    update_wallet_instance = [Wallet(
        user_id = value.get("user__id",""),
        amount = value.get("total",""),
        ) for key,value in wallet_dict.items()]
    Wallet.objects.bulk_update_or_create(update_wallet_instance,['user_id','amount'],match_field=['user_id'])
    

    
    



