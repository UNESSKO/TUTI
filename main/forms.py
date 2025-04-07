from django import forms
from .models import Menu, ContactMessage


class MenuAdminForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        published = cleaned_data.get('published')

        # Если пользователь пытается опубликовать запись
        if published:
            # Проверяем, заполнены ли все обязательные поля
            required_fields = ['name', 'description', 'price', 'image', 'barcode', 'unit', 'published']
            for field in required_fields:
                if not cleaned_data.get(field):
                    raise forms.ValidationError(f"Поле '{field}' обязательно для публикации.")

        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
