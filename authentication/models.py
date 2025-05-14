from django.db import models
from core.models import Users

class OTPRequest(models.Model):
    user       = models.ForeignKey(Users, on_delete=models.CASCADE)
    secret     = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used       = models.BooleanField(default=False)

    class Meta:
        db_table = 'otp_requests'
