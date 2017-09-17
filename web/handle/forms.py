from django import forms
from django.core.exceptions import ValidationError

import hashlib
import re

def get_hexdigest(password):
    return hashlib.sha1(password).hexdigest()

def validate_username(username):
    pattern = re.compile('[^a-zA-Z0-9_+-@.]')
    if re.search(pattern, username):
        raise ValidationError('username must be consist of %s' % '[a-zA-Z0-9_+-@.]')

class RegisterForm(forms.Form):
    username = forms.CharField(validators=[validate_username])
    password1 = forms.CharField(min_length = 8, widget = forms.PasswordInput)
    password2 = forms.CharField(min_length = 8, widget = forms.PasswordInput)
    email = forms.EmailField()
    realname = forms.CharField()
    grade = forms.CharField()
    school = forms.CharField()

    def clean_password1(self):
        return get_hexdigest(self.cleaned_data['password1'])

    def clean_password2(self):
        return get_hexdigest(self.cleaned_data['password2'])

class ProfileForm(forms.Form):
    username = forms.CharField(validators=[validate_username])
    orginalpassword = forms.CharField(min_length = 8, widget = forms.PasswordInput)
    email = forms.EmailField()
    realname = forms.CharField(required = False)
    signature = forms.CharField(required = False)
    headurl = forms.CharField(required = False)
    school = forms.CharField(required = False)
    grade = forms.CharField(required = False)

    def clean_orginalpassword(self):
        return get_hexdigest(self.cleaned_data['orginalpassword'])

class LoginForm(forms.Form):
    username = forms.CharField(validators=[validate_username])
    password = forms.CharField(widget = forms.PasswordInput)

    def clean_password(self):
        return get_hexdigest(self.cleaned_data['password'])
