from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    email = forms.CharField(widget=forms.EmailInput, required=True, max_length=120, label="Е-майл: ")
    password = forms.CharField(widget=forms.PasswordInput, required=True, max_length=50, min_length=8, label="Парола", help_text="Паролата трябва да е минимум 8 символа.")
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    password = forms.CharField(max_length=50, min_length=8, label="Парола")
    
class ModeratorLoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label="Потребителско име: ", min_length=4)
    password = forms.CharField(max_length=50, min_length=8, label="Парола")
    
class BeachAddForm(forms.Form):
    image = forms.ImageField(required=True, label="Снимка: ", help_text="Изискваме снимки, за да осигурим...")
    name = forms.CharField(max_length=100, min_length=5, required=True, label="Име на плажа: ")
    description = forms.CharField(max_length=250, label="Кратко описание: ", help_text="*незадължително", widget=forms.Textarea, required=False)
    has_lifeguard = forms.BooleanField(required=False, label="Спасител: ", help_text="*незадължително")
    has_parking = forms.BooleanField(required=False, label="Паркинг: ", help_text="*незадължително")
    has_paid_parking = forms.BooleanField(required=False, label="Платен Паркинг: ", help_text="*незадължително")
    has_toilets = forms.BooleanField(required=False, label="Тоалетни: ", help_text="*незадължително")
    has_changing_rooms = forms.BooleanField(required=False, label="Съблекални: ", help_text="*незадължително")
    has_paid_zone = forms.BooleanField(required=False, label="Платена зона: ", help_text="*незадължително")
    has_beach_bar = forms.BooleanField(required=False, label="Заведения: ", help_text="*незадължително")