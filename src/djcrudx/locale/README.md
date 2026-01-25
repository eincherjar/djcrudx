# DjCrudX Internationalization (i18n)

DjCrudX supports Django's internationalization framework. All user-facing text in templates uses Django's `{% trans %}` and `{% blocktrans %}` tags.

## Available Translations

Currently supported languages:
- English (en) - default
- Polish (pl) - example
- Add more languages by contributing translation files

## How to Add Translations

1. **In your Django project**, add DjCrudX to `LOCALE_PATHS`:

```python
# settings.py
import djcrudx
import os

LOCALE_PATHS = [
    os.path.join(os.path.dirname(djcrudx.__file__), 'locale'),
    # your other locale paths...
]

LANGUAGES = [
    ('en', 'English'),
    ('pl', 'Polish'),
    ('it', 'Italian'),
    # add more languages...
]
```

2. **Generate translation files**:

```bash
# In your project root
python manage.py makemessages -l pl
python manage.py makemessages -l it
```

3. **Translate the strings** in `locale/[lang]/LC_MESSAGES/django.po`

4. **Compile translations**:

```bash
python manage.py compilemessages
```

## Key Translatable Strings

- "Previous" / "Next" - pagination navigation
- "Show:" - items per page selector
- "Showing X to Y of Z results" - pagination info
- Form labels and buttons (in your forms)

## Override Templates

You can override any DjCrudX template in your project:

```
your_project/
├── templates/
│   └── crud/
│       ├── base.html          # Override base template
│       ├── list_view.html     # Override list template
│       └── _partials/
│           └── pagination.html # Override pagination
```

This allows you to:
- Add custom translations
- Change styling
- Modify layout
- Add custom functionality