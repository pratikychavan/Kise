from django.urls import path
from Auth import views

urlpatterns = [
    path("register", views.Register.as_view(), name="execute-job"),
    path("reset-password", views.PasswordReset.as_view(), name="list-jobs"),
    path("password-reset-confirm", views.PasswordResetConfirm.as_view(), name="password-reset-confirmation"),
    path("login", views.Login.as_view(), name="delete-job")
]