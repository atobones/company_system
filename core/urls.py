from django.urls import path
from .views import (
    home, login_view,
    driver_list, add_driver, edit_driver, delete_driver, upload_driver_file, view_driver,
    car_list, add_car, edit_car, delete_car, upload_car_file, car_contact,
    report_home, report_list, create_report, view_report, delete_report, report_detail, 
    logout_view, 
    # Лицензии
    license_list, add_license, bulk_delete_licenses
)

urlpatterns = [
    path('licenses/delete-multiple/', bulk_delete_licenses, name='bulk_delete_licenses'),

    # Аутентификация
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Главная страница
    path('', home, name='home'),

    # Водители
    path('drivers/', driver_list, name='driver_list'),
    path('drivers/add/', add_driver, name='add_driver'),
    path('drivers/<int:driver_id>/edit/', edit_driver, name='edit_driver'),
    path('drivers/<int:driver_id>/delete/', delete_driver, name='delete_driver'),
    path('drivers/<int:driver_id>/files/', upload_driver_file, name='upload_driver_file'),
    path('drivers/<int:driver_id>/view/', view_driver, name='view_driver'),

    # Машины
    path('cars/', car_list, name='car_list'),
    path('cars/add/', add_car, name='add_car'),
    path('cars/<int:car_id>/edit/', edit_car, name='edit_car'),
    path('cars/<int:car_id>/delete/', delete_car, name='delete_car'),
    path('cars/<int:car_id>/files/', upload_car_file, name='upload_car_file'),
    path('cars/<int:car_id>/contact/', car_contact, name='car_contact'),

    # Лицензии
    path('licenses/', license_list, name='license_list'),
    path('licenses/add/', add_license, name='add_license'),

    # Отчёты
    path('reports/', report_home, name='report_home'),
    path('reports/<str:employee>/', report_list, name='report_list'),
    path('reports/<str:employee>/create/', create_report, name='create_report'),
    path('reports/<str:employee>/<str:date>/', view_report, name='view_report'),
    path('reports/<str:employee>/<str:date>/delete/', delete_report, name='delete_report'),
    path('reports/<str:employee>/<int:report_id>/', report_detail, name='report_detail'),
]

