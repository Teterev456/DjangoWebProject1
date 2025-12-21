import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoWebProject1.settings')

django.setup()

from django.contrib.auth.models import Group

if __name__ == '__main__':
    managers_group, created = Group.objects.get_or_create(name='Managers')
    
    if created:
        print("\033[92m✅ Группа 'Managers' успешно создана\033[0m")
    else:
        print("\033[94mℹ️ Группа 'Managers' уже существует\033[0m")