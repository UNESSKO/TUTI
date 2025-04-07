from django.shortcuts import render, redirect
from .forms import ContactForm
from .models import Menu
from django.contrib import messages
from django.core.paginator import Paginator


def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Спасибо за сообщение! Мы свяжемся с вами в ближайшее время')
            return redirect('home')
    else:
        form = ContactForm()

    menu = Menu.objects.filter(published=True)

    # Пагинатор
    paginator = Paginator(menu, 3)
    page_number = request.GET.get('page')  # Получаем номер текущей страницы из запроса
    page_obj = paginator.get_page(page_number)  # Получаем объект страницы

    return render(request, 'main/site.html', {'form': form, 'page_obj': page_obj})

