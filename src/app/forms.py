from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


# サインアップ用フォーム
class SignupForm(UserCreationForm):
  email = forms.EmailField(
    required=True,
    label="メールアドレス",
    widget=forms.EmailInput(attrs={'placeholder': ''})
  )

  class Meta:
    model = User
    fields = ['username', 'email', 'password1', 'password2']

  def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは既に登録されています。")
        return email
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['username'].help_text = None
    self.fields['password1'].help_text = None
    self.fields['password2'].help_text = None


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

  def clean(self):
     email = self.cleaned_data.get('username')
     password = self.cleaned_data.get('password')

     if email and password:
        try:
           user = User.objects.get(email=email)
        except User.DoesNotExist:
           raise forms.ValidationError('このメールアドレスに対応するユーザーが存在しません')

        self.user_cache = authenticate(self.request, username=user.username, password=password)
        if self.user_cache is None:
           raise forms.ValidationError(
              self.error_messages['invalid_login'],
              code='invalid_login',
              params={'username':self.username_field.verbose_name},
           )
        else:
           self.confirm_login_allowed(self.user_cache)
     return self.cleaned_data

 
# アカウント変更
# passwordが未入力の場合は更新しない。
class AccountChangeForm(forms.ModelForm):
   password = forms.CharField(
      required=False,
      widget=forms.PasswordInput(attrs={"placeholder":"新規パスワード"})
   )
   password_confirm = forms.CharField(
      required=False,
      widget=forms.PasswordInput(attrs={"placeholder":"新規パスワード"})
   )

   class Meta:
      model = User
      fields = ['username', 'email']
   
   def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            self.add_error("password_confirm", "パスワードと確認用パスワードが一致しません。")

        return cleaned_data

   def save(self, commit=True):
      user = super().save(commit=False)

      password = self.cleaned_data.get('password')
      if password:
         user.set_password(password)

      if commit:
         user.save()

      return user

    


