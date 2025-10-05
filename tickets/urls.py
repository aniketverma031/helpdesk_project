# tickets/urls.py (Example)
from django.urls import path
from . import views

urlpatterns = [
    # General app views
    path('', views.tickets_list, name='tickets_list'),
    path('new/', views.ticket_new, name='ticket_new'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # Auth views
    path('login/', views.custom_login, name='custom_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('register/', views.register, name='register'),

    # NEW: Admin Role Management View
    path('roles/manage/', views.user_role_management, name='user_role_management'), 
]