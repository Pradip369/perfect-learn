from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationForm(UserCreationForm):
    
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder' : "Enter Username",'autofocus' : True}),)
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control','placeholder' : "Enter Email Id"}),)
    phone_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder' : "Enter Mobile no.",'type' : "number"}),)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs = {'class' : 'form-control','placeholder' : "Enter Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs = {'class' : 'form-control','placeholder' : 'Confirm password'}))
    
    class Meta:
        model = User
        fields = ['username','email','phone_no','password1','password2']
        help_texts = {
            "username":None,
        }
        
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder' : "Enter Username or Email Id",'autofocus' : True}),)
    password = forms.CharField(widget=forms.PasswordInput(attrs = {'class' : 'form-control','placeholder' : "Enter Password"}))

class UserProfileForm(UserChangeForm):
    password = None
    class Meta:
        model = User
        fields = ["username","first_name","last_name","phone_no","email"]
        labels = {'email':'Email'}  