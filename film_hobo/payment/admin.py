from django.contrib import admin

from .models import PaymentOptions, Transaction

# Register your models here.

admin.site.register(PaymentOptions)
admin.site.register(Transaction)
