from django.contrib import admin
from .models import (
    Profile
)
# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ['id','user','mobile_number','birth_date','gender','source','created','updated']

admin.site.register(Profile, ProfileAdmin)