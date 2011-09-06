from django import forms

from barabasdjango.webserver import WebServer
from barabas.identity.user import User
from barabas.identity.passwordauthentication import PasswordAuthentication

class PasswordLoginForm(forms.Form):
    username = forms.CharField(max_length=32, label="Test",
                               widget=forms.TextInput(attrs={'placeholder': 'John.Doe'}))
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    
    def clean(self):
        """Empty docstring"""
        data = self.cleaned_data
        db = WebServer.database()
        pa = db.find(PasswordAuthentication, PasswordAuthentication.username == data['username']).one()
        
        if not (pa and pa.testPassword(data['password'])):
            raise forms.ValidationError("Wrong username or password")
        
        data['passwordAuthentication'] = pa
        return data

class PasswordBasedRegistrationForm(forms.Form):
    username = forms.CharField(max_length=32, label="Username",
                               widget=forms.TextInput(attrs={'placeholder': 'John.Doe'}))
    email = forms.CharField(label="E-mail",
                            widget=forms.TextInput(attrs={'placeholder': 'john.doe@example.com'}))
    firstName = forms.CharField(label="First Name",
                                widget=forms.TextInput(attrs={'placeholder': 'John'}))
    lastName = forms.CharField(label="Last Name",
                               widget=forms.TextInput(attrs={'placeholder': 'Doe'}))
    
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    passwordCheck = forms.CharField(label="Password (check)",
                                    widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    
    def clean(self):
        """Empty docstring"""
        data = self.cleaned_data
        print data['password']
        
        db = WebServer.database()
        user = User(data['firstName'], data['lastName'], data['email'])
        pa = PasswordAuthentication()
        pa.username = data['username']
        pa.password(data['password'])
        pa.user = user
        
        data['user'] = user
        data['passwordAuth'] = pa
        return data

class ProfileForm(forms.Form):
    pass
    
