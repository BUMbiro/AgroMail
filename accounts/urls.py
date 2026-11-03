from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),  # <-- НОВОЕ
    path('verify-email/sent/', views.EmailVerificationSentView.as_view(), name='email_verification_sent'),
    path('verify-email/<int:pk>/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
]
