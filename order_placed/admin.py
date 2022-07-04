from django.contrib import admin
from .models import (
    Betting
)
# Register your models here.

class BettingAdmin(admin.ModelAdmin):
    model = Betting
    list_display = ["id","user","amount","odds","status","bet_on_team","winning_team","match","loss_profit"]
    
admin.site.register(Betting, BettingAdmin)