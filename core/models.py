import os
from django.db import models
from datetime import date
from django.conf import settings 
from django.utils import timezone 
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

class Driver(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    bank_account = models.CharField(max_length=50, blank=True, null=True)
    home_address = models.CharField(max_length=255, blank=True, null=True)

    COMPANY_CHOICES = [
        ('Jarahim', 'Jarahim'),
        ('Jarazak', 'Jarazak'),
        ('Szam', 'Szam'),
        ('Lulu', 'Lulu'),
        ('Sahar', 'Sahar'),
        ('Zoja', 'Zoja'),
    ]
    company = models.CharField(
        max_length=20,
        choices=COMPANY_CHOICES,
        blank=True,
        null=True
    )

    file = models.FileField(upload_to='drivers/', blank=True, null=True)

    def __str__(self):
        return self.full_name



class Car(models.Model):
    registration_number = models.CharField(max_length=20, unique=True)
    insurance_expiry = models.DateField()
    color_status = models.CharField(
        max_length=10,
        choices=[('green', 'Зелёный'), ('red', 'Красный')],
        default='green'
    )

    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')

    file = models.FileField(upload_to='cars/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if date.today() > self.insurance_expiry:
            self.color_status = 'red'
        else:
            self.color_status = 'green'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.registration_number

    
    
class License(models.Model):
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)
    registration_number = models.CharField(max_length=20)
    file = models.FileField(upload_to='licenses/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"License: {self.registration_number}"

class Report(models.Model):
    EMPLOYEE_CHOICES = [
        ('ATO', 'ATO'),
        ('Sherali', 'Sherali'),
        ('Zhana', 'Zhana'),
    ]

    employee = models.CharField(max_length=50, choices=EMPLOYEE_CHOICES)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.employee} - {self.date}"


class ReportEntry(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Ожидание'),
        ('rejected', 'Не приняли'),
        ('done', 'Готово'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='entries')
    car_number = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.car_number} — {self.status}"
    


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Админ'),
        ('manager', 'Менеджер'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='manager')

    def is_admin(self):
        return self.role == 'admin'

    def is_manager(self):
        return self.role == 'manager'

    def save(self, *args, **kwargs):
        # Если суперпользователь, автоматически ставим роль admin
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)


User = get_user_model()

class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Добавил'),
        ('update', 'Изменил'),
        ('delete', 'Удалил'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=50)
    object_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.object_type} (ID {self.object_id})"