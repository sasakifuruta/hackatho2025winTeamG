from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()


# サインアップ用フォーム
class SignupForm(UserCreationForm):
  email = forms.EmailField(
    required=True,
    label="登録メールアドレス",
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

    self.fields['username'].label = '名前'
    self.fields['email'].label = '登録メールアドレス'
    self.fields['password1'].label = 'パスワード'
    self.fields['password2'].label = '確認用パスワード'

    self.fields['username'].help_text = None
    self.fields['password1'].help_text = None
    self.fields['password2'].help_text = None


# ログイン用フォーム
class LoginForm(AuthenticationForm):
  username = forms.EmailField(
    max_length=100,
    label="",
    widget=forms.EmailInput(attrs={'autofocus':True, 'placeholder': 'メールアドレス'})
  )
  password = forms.CharField(
    label="",
    widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'placeholder': 'パスワード'})
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
      widget=forms.PasswordInput(attrs={
         "placeholder":"",
         "autocomplete": "new-password"
         }),
   )

   password_confirm = forms.CharField(
      required=False,
      widget=forms.PasswordInput(attrs={
         "placeholder":"",
         "autocomplete": "new-password"
        }),
   )

   email = forms.EmailField(
      required=True,
      widget=forms.EmailInput(attrs={
         "placeholder": "メールアドレス",
         "autocomplete": "email"
      }),
      error_messages={'invalid': '有効なメールアドレスを入力してください'}
   )

   class Meta:
      model = User
      fields = ['username', 'email']
      error_messages = {
            'username': {
                'unique': 'このユーザー名は既に使用されています'
            }
        }
   
   def clean_email(self):
      email = self.cleaned_data.get('email')
      if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("このメールアドレスは既に使用されています")
      return email

   def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password or password_confirm:
            if not password:
                self.add_error("password", "パスワードを入力してください")
            if not password_confirm:
                self.add_error("password_confirm", "確認用パスワードを入力してください")
            elif password != password_confirm:
                self.add_error("password_confirm", "パスワードが一致しません")

        # パスワード強度チェック
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                self.add_error('password', e.messages[0])

        # メールアドレス形式チェック（追加）
        email = cleaned_data.get('email')
        if email:
            try:
                validate_email(email)
            except ValidationError:
                self.add_error('email', '正しいメールアドレス形式で入力してください')

        return cleaned_data
        
   def save(self, commit=True):
    user = super().save(commit=False)
    password = self.cleaned_data.get('password')
    if password:
        user.set_password(password)
    if commit:
        user.save()
    return user

    


