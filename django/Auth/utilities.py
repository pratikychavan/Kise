from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

def generate_password_reset_link(user):
    token_generator = PasswordResetTokenGenerator()
    uidb64 = urlsafe_base64_encode(force_bytes(user.id))
    token = token_generator.make_token(user)
    reset_link = f"https://0.0.0.0:5000/auth/password-reset-confirm/?uidb64={uidb64}&token={token}"    
    return reset_link

def send_password_reset_email(user):
    reset_link = generate_password_reset_link(user)
    message = f"""
Password Reset Request

Hi {user.username},

    You have requested to reset your password. Click the link below to reset your password:

    {reset_link}
    
    If you didn't request this, please ignore this email.
"""
    from_email = 'pchavan1996@gmail.com'  # Replace with your email
    to_email = user.email
    send_mail("Password Reset Request", message, from_email, [to_email])
    return message


# In your views, after generating the reset token, you can call this function:
# send_password_reset_email(user, token)
