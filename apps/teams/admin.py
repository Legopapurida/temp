from django.contrib import admin
from .models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'is_featured', 'order')
    list_filter = ('role', 'is_featured')
    search_fields = ('name', 'bio')
    ordering = ('order', 'name')