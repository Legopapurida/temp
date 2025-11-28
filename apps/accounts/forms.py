from django import forms
from django.contrib.auth.models import User
from apps.community.models import UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'discord_username', 'twitch_username', 'youtube_channel']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
        
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save Changes', css_class='btn btn-primary'))
    
    def save_user(self, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

class OTPVerificationForm(forms.Form):
    token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': 'Enter 6-digit code',
            'style': 'letter-spacing: 0.5em; font-size: 1.2em;'
        })
    )
    
    def clean_token(self):
        token = self.cleaned_data.get('token')
        if token and not token.isdigit():
            raise forms.ValidationError('Token must contain only digits.')
        return token
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Verify', css_class='btn btn-primary w-100'))