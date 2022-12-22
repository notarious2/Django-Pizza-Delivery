from django import forms


class CouponApplyForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-3/5 m-2 rounded focus:ring-0 focus:border-[#c0c0c0] bg-green-100',
        'placeholder': 'Enter Promo Code'
    }))
