from tkinter import N
from django.urls import path
from .views import employee_api, employee_api_pk, team_api, team_api_pk, team_employee_api, financials_api

urlpatterns = [
    path('employee/', employee_api, name='employee-api'),
    path('employee/<str:pk>', employee_api_pk, name='employee-api-pk'),
    path('team/', team_api, name='team-api'),
    path('team/<str:pk>', team_api_pk, name='team-api-pk'),
    path('team-employee-relation', team_employee_api, name='team-employee-api'),
    path('financials/', financials_api, name='financials-api'),
]