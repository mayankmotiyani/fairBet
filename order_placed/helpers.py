""" Here we will create algorithm for updating the loss and profit of each user """
import pandas as pd
import numpy as np
from django_pandas.io import read_frame
from .models import Betting
from django.db.models import F, Q, When, Value, Case

def handle_all_bettings(matchName,winningTeam):
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


