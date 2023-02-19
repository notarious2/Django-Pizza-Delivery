from django.contrib import admin
from .models import Customer, User
from .forms import CustomUserCreation
from django.contrib.auth.admin import UserAdmin
from order.models import Order


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreation
    ordering = ("email",)
    list_display_links = ("email", "username")
    # exclude = ('username', )
    fieldsets = (
        (
            "Personal info",
            {"fields": ("email", "password", "first_name",
                        "last_name", "username")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    # add fields those needs to be visible when adding new user in admin.
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
    )


class OrderInline(admin.TabularInline):
    model = Order

    # remove permission to modify
    def has_change_permission(self, request, obj):
        return False

    # remove permission to add

    def has_add_permission(self, request, obj):
        return False


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_at",)
    inlines = [OrderInline]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(User, CustomUserAdmin)
