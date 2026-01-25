# DjCrudX - Uniwersalne tłumaczenia

DjCrudX obsługuje **3 sposoby tłumaczeń** w kolejności priorytetów:

## 1. 🥇 Django i18n (standardowe) - NAJWYŻSZY PRIORYTET

```python
# settings.py
LANGUAGE_CODE = 'pl'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

```bash
python manage.py makemessages -l pl
python manage.py compilemessages
```

## 2. 🥈 Własne tłumaczenia w settings.py

```python
# settings.py
DJCRUDX_TRANSLATIONS = {
    'pl': {
        'Create': 'Dodaj nowy',
        'Edit': 'Modyfikuj',
        'Delete': 'Usuń element',
        'Save': 'Zachowaj',
    },
    'de': {
        'Create': 'Erstellen',
        'Edit': 'Bearbeiten',
    }
}
```

## 3. 🥉 Wbudowane tłumaczenia (fallback)

Automatyczne dla języka polskiego - nie musisz nic robić!

```python
# settings.py - WYSTARCZY TO!
LANGUAGE_CODE = 'pl'
```

## Przykład użycia wszystkich opcji

```python
# settings.py
LANGUAGE_CODE = 'pl'
USE_I18N = True

# Własne tłumaczenia (nadpisują wbudowane)
DJCRUDX_TRANSLATIONS = {
    'pl': {
        'Create': 'Dodaj nowy rekord',  # Zamiast "Utwórz"
        'Edit': 'Modyfikuj dane',       # Zamiast "Edytuj"
    }
}
```

**Rezultat:**
- "Create" → "Dodaj nowy rekord" (z DJCRUDX_TRANSLATIONS)
- "Delete" → "Usuń" (z wbudowanych tłumaczeń)
- Inne teksty → standardowe Django i18n (jeśli istnieją)

## Dodawanie nowych języków

```python
# settings.py
DJCRUDX_TRANSLATIONS = {
    'de': {
        'Create': 'Erstellen',
        'Edit': 'Bearbeiten',
        'Delete': 'Löschen',
        'Save': 'Speichern',
        'Cancel': 'Abbrechen',
    },
    'fr': {
        'Create': 'Créer',
        'Edit': 'Modifier',
        'Delete': 'Supprimer',
    }
}
```