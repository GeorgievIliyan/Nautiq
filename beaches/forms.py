from django import forms
from . import models

#* ====== AUTHENTICATION FORMS ===== *#
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    email = forms.CharField(widget=forms.EmailInput, required=True, max_length=120, label="Е-майл: ")
    password = forms.CharField(widget=forms.PasswordInput, required=True, max_length=50, min_length=8, label="Парола", help_text="Паролата трябва да е минимум 8 символа.")
    
class UserPreferencesForm(forms.Form):
    nickname = forms.CharField(max_length=50, required=True, label="Наименование: ", min_length=4, help_text='С това наименование другите ще виждат вашата активност.')
    lat = forms.DecimalField(max_digits=9, decimal_places=6, label="Географска ширина: ", required=False, help_text="Въведете кординатите за центриране на картата.")
    lng = forms.DecimalField(max_digits=9, decimal_places=6, label="Географска дължина: ", required=False, help_text="Въведете кординатите за центриране на картата.")
    
class LoginForm(forms.Form):
    email = forms.CharField(max_length=100, required=True, label="Емайл: ", min_length=1, widget=forms.EmailInput)
    password = forms.CharField(max_length=50, min_length=8, label="Парола: ", widget=forms.PasswordInput)
    
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=100, label="Стара парола: ", widget=forms.PasswordInput)
    new_password = forms.CharField(max_length=100, min_length=8, label="Нова парола: ", widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100, label="Повтори новата парола: ", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Новата парола и потвърждението ѝ не съвпадат!")

        return cleaned_data
    
class SetPasswordForm(forms.Form):
    new_password = forms.CharField(max_length=100, min_length=8, label="Нова парола", widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100, label="Повтори новата парола", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Новата парола и потвърждението ѝ не съвпадат!")

        return cleaned_data    
    
#* ===== BEACH FORMS ===== *#
class BeachAddForm(forms.Form):
    latitude = forms.DecimalField(
        max_digits=20,
        decimal_places=18,
        label="Latitude",
        widget=forms.TextInput(
            attrs={"readonly": "readonly", "class": "form-control"}
        )
    )
    longitude = forms.DecimalField(
        max_digits=20,
        decimal_places=18,
        label="Longitude",
        widget=forms.TextInput(
            attrs={"readonly": "readonly", "class": "form-control"}
        )
    )
    image = forms.ImageField(
        required=True,
        label="Снимка:",
        help_text="Моля, добавете снимки, за да докажете..."
    )
    name = forms.CharField(
        max_length=100,
        min_length=5,
        required=True,
        label="Име на плажа:"
    )
    description = forms.CharField(
        max_length=250,
        label="Кратко описание:",
        required=False,
        widget=forms.Textarea
    )
    has_lifeguard = forms.BooleanField(required=False, label="Спасител:")
    has_parking = forms.BooleanField(required=False, label="Паркинг:")
    has_paid_parking = forms.BooleanField(required=False, label="Платен паркинг:")
    has_toilets = forms.BooleanField(required=False, label="Тоалетни:")
    has_changing_rooms = forms.BooleanField(required=False, label="Съблекални:")
    has_paid_zone = forms.BooleanField(required=False, label="Платена зона:")
    has_beach_bar = forms.BooleanField(required=False, label="Заведения:")
    
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