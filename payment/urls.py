from django.urls import path
from .views import payment_home, order_payment, callback, RazorPayOrderForm, CallbackView

urlpatterns = [
    path('payment/',payment_home),
    path("order_payment/", order_payment, name="payment"),
    path("callback/", CallbackView.as_view(), name="callback"),
    path('razorPay/',RazorPayOrderForm.as_view()),
]