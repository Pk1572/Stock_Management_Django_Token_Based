from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Company
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'role', 'is_active', 'is_staff', 'company')
    list_filter = ('role', 'is_active', 'is_staff', 'company')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('phone_number', 'role', 'company')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_number', 'password1', 'password2', 'role', 'company', 'is_active', 'is_staff'),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_address', 'phone_number')
    search_fields = ('company_name', 'company_address')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Company, CompanyAdmin)
