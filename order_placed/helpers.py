""" Here we will create algorithm for updating the loss and profit of each user """
import pandas as pd
import numpy as np
from django_pandas.io import read_frame
from .models import Betting
from django.db.models import F, Q, When, Value

def handle_all_bettings(matchName,winningTeam):
    """ will filter according to match_name """
    df = read_frame(Betting.objects.all())
    df['winning_team'] = winningTeam

    def CalculateLossProfit_userBetting(row,winningTeam):
        if row.status == "BACK" and row.bet_on_team == winningTeam and row.winning_team == winningTeam:
            return row.amount * row.odds - row.amount 
        elif row.status == "BACK" and row.bet_on_team == winningTeam and row.bet_on_team != winningTeam:
            return -row.amount
        elif row.status == "LAY" and row.bet_on_team == winningTeam and row.bet_on_team == winningTeam:
            return row.amount * - row.odds + row.amount
        elif row.status == "LAY" and row.bet_on_team == winningTeam and row.bet_on_team != winningTeam:
            return row.amount
    df['Loss/Profit'] = df.apply(CalculateLossProfit_userBetting,axis=1)

    return df

    
# Betting.objects.update(
#     loss_profit=Case(
#         When(status="B",
#              match="Srilanka vs India",
#              winning_team = "Not declared yet",
#              then=F("amount")*F("odds") - F("amount")),
#         When(status="L",
#              match="Srilanka vs India",
#              winning_team = "Not declared yet",
#              then=F("amount")* -F("odds") + F("amount")),
#         default=F("loss_profit")
# )
#      )

