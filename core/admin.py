from django.contrib import admin
from .models import Car, Driver, License, Report, ReportEntry, CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)

# И зарегистрировать остальные модели, если надо:
admin.site.register(Car)
admin.site.register(Driver)
admin.site.register(License)
admin.site.register(Report)
admin.site.register(ReportEntry)
