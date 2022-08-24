from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class IiqaForm(ModelForm):
    class Meta:
        model = Iiqa
        fields = "__all__"
        exclude = ['user', 'status']


class SsrTextVerifyForm(ModelForm):
    class Meta:
        model = Ssr_Text_Converter
        fields = "__all__"
        exclude = ['user', 'status']


class SsrGeoForm(ModelForm):
    class Meta:
        model = Ssr_Geo_Tag
        fields = "__all__"
        exclude = ['user', 'status', 'latitude',
                   'longitude', 'lat_convert',
                   'long_convert']
