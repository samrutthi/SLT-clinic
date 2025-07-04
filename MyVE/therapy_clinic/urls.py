"""
URL configuration for therapy_clinic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('',views.home,name='home'),
    path('login/',views.login_view,name='login'),
    
    path('receptionist_dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('therapist_dashboard/', views.therapist_dashboard, name='therapist_dashboard'),
    path('clinical_supervisor_dashboard/', views.clinical_supervisor_dashboard, name='clinical_supervisor_dashboard'),
    path('case_supervisor_dashboard/', views.case_supervisor_dashboard, name='case_supervisor_dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
