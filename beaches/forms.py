from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    email = forms.CharField(widget=forms.EmailInput, required=True, max_length=120, label="Е-майл: ")
    password = forms.CharField(widget=forms.PasswordInput, required=True, max_length=50, min_length=8, label="Парола", help_text="Паролата трябва да е минимум 8 символа.")
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    password = forms.CharField(max_length=50, min_length=8, label="Парола")