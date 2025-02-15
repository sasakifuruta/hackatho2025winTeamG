from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

# ユーザーモデル取得
User = get_user_model()

# ログイン用フォーム
class LoginForm(AuthenticationForm):
  username = forms.EmailField(
    max_length=100,
    label="メールアドレス",
    widget=forms.EmailInput(attrs={'autofocus':True})
  )
  password = forms.CharField(
    label="パスワード",
    widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
  )

  error_messages = {
    'invalid_login': '無効なメールアドレスまたはパスワードです。',
    'invalid_login':'このアカウントは現在無効です。',
  }

  def clean_username(self):
    username = self.cleaned_data.get('username')
    if not username.endswith('@example.com'):
      raise forms.ValidationError("メールアドレスは@example.comでなければなりません")
    return user.username