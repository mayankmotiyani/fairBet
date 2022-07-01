from rest_framework import serializers
from .models import (
    Betting
)

class BettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Betting
        fields = "__all__"

    
    def to_representation(self, obj):
        instance = super(BettingSerializer, self).to_representation(obj)
        if instance['status'] == "B":
            instance['status'] = "BACK"
        elif instance['status'] == "L":
            instance['status'] = "LAY"
        
        return instance