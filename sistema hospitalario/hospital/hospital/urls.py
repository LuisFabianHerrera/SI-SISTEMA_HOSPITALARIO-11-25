"""
URL configuration for hospital project.

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
from django.urls import path, include
from gestion_administrativa.views import login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login y Logout desde la raíz
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Apps con prefijo
    path('administracion/', include('gestion_administrativa.urls')),
    path('std/', include('gestion_STD.urls')),
    path('financiera/', include('gestion_financiera.urls')),
    path('pacientes/', include('gestion_pacientes.urls')),
]
