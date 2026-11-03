from django.urls import path
from django.http import HttpResponse

app_name = 'accounts'

urlpatterns = [
    path('login/', lambda r: HttpResponse('Страница входа (заглушка)'), name='login'),
    path('logout/', lambda r: HttpResponse('Выход (заглушка)'), name='logout'),
    path('register/', lambda r: HttpResponse('Регистрация (заглушка)'), name='register'),
]
