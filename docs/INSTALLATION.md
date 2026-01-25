# DjCrudX - Instrukcje instalacji i publikacji

## 🔧 Przygotowanie środowiska deweloperskiego

```bash
# Sklonuj projekt
git clone <repository-url>
cd djcrudx-package

# Synchronizuj zależności (tworzy .venv automatycznie)
uv sync

# Aktywuj środowisko wirtualne
source .venv/bin/activate
# lub na Windows: .venv\Scripts\activate
```

## 📦 Budowanie pakietu

```bash
# Użyj skryptu build
./build.sh

# Lub ręcznie:
uv build
```

## 🧪 Testowanie lokalnie

```bash
# Zainstaluj lokalnie z pliku wheel
uv pip install dist/djcrudx-0.1.0-py3-none-any.whl

# Lub w trybie edytowalnym
uv pip install -e .
```

## 📤 Publikacja na PyPI

### Test PyPI (zalecane najpierw)

```bash
# Zarejestruj się na https://test.pypi.org/
# Utwórz API token

uv run twine upload --repository testpypi dist/*

# Testuj instalację
uv pip install --index-url https://test.pypi.org/simple/ djcrudx
```

### Produkcyjne PyPI

```bash
# Zarejestruj się na https://pypi.org/
# Utwórz API token

uv run twine upload dist/*

# Instalacja przez użytkowników
pip install djcrudx
# lub
uv add djcrudx
```

## 🔑 Konfiguracja tokenów

Utwórz plik `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_API_TOKEN_HERE
```

## 📋 Checklist przed publikacją

- [ ] Zaktualizuj wersję w `pyproject.toml`
- [ ] Zaktualizuj `README.md` z najnowszymi funkcjami
- [ ] Przetestuj lokalnie (`uv sync && uv run pytest`)
- [ ] Zbuduj pakiet (`uv build`)
- [ ] Opublikuj na Test PyPI
- [ ] Przetestuj instalację z Test PyPI
- [ ] Opublikuj na produkcyjnym PyPI

## 🚀 Użycie przez użytkowników końcowych

```bash
# Instalacja
pip install djcrudx
# lub
uv add djcrudx

# W settings.py
INSTALLED_APPS = [
    # ...
    'djcrudx',
    # ...
]

# W kodzie
from djcrudx import create_crud
from djcrudx.widgets import MultiSelectDropdownWidget
```

## 🛠️ Komendy deweloperskie

```bash
# Synchronizuj zależności
uv sync

# Dodaj nową zależność
uv add django-extensions

# Dodaj zależność deweloperską
uv add --group dev pytest-cov

# Uruchom testy
uv run pytest

# Formatuj kod
uv run black .

# Sprawdź jakość kodu
uv run flake8

# Zbuduj pakiet
uv build

# Opublikuj na PyPI
uv run twine upload dist/*
```