from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'city', 'postal_code')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('email',)
    actions = ['activate_users', 'deactivate_users']

    fieldsets = (
        (None, {
            "fields": ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'middle_name',
                      'city', 'street', 'house_number',
                      'apartment_number', 'postal_code')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                      'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',
                      'is_active', 'is_staff', 'is_superuser')
        }),
    )

    readonly_fields = ('last_login',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['user_permissions'].disabled = True
            form.base_fields['groups'].disabled = True

        if obj:
            form.base_fields['password'].help_text = (
                "Raw passwords are not stored, so there is no way to see this "
                "user's password, but you can change the password using "
                '<a href="../password/">this form</a>.'
            )
            form.base_fields['password'].widget.attrs['readonly'] = True

        return form

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} users activated")

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} users deactivated")
