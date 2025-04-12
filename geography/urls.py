"""geography URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('table/', views.countries_table, name='countries_table'),
    path('stats/', views.stats, name='stats'),
    path('add-country/', views.add_country, name='add_country'),
    path('send-country/', views.send_country, name='send_country'),
    
    path('quiz/', views.quiz_settings, name='quiz_settings'),
    path('quiz/question/', views.quiz_question, name='quiz_question'),
    path('quiz/check/', views.check_answer, name='check_answer'),
    path('quiz/skip/', views.skip_question, name='skip_question'),
    path('quiz/results/', views.quiz_results, name='quiz_results'),
]
