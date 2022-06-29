from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import *

urlpatterns = [
    
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),

]