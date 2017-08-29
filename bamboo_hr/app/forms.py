from django import forms

class ApiKeyForm(forms.Form):
    api_key = forms.CharField(label='Your API Key', max_length=200)