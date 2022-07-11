from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from fairbet_auth_app.models import Profile
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from payment.models import (
    Wallet
)
from datetime import datetime, date
import re

reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
passObj = re.compile(reg)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        email = attrs.get("email", None)
        password = attrs.get("password", None)
        try:
            user_instance = User.objects.get(email__iexact=email)
        except Exception as exception:
            data = dict()
            data['status'] = status.HTTP_401_UNAUTHORIZED
            data['response'] = "User is not exists.Please Register first!"
            return data
        user = authenticate(username=user_instance.username, password=password)
        if user is not None:
            refresh = self.get_token(user)
            data = dict()
            data['status'] = status.HTTP_200_OK
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            data['username'] = user_instance.username
            return data
        elif user is None:
            data = dict()
            data['status'] = status.HTTP_401_UNAUTHORIZED
            data['response'] = "Incorrect Password!"
            return data
            
            
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        return token
    
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    mobile_number = serializers.CharField(write_only=True, required=True,validators=[UniqueValidator(queryset=Profile.objects.all())])
    birth_date = serializers.DateField(write_only=True, required=True)
    gender = serializers.CharField(write_only=True, required=True)
    source = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email','mobile_number','birth_date','gender','source')

    def validate(self, attrs):
        today = date.today()
        birthdate = datetime.strptime(str(attrs['birth_date']),"%Y-%m-%d")
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))     
        pass_regex1 = re.search(passObj, attrs['password'])
        pass_regex2 = re.search(passObj, attrs['password2'])

        if not pass_regex1 and not pass_regex2:
            raise serializers.ValidationError({"password": "Invalid Password!"})
        elif age <= 18: 
            raise serializers.ValidationError({"birth_date": "Age should be 18 above!"})
        elif attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
        
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        profile = Profile.objects.create(
            user = user,
            mobile_number = validated_data['mobile_number'],
            birth_date = validated_data['birth_date'],
            gender = validated_data['gender'],
            source = validated_data['source'],
        )
        profile.save()
        wallet_instance = Wallet.objects.create(user=profile)
        wallet_instance.save()
        return user