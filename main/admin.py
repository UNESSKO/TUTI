from django.contrib import admin
from .models import Menu, ContactMessage
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
import json
from django.http import HttpResponseRedirect
from .forms import MenuAdminForm


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    readonly_fields = ['name', 'email', 'phone', 'message', 'created_at']


class JsonUploadForm(forms.Form):
    json_file = forms.FileField()


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    form = MenuAdminForm  # Кастомная форма
    list_display = ('name', 'price', 'unit', 'published')
    list_editable = ()
    fields = ('name', 'description', 'price', 'image', 'barcode', 'unit', 'published')
    change_list_template = 'admin/menu_change_list.html'  # Кастомный шаблон
    search_fields = ['name']  # Поиск по полю name
    list_filter = ['published']  # Фильтр по полю published

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-json/', self.upload_json, name='upload_json'),
        ]
        return custom_urls + urls

    def upload_json(self, request):
        if request.method == 'POST':
            form = JsonUploadForm(request.POST, request.FILES)
            if form.is_valid():
                json_file = request.FILES['json_file']
                try:
                    data = json.load(json_file)
                    duplicates = self.process_json(data)
                    if duplicates:
                        self.message_user(request, f"Обнаружены дубликаты: {', '.join(duplicates)}", level=messages.ERROR)
                    else:
                        self.message_user(request, "Данные успешно загружены!", level=messages.SUCCESS)
                except json.JSONDecodeError:
                    self.message_user(request, "Ошибка: Неверный формат JSON-файла.", level=messages.ERROR)
                except Exception as e:
                    self.message_user(request, f"Ошибка: {str(e)}", level=messages.ERROR)
                return redirect('..')
        else:
            form = JsonUploadForm()

        context = {
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/upload_json.html', context)

    def process_json(self, data):
        duplicates = []
        names_in_json = set()

        # Проверка на дубликаты в JSON
        for item in data:
            name = item.get('name')
            if name in names_in_json:
                duplicates.append(name)
            names_in_json.add(name)

        if duplicates:
            return duplicates

        # Обновление или добавление данных
        for item in data:
            name = item.get('name')
            price = item.get('price')
            barcode = item.get('barcode')
            unit = item.get('unit')

            # Получаем существующую запись или создаем новую
            menu_item, created = Menu.objects.get_or_create(
                name=name,
                defaults={
                    'price': price,
                    'barcode': barcode,
                    'unit': unit,
                    'published': False,  # Для новой записи published=False
                }
            )

            # Если запись уже существует, обновляем только price, barcode и unit
            if not created:
                menu_item.price = price
                menu_item.barcode = barcode
                menu_item.unit = unit
                menu_item.save()

        return None

    def get_readonly_fields(self, request, obj=None):
        # Делаем поле published доступным только для чтения, если не все поля заполнены
        if obj and not obj.is_complete():
            return ('published',)
        return ()

    def save_model(self, request, obj, form, change):
        # Сохраняем запись, даже если не все поля заполнены
        super().save_model(request, obj, form, change)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        # Добавляем контекст для отображения предупреждения
        extra_context = extra_context or {}
        if object_id:
            obj = self.get_object(request, object_id)
            if obj and not obj.is_complete():
                extra_context['show_warning'] = True
        return super().changeform_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        if "_publish" in request.POST:
            if obj.is_complete():
                obj.published = True
                obj.save()
                self.message_user(request, "Запись успешно опубликована.")
            else:
                self.message_user(request, "Не все обязательные поля заполнены. Запись не может быть опубликована.", level=messages.ERROR)
            return HttpResponseRedirect(reverse('admin:main_menu_changelist'))
        return super().response_change(request, obj)

    # def is_complete(self, obj):
    #     # Проверяем, заполнены ли все обязательные поля
    #     required_fields = ['name', 'price', 'barcode', 'unit']
    #     for field in required_fields:
    #         if not getattr(obj, field):
    #             return False
    #     return True


