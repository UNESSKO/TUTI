from django.db import models


class Menu(models.Model):
    name = models.CharField(unique=True, max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание", null=True)
    price = models.DecimalField(blank=True, max_digits=10, decimal_places=2, verbose_name="Цена", null=True)
    image = models.ImageField(blank=True, upload_to='products/', verbose_name="Изображение")
    barcode = models.IntegerField(blank=True, unique=True, verbose_name="Штриховый код", null=True)
    unit = models.CharField(blank=True, max_length=50, default="kg", verbose_name="Мера массы")
    published = models.BooleanField(default=False, verbose_name="Опубликовано")

    def __str__(self):
        return self.name

    def is_complete(self):
        # Проверяем, заполнены ли все обязательные поля для публикации
        required_fields = ['name', 'price', 'barcode', 'unit']
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True

    class Meta:
        verbose_name = "Десерт"
        verbose_name_plural = "Десерты"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"