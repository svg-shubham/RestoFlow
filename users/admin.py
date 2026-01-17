from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):
  model = User
  list_display = ['username', 'email', 'role', 'is_staff']
  fieldsets = UserAdmin.fieldsets + (
      (None, {'fields': ('role',)}),
  )
  add_fieldsets = UserAdmin.add_fieldsets + (
      (None, {'fields': ('role',)}),
  )

admin.site.register(User,CustomUserAdmin)