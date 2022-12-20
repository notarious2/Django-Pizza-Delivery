from django import forms

class CouponApplyForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs= {
        'class': 'w-3/5 m-2 rounded focus:ring-0 focus:border-[#c0c0c0] bg-green-100',
        'placeholder': 'Enter Promo Code'
    }))


class AddressForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    address_1 = forms.CharField()
    address_2 = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    country = forms.CharField()
    postal_code = forms.CharField()
    phone = forms.CharField()