from django import forms
from . import models

#* ====== AUTHENTICATION FORMS ===== *#
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    email = forms.CharField(widget=forms.EmailInput, required=True, max_length=120, label="Е-майл: ")
    password = forms.CharField(widget=forms.PasswordInput, required=True, max_length=50, min_length=8, label="Парола", help_text="Паролата трябва да е минимум 8 символа.")
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    password = forms.CharField(max_length=50, min_length=8, label="Парола")
    
class BeachEditForm(forms.ModelForm):
    class Meta:
        model = models.Beach
        fields = '__all__'

    image = forms.ImageField(required=False, label="Снимка: ", help_text="Променете снимката")
    
    description = forms.CharField(
        max_length=250,
        label="Кратко описание:",
        help_text="*незадължително",
        widget=forms.Textarea,
        required=False
    )

#* ===== BEACH REPORTING ===== *#
class ReportBeachForm(forms.Form):
    REPORT_CHOICES = models.BeachReport.REPORT_CATEGORIES
    title = forms.CharField(max_length=60, required=True, label="Заглавие на доклада: ")
    description = forms.CharField(max_length=500, required=False, label="Описание на проблема: ", help_text="*незадължително")
    category = forms.ChoiceField(choices=REPORT_CHOICES, required=True, label="Изберете категория за доклада: ")

#* ===== BEACH LOGGING ===== *#
class LogBeachForm(forms.Form):
    image = forms.ImageField(required=True, label="Снимка")
