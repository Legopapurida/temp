from django.contrib import admin
from .models import OTPDevice, OTPToken

@admin.register(OTPDevice)
class OTPDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'email')
    readonly_fields = ('created_at',)

@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ('device', 'token', 'is_used', 'created_at', 'used_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('device__user__username', 'device__email', 'token')
    readonly_fields = ('created_at', 'used_at')
    
    def has_add_permission(self, request):
        return False  # Tokens should only be created programmatically