from django.db import migrations

def migrate_categories(apps, schema_editor):
    CardsProduct = apps.get_model('app', 'CardsProduct')
    Category = apps.get_model('app', 'Category')
    
    # Отображение старых значений на slug
    mapping = {
        'photo_sessions': 'photo_sessions',
        'printed_products': 'printed_products',
        'service_packages': 'service_packages',
    }
    
    for product in CardsProduct.objects.all():
        old_value = product.category
        if old_value in mapping:
            try:
                cat = Category.objects.get(slug=mapping[old_value])
                product.category_fk = cat
                product.save()
            except Category.DoesNotExist:
                print(f"Категория не найдена для: {old_value}")
        else:
            print(f"Неизвестное значение категории: {old_value}")

def reverse_migrate(apps, schema_editor):
    # Обратная операция — не обязательна, но можно оставить пустой
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0026_auto_20251223_1932'),  
    ]

    operations = [
        migrations.RunPython(migrate_categories, reverse_migrate),
    ]