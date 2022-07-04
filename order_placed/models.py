from django.db import models
from fairbet_auth_app.models import (
    Profile
)
from django.utils.translation import gettext_lazy as _
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
# Create your models here.


class Betting(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    orderStatus = (
        ('B','BACK'),
        ('L','LAY')
    )
    user = models.ForeignKey(Profile,on_delete=models.CASCADE)
    amount = models.FloatField(
        _('placedAmount'))
    bet_on_team = models.CharField(
        _('betOnTeam'),max_length=100,null=True)
    status = models.CharField(
        _('Status'),max_length=100,choices=orderStatus)
    odds = models.FloatField(
        _('Odds'),null=True)
    winning_team = models.CharField(
        _('winningTeam'),max_length=100,null=True,blank=True,default="Not declared yet")
    loss_profit = models.FloatField(
        _('lossProfit'),null=True,default=0.0)
    match = models.CharField(_("liveMatch"),max_length=100,null=True,blank=True,default="")
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    
    # def __str__(self):
    #     return 'user:{}, placedAmount:{}, Status:{}, Odds:{}, winningTeam:{}, lossProfit{}'.format(self.user,self.amount,self.bet_on_team,self.odds,self.winning_team,self.loss_profilt,)
    
    


    
