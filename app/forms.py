from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

# ユーザーモデル取得
User = get_user_model()

# サインアップ用フォーム
class SignupForm(UserCreationForm):
  email = forms.EmailField(
    required=True,
    label="メールアドレス",
    widget=forms.EmailInput(attrs={'placeholder': ''})
  )

  class Meta:
    model = get_user_model()
    fields = ['username', 'email', 'password1', 'password2']

  def clean(self):
    cleaned_data = super().clean()
    return cleaned_data
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['username'].help_text = None
    self.fields['password1'].help_text = None
    self.fields['password2'].help_text = None

# login画面に戻るボタンの処理を実装

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
  }

  def clean_username(self):
    username = self.cleaned_data.get('username')
    # if not username.endswith('@example.com'):
    #   raise forms.ValidationError("メールアドレスは@example.comでなければなりません")
  
    try:
      user = User.objects.get(email=username)
    except User.DoesNotExist:
      raise forms.ValidationError("このメールアドレスに対応するユーザーが存在しません")
  
    return username


# 新規登録画面への遷移ボタンを実装

# update_profileの処理を実装