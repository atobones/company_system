# Create your models here.
import os
from django.db import models
from datetime import date
from django.conf import settings 
from django.utils import timezone 
from django.contrib.auth.models import AbstractUser

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Путь до папки: BASE_DIR/drivers/Имя Фамилия
        driver_folder = os.path.join(settings.BASE_DIR, 'drivers', self.full_name)
        os.makedirs(driver_folder, exist_ok=True)

        # Создаём текстовый файл contact.txt
        contact_file = os.path.join(driver_folder, 'contact.txt')
        with open(contact_file, 'w', encoding='utf-8') as f:
            f.write(
                f"Телефон: {self.phone}\n"
                f"Email: {self.email}\n"
                f"Банк: {self.bank_account or '-'}\n"
                f"Адрес: {self.home_address or '-'}\n"
                f"Фирма: {self.company or '-'}"
            )

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

    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')  # 🔗 связь с водителем

    def save(self, *args, **kwargs):
        # Проверяем дату страховки
        if date.today() > self.insurance_expiry:
            self.color_status = 'red'
        else:
            self.color_status = 'green'

        super().save(*args, **kwargs)

        # Создаём папку с номером машины
        car_folder = os.path.join(settings.BASE_DIR, 'cars', self.registration_number)
        os.makedirs(car_folder, exist_ok=True)

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