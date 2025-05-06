import os
import json
import mimetypes
from datetime import date, datetime
from collections import Counter
from django.conf import settings
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, Value, IntegerField
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Driver, Car, License, Report, ReportEntry
from .forms import DriverForm, CarForm, LicenseForm
from .models import ActionLog 


# Вход
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def bulk_delete_licenses(request):
    if request.method == 'POST':
        ids = request.POST.getlist('license_ids')
        License.objects.filter(id__in=ids).delete()
    return redirect('license_list')

# Главная
@login_required
def home(request):
    total_drivers = Driver.objects.count()
    total_cars = Car.objects.count()
    active_cars = Car.objects.filter(insurance_expiry__gte=date.today()).count()
    expired_cars = Car.objects.filter(insurance_expiry__lt=date.today()).count()

    cars = Car.objects.all()
    monthly_counter = Counter(car.insurance_expiry.strftime('%B %Y') for car in cars)
    sorted_items = sorted(monthly_counter.items(), key=lambda x: datetime.strptime(x[0], "%B %Y"))
    labels = [item[0] for item in sorted_items]
    data = [item[1] for item in sorted_items]
    employees = ['ATO', 'Sherali', 'Zhana']

    return render(request, 'home.html', {
        'total_drivers': total_drivers,
        'total_cars': total_cars,
        'active_cars': active_cars,
        'expired_cars': expired_cars,
        'chart_labels': labels,
        'chart_data': data,
        'employees': employees,
    })

# Водители
@login_required
def driver_list(request):
    drivers = Driver.objects.all()
    is_admin = request.user.is_authenticated and request.user.is_admin()
    return render(request, 'drivers.html', {'drivers': drivers, 'is_admin': is_admin})

@login_required
def view_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    return render(request, 'drivers/view_driver.html', {'driver': driver})

@login_required
def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save()

            # ЛОГ ДОБАВЛЕНИЯ
            ActionLog.objects.create(
                user=request.user,
                action="Добавил водителя",
                object_name=driver.full_name
            )

            return redirect('upload_driver_file', driver_id=driver.id)
    else:
        form = DriverForm()
    return render(request, 'add_driver.html', {'form': form})

@login_required
def edit_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()

            # ЛОГ ИЗМЕНЕНИЯ
            ActionLog.objects.create(
                user=request.user,
                action="Изменил водителя",
                object_name=driver.full_name
            )

            return redirect('upload_driver_file', driver_id=driver.id)
    else:
        form = DriverForm(instance=driver)
    return render(request, 'edit_driver.html', {'form': form, 'driver': driver})

@login_required
def delete_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == 'POST':

        # ЛОГ УДАЛЕНИЯ
        ActionLog.objects.create(
            user=request.user,
            action="Удалил водителя",
            object_name=driver.full_name
        )

        driver.delete()
        return redirect('driver_list')
    return render(request, 'delete_driver.html', {'driver': driver})

# Машины
@login_required
def car_list(request):
    today = date.today()
    cars = Car.objects.annotate(
        expired=Case(
            When(insurance_expiry__lt=today, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('expired', 'insurance_expiry')

    for car in cars:
        car.color_status = 'red' if car.insurance_expiry < today else 'green'

    is_admin = request.user.is_authenticated and request.user.is_admin()

    return render(request, 'cars.html', {'cars': cars, 'is_admin': is_admin})

@login_required
def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save()

            # ЛОГ ДОБАВЛЕНИЯ
            ActionLog.objects.create(
                user=request.user,
                action="Добавил машину",
                object_name=car.registration_number
            )

            return redirect('upload_car_file', car_id=car.id)
    else:
        form = CarForm()
    return render(request, 'add_car.html', {'form': form})

@login_required
def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()

            # ЛОГ ИЗМЕНЕНИЯ
            ActionLog.objects.create(
                user=request.user,
                action="Изменил машину",
                object_name=car.registration_number
            )

            return redirect('car_list')
    else:
        form = CarForm(instance=car)
    return render(request, 'edit_car.html', {'form': form, 'car': car})

@login_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':

        # ЛОГ УДАЛЕНИЯ
        ActionLog.objects.create(
            user=request.user,
            action="Удалил машину",
            object_name=car.registration_number
        )

        car.delete()
        return redirect('car_list')
    return render(request, 'delete_car.html', {'car': car})

# Связь с водителем
@login_required
def car_contact(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if not car.driver:
        return render(request, 'car_no_driver.html', {'car': car})
    return render(request, 'car_contact.html', {'car': car, 'driver': car.driver})

# Файлы
@login_required
def upload_driver_file(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    driver_folder = os.path.join(settings.BASE_DIR, 'drivers', driver.full_name)
    os.makedirs(driver_folder, exist_ok=True)

    if request.GET.get('preview'):
        file_path = os.path.join(driver_folder, request.GET['preview'])
        mime_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=mime_type)

    if request.GET.get('download'):
        file_path = os.path.join(driver_folder, request.GET['download'])
        mime_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=mime_type, as_attachment=True)

    if request.GET.get('delete'):
        os.remove(os.path.join(driver_folder, request.GET['delete']))
        return HttpResponseRedirect(request.path)

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        with open(os.path.join(driver_folder, file.name), 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
        return HttpResponseRedirect(request.path)

    files = [f for f in os.listdir(driver_folder) if f != 'contact.txt']
    return render(request, 'upload_driver_file.html', {'driver': driver, 'files': files})

@login_required
def upload_car_file(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    car_folder = os.path.join(settings.BASE_DIR, 'cars', car.registration_number)
    os.makedirs(car_folder, exist_ok=True)

    if request.GET.get('preview'):
        file_path = os.path.join(car_folder, request.GET['preview'])
        mime_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=mime_type)

    if request.GET.get('download'):
        file_path = os.path.join(car_folder, request.GET['download'])
        mime_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=mime_type, as_attachment=True)

    if request.GET.get('delete'):
        os.remove(os.path.join(car_folder, request.GET['delete']))
        return HttpResponseRedirect(request.path)

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        with open(os.path.join(car_folder, file.name), 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
        return HttpResponseRedirect(request.path)

    files = os.listdir(car_folder)
    return render(request, 'upload_car_file.html', {'car': car, 'files': files})


# Отчёты
@login_required
def create_report(request, employee):
    if request.method == "POST":
        report_date = request.POST.get("date")
        car_numbers = request.POST.getlist("car_number[]")
        comments = request.POST.getlist("comment[]")
        statuses = request.POST.getlist("status[]")

        entries = []
        for number, comment, status in zip(car_numbers, comments, statuses):
            entries.append({
                "car_number": number,
                "comment": comment,
                "status": status
            })

        folder = os.path.join(settings.BASE_DIR, "reports", employee)
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, f"{report_date}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

        return redirect("report_list", employee=employee)

    return render(request, "reports/create.html", {
        "employee": employee,
        "today": date.today().isoformat()
    })


@login_required
def report_list(request, employee):
    folder = os.path.join(settings.BASE_DIR, 'reports', employee)
    if not os.path.exists(folder):
        reports = []
    else:
        reports = [f[:-5] for f in os.listdir(folder) if f.endswith('.json')]
        reports.sort(reverse=True)

    return render(request, 'reports/list.html', {
        'employee': employee,
        'reports': reports
    })

@login_required
def view_report(request, employee, date):
    path = os.path.join(settings.BASE_DIR, 'reports', employee, f"{date}.json")
    if not os.path.exists(path):
        return render(request, 'reports/view_report.html', {
            'employee': employee,
            'date': date,
            'entries': []
        })
    with open(path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    return render(request, 'reports/view_report.html', {
        'employee': employee,
        'date': date,
        'entries': entries
    })

@login_required
def delete_report(request, employee, date):
    filepath = os.path.join(settings.BASE_DIR, 'reports', employee, f"{date}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect('report_list', employee=employee)

@login_required
def report_detail(request, employee, report_id):
    report = get_object_or_404(Report, id=report_id, employee=employee)
    if request.method == 'POST':
        car_number = request.POST.get('car_number')
        comment = request.POST.get('comment')
        status = request.POST.get('status')
        if car_number and status:
            ReportEntry.objects.create(report=report, car_number=car_number, comment=comment, status=status)
            return redirect('report_detail', employee=employee, report_id=report.id)
    return render(request, 'reports/detail.html', {'report': report})


@login_required
def report_home(request):
    employees = ['ATO', 'Sherali', 'Zhana']
    return render(request, 'reports/home.html', {'employees': employees})


#license

@login_required
def license_list(request):
    licenses = License.objects.all().order_by('-created_at')
    is_admin = request.user.is_authenticated and request.user.is_admin()
    
    return render(request, 'license.html', {
        'licenses': licenses,
        'is_admin': is_admin,
    })

@login_required
def add_license(request):
    if not (request.user.is_authenticated and request.user.is_admin()):
        return redirect('license_list')

    if request.method == 'POST':
        form = LicenseForm(request.POST, request.FILES)
        if form.is_valid():
            license = form.save()

            # ЛОГ ДОБАВЛЕНИЯ
            ActionLog.objects.create(
                user=request.user,
                action="Добавил лицензию",
                object_name=str(license.registration_number)
            )

            return redirect('license_list')
    else:
        form = LicenseForm()

    return render(request, 'add_license.html', {'form': form})

@login_required
def bulk_delete_licenses(request):
    if request.method == 'POST':
        ids = request.POST.getlist('license_ids')
        licenses = License.objects.filter(id__in=ids)
        for lic in licenses:
            ActionLog.objects.create(
                user=request.user,
                action="Удалил лицензию",
                object_name=str(lic.registration_number)
            )
        licenses.delete()
    return redirect('license_list')


def log_action(user, action, model_name, object_id, description=''):
    ActionLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
    )