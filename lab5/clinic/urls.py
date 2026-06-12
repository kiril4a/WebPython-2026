from django.urls import path
from clinic import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.custom_login, name='login'),
    path('demo-login/<str:username>/', views.demo_login, name='demo_login'),
    path('logout/', views.custom_logout, name='logout'),
    path('confirm_appointment/<int:pk>/', views.confirm_appointment, name='confirm_appointment'),
]
