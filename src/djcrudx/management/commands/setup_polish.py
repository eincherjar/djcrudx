from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Automatycznie konfiguruje DjCrudX dla języka polskiego'

    def handle(self, *args, **options):
        if getattr(settings, 'LANGUAGE_CODE', 'en') == 'pl':
            self.stdout.write(self.style.SUCCESS('✓ LANGUAGE_CODE już ustawiony na "pl"'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Ustaw LANGUAGE_CODE = "pl" w settings.py'))

        if 'djcrudx' in settings.INSTALLED_APPS:
            self.stdout.write(self.style.SUCCESS('✓ djcrudx jest w INSTALLED_APPS'))
        else:
            self.stdout.write(self.style.ERROR('✗ Dodaj "djcrudx" do INSTALLED_APPS'))

        self.stdout.write(self.style.SUCCESS('\n🎉 DjCrudX automatycznie wykryje język polski!'))
        self.stdout.write('Nie musisz uruchamiać makemessages ani compilemessages.')
        self.stdout.write('Biblioteka ma wbudowane tłumaczenia.')