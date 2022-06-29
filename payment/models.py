from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from .constants import PaymentStatus
from fairbet_auth_app.models import Profile
# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(Profile,null=True,on_delete=models.CASCADE)
    amount = models.FloatField(_("Amount"), null=False, blank=False)
    status = CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )

    created = models.DateTimeField(auto_now_add=True,null=True)
    updated = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return f"{self.id}-{self.user.username}-{self.status}"

    
class Wallet(models.Model):
    user = models.ForeignKey(Profile,on_delete=models.CASCADE)
    amount = models.FloatField(_("Balance"),default=0.0)

    def __str__(self):
        return f"{self.user.user.username}"
