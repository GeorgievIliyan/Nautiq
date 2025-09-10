from django import forms
from . import models

#* ====== AUTHENTICATION FORMS ===== *#
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    email = forms.CharField(widget=forms.EmailInput, required=True, max_length=120, label="Е-майл: ")
    password = forms.CharField(widget=forms.PasswordInput, required=True, max_length=50, min_length=8, label="Парола", help_text="Паролата трябва да е минимум 8 символа.")
    nickname = forms.CharField(max_length=50, required=True, label="Наименование: ", min_length=4, help_text='С това наименование другите ще виждат вашата активност.')
    lat = forms.DecimalField(max_digits=9, decimal_places=6, label="Географска ширина: ", required=False, help_text="Въведете кординатите за центриране на картата.")
    lng = forms.DecimalField(max_digits=9, decimal_places=6, label="Географска дължина: ", required=False, help_text="Въведете кординатите за центриране на картата.")
    
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
    category = forms.ChoiceField(
        choices=REPORT_CHOICES,
        required=True,
        label="Изберете категория за доклада: "
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        label="Описание на проблема: ",
        help_text="*незадължително",
        widget=forms.Textarea(attrs={'rows': 4})
    )

#* ===== BEACH LOGGING ===== *#
class LogBeachForm(forms.Form):
    image = forms.ImageField(required=True, label="Снимка")
    
    # Conditions
    crowd_level = forms.ChoiceField(
        choices=models.BeachLog.CROWD_LEVEL_CHOICES,
        required=True,
        label="Количество хора: "
    )
    
    water_clarity = forms.ChoiceField(
        choices=models.BeachLog.WATER_CLARITY_CHOICES,
        required=True,
        label="Ниво на чистотата на водата: "
    )
    
    water_temp = forms.ChoiceField(
        choices= models.BeachLog.WATER_TEMPERATURE_CHOICES,
        required=True,
        label='Температура на водата: '
    )
    
    weather = forms.ChoiceField(
        choices=models.BeachLog.WEATHER_CONDITION_CHOICES,
        required=True,
        label="Време: "
    )
    
    algae = forms.ChoiceField(
        choices=models.BeachLog.ALGAE_VOLUME_CHOICES,
        required=True,
        label="Водорасли: ",
    )
    
    parking_space = forms.ChoiceField(
        required=True,
        label="Място за паркиране: ",
        choices=models.BeachLog.PARKING_SPACE_CHOICES
    )
    
    waves = forms.ChoiceField(
        required=True,
        label="ВЪлни: ",
        choices=models.BeachLog.WAVE_CHOICES
    )
    
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Бележка: ',
        help_text="*незадължително",
        required=False,
        max_length=300
    )