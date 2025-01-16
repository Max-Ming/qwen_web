from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True, help_text="必填，最多 150 个字符")
    password1 = forms.CharField(widget=forms.PasswordInput, help_text="必填，至少 8 个字符")
    password2 = forms.CharField(widget=forms.PasswordInput, help_text="确认密码")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        # 检查密码是否一致
        if password1 != password2:
            raise ValidationError("两次输入的密码不一致")
        return password2