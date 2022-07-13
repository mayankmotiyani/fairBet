""" Here we will create algorithm for updating the loss and profit of each user """
import pandas as pd
import numpy as np
from django_pandas.io import read_frame
from .models import Betting
from django.db.models import F, Q, When, Value, Case, Sum, OuterRef, Subquery
from payment.models import Wallet



def handle_all_betting_(matchName,winningTeam):
    """
        first we need to update the winning_team
    """
    """  
        will filter according to match_name and Case When Conditional Statement to update the loss_profit
        This function will automatic update loss or profit of each user on particular match.
        and also update the wallet of each user.
    """
    Betting.objects.filter(match=matchName).update(winning_team=winningTeam,is_closed=True)
    betting_instance = Betting.objects.filter(
        match = matchName,
        winning_team = winningTeam,
        is_closed=True
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

    subquery = Betting.objects.filter(
        user_id=OuterRef('user_id'),
        match = matchName,
        winning_team = winningTeam
    ).values(
        'user__id'
    ).annotate( 
        total_amount=Sum('loss_profit')
    ).values(
        'total_amount'
    )
 
    betting_user_list = set(Betting.objects.filter(match = matchName,winning_team = winningTeam).values_list("user_id",flat=True))
    betting_user_list = list(betting_user_list)
    """ update wallet """
    Wallet.objects.filter(user_id__in=list(betting_user_list)).update(amount=F('amount')+Subquery(subquery))
    

    
    



