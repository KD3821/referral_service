from django.contrib import admin
from .models import User, TemporaryUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone', 'referralcode', 'invitecode', 'created_at', 'admin', 'is_invited', 'is_inviter']
    list_filter = ['phone', 'invitecode']


@admin.register(TemporaryUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone', 'passcode']
    list_filter = ['phone']

