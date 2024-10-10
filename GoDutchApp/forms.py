# forms.py
from django import forms
from .models import UserProfile
from .models import T_Expense,T_Burden_User,T_Expense_Detail,User
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe
import locale
from django import forms

class ExpenseForm(forms.Form):
    # 他の経費関連のフィールドを追加

    def __init__(self, user, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)

        # ログインユーザのgroup_idを取得
        group_id = UserProfile.objects.get(user=user).group_id

        # 同じgroup_idのユーザを取得
        users_in_same_group = UserProfile.objects.filter(group_id=group_id)

        # チェックボックスを動的に追加
        for user_in_group in users_in_same_group:
            self.fields[f'user_{user_in_group.user.id}'] = forms.BooleanField(
                label=user_in_group.user.username,
                required=False  # 必要に応じて変更
            )
            
class ExpenseDetailForm(forms.ModelForm):
    class Meta:
        model = T_Expense_Detail
        fields = ['payment_on', 'payment_amount', 'payer', 'category', 'payee', 'payment_method', 'memo']
        widgets = {
            'payment_amount': forms.NumberInput(attrs={'placeholder': '###,###'}), 
            'payment_on': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 必須にしたいフィールドのリスト
        required_fields = ['payment_on', 'payment_amount', 'payer', 'category']

        for field_name, field in self.fields.items():
            if field_name in required_fields:
                field.required = True
                field.widget.attrs['class'] = 'required-field'  # 必須項目にスタイリングを適用

    def as_p(self):
        # as_pメソッドをオーバーライドして特定の文字列に対してスタイリングを適用
        output = super().as_p()
        styled_fields = ['payment_on', 'payment_amount', 'payer', 'category']

        for field_name in styled_fields:
            output = output.replace(f'<label for="id_{field_name}"', f'<label for="id_{field_name}" class="required-label"')

        return mark_safe(output)