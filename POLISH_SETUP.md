# Konfiguracja DjCrudX dla projektów w języku polskim

## 1. Instalacja

```bash
pip install git+https://github.com/twoj-username/djcrudx.git
```

## 2. Ustawienia Django (settings.py)

```python
INSTALLED_APPS = [
    # ...
    'djcrudx',
    # ...
]

# Język polski - WYSTARCZY TO!
LANGUAGE_CODE = 'pl'
```

## 3. Gotowe! 🎉

Biblioteka automatycznie wyświetli polskie tłumaczenia.
**NIE MUSISZ robić makemessages!**

## 4. Opcjonalne dostosowania

### Własne tłumaczenia (bez makemessages)
```python
# settings.py
DJCRUDX_TRANSLATIONS = {
    'pl': {
        'Create': 'Dodaj nowy',
        'Edit': 'Modyfikuj',
    }
}
```

### Pełne Django i18n (tylko jeśli potrzebujesz)
```python
# settings.py
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

```bash
python manage.py makemessages -l pl
python manage.py compilemessages
```

## 4. Przykład użycia w polskim projekcie

```python
# models.py
class Produkt(models.Model):
    nazwa = models.CharField(max_length=100)
    cena = models.DecimalField(max_digits=10, decimal_places=2)
    kategoria = models.ForeignKey('Kategoria', on_delete=models.CASCADE)
    aktywny = models.BooleanField(default=True)
    utworzony = models.DateTimeField(auto_now_add=True)

# forms.py
from djcrudx.widgets import MultiSelectDropdownWidget, ColoredSelectDropdownWidget

class ProduktForm(forms.ModelForm):
    class Meta:
        model = Produkt
        fields = '__all__'
        widgets = {
            'kategoria': ColoredSelectDropdownWidget(),
            'aktywny': ActiveStatusDropdownWidget(),
        }

# views.py
from djcrudx import create_crud

TABLE_CONFIG = [
    {
        "label": "Nazwa",
        "field": "nazwa",
        "value": lambda obj: obj.nazwa,
        "url": lambda obj: ("produkty:edit", {"pk": obj.pk}),
    },
    {
        "label": "Cena",
        "field": "cena",
        "value": lambda obj: f"{obj.cena} zł",
    },
    {
        "label": "Status",
        "field": "aktywny",
        "is_badge": True,
        "badge_data": lambda obj: [{
            "name": "Aktywny" if obj.aktywny else "Nieaktywny",
            "background_color": "green-100" if obj.aktywny else "red-100",
            "text_color": "green-800" if obj.aktywny else "red-800"
        }],
    },
]

FORM_SECTIONS = [
    {
        "title": "Podstawowe informacje",
        "columns": 2,
        "fields": ["nazwa", "cena", "kategoria", "aktywny"]
    }
]

crud = create_crud(Produkt, ProduktForm, ProduktFilter)

produkt_lista = crud['list'](
    TABLE_CONFIG,
    page_title="Lista produktów",
    create_url="produkty:create"
)

produkt_dodaj = crud['create'](
    FORM_SECTIONS,
    page_title="Dodaj produkt"
)
```

## 5. URLs

```python
# urls.py
urlpatterns = [
    path('produkty/', produkt_lista, name='lista'),
    path('produkty/dodaj/', produkt_dodaj, name='create'),
    path('produkty/<int:pk>/edytuj/', produkt_edytuj, name='edit'),
    path('produkty/<int:pk>/', produkt_szczegoly, name='detail'),
    path('produkty/<int:pk>/usun/', produkt_usun, name='delete'),
]
```

## 6. Własne tłumaczenia

Utwórz plik `locale/pl/LC_MESSAGES/django.po` w swojej aplikacji:

```po
msgid "Create"
msgstr "Utwórz"

msgid "Edit"
msgstr "Edytuj"

msgid "Delete"
msgstr "Usuń"

msgid "Save"
msgstr "Zapisz"

msgid "Cancel"
msgstr "Anuluj"
```

## 7. Nadpisywanie szablonów (opcjonalne)

Utwórz `templates/crud/base.html` w swoim projekcie, żeby dostosować wygląd:

```html
{% load i18n %}
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE|default:'pl' }}">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Moja Aplikacja{% endblock %}</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```