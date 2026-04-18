# Contributing to StoreChecker

Děkujeme za zájem! Tady jsou pokyny pro přispívání do projektu.

## Jak přispět

### 1. Aktualizace CSS selektorů (Nejdůležitější!)

Scrapery mají zástupné selektory. Pokud chcete, aby projekt fungoval skutečně, musíte aktualizovat CSS selektory.

Postup:
1. Otevřete `SCRAPER_GUIDE.md` v sekci "How to Update Selectors"
2. Navštivtewebové stránky jednotlivého řetězce
3. Otevřete DevTools (F12)
4. Najděte CSS selektory pro: jméno, město, adresu, status skladu
5. Aktualizujte `src/scrapers/retailer_scraper.py`
6. Otestujte s `python main.py --once`

Příklad Pull Requestu:
- Název: "Fix: Update Tesco CSS selectors"
- Popis: "Updated selectors for Tesco store locator (verified on 2024-04-18)"

### 2. Oprava chyb (Bugs)

Pokud najdete bug:
1. Vytvořte Issue se podrobnostmi
2. Zkuste bug reprodukovat
3. Odešlete Pull Request s opravou
4. Zahrňte test reprodukující问题 (pokud je to možné)

### 3. Nové funkce

Pro nové funkce:
1. Nejdřív otevřete Discussion/Issue
2. Popište, co chcete přidat
3. Najděte dohodu na designu
4. Implementujte feature
5. Odešlete Pull Request

### 4. Dokumentace

Vylepšení dokumentace jsou vítány:
- Opravy typo
- Ujasňující vysvětlení
- Nové příklady
- Překlady

## Development Setup

```bash
# Klonujte repo
git clone <repo>
cd storechecker

# Vytvořte virtual env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Nainstalujte requirements
pip install -r requirements.txt

# Zkopírujte config
cp config.example.py config.py
# (Upravte config.py)

# Otestujte změny
python main.py --once
```

## Code Style

Dodržujte PEP 8:

```python
# ✅ Dobré
def get_store_count(self, retailer: Optional[str] = None) -> Dict[str, int]:
    """Get count of stores by retailer."""
    pass

# ❌ Špatné
def getStoreCount(retailer=None):
    pass
```

Pravidla:
- 4 mezery odsazení
- Max 88 znaků na řádek
- Type hints pro funkce
- Docstrings pro třídy/metody
- TODO komentáře s inicialami

## Commit Messages

```bash
# ✅ Dobré commity
git commit -m "feat: Add Baumarkt scraper"
git commit -m "fix: Handle missing store status"
git commit -m "docs: Update SCRAPER_GUIDE"
git commit -m "refactor: Simplify email generation"

# ❌ Špatné commity
git commit -m "fix bug"
git commit -m "changes"
git commit -m "WIP"
```

Formát:
```
<type>: <subject>

<body>

Closes #123
```

Typy:
- `feat:` - Nová funkce
- `fix:` - Oprava chyby
- `docs:` - Dokumentace
- `refactor:` - Refaktorování
- `perf:` - Výkon
- `test:` - Testy
- `chore:` - Build, deps, atd.

## Pull Request Process

1. **Forknite repo** a vytvořte feature branch
   ```bash
   git checkout -b fix/issue-description
   ```

2. **Implementujte změny** a dodržujte code style

3. **Otestujte** s `python main.py --once`

4. **Updatujte dokumentaci** (README, SCRAPER_GUIDE, apod.)

5. **Pushněte změny**
   ```bash
   git push origin fix/issue-description
   ```

6. **Otevřete Pull Request** s popisem:
   - Co se mění?
   - Proč?
   - Jak to testovat?

7. **Odpovězte na review comments**

## Testing Checklist

Před odesláním PR:

- [ ] Kód se spouští bez chyb: `python main.py --once`
- [ ] Scrapery vrací data (pokud nejsou placeholdery)
- [ ] Databáze se vytvoří správně: `sqlite3 data/stores.db`
- [ ] Email se odešle (nebo se zaznamená pokus)
- [ ] Logy jsou bez ERROR/CRITICAL zpráv
- [ ] Code style je PEP 8 (alespoň přibližně)
- [ ] Dokumentace je aktualizovaná

## Problémové řešení při Testech

### ImportError: No module named 'config'

```bash
cp config.example.py config.py
```

### Database is locked

```bash
rm data/stores.db
```

### SMTP connection error

Zkontrolujte v `config.py`:
- Správný server a port
- Správné credentials
- Firewall neblokuje port

## Oblasti, kde je pomoc potřeba

- 🔧 **CSS selektory** - Aktualizace pro všechny řetězce
- 🧪 **Testy** - Unit tests, integration tests
- 📦 **Balení** - Setup.py, Docker, apod.
- 🌐 **Web UI** - Webové rozhraní pro monitorování
- 📱 **Notifikace** - Telegram, Slack, SMS
- 🗺️ **Lokalizace** - Příkazy, UI, komentáře

## Pravidla komunity

- Buďte slušní a respektující
- Přispívejte konstruktivně
- Nebuďte spamem nebo zneužívejte
- Reportujte bezpečnostní problémy diskrétně (neveřejně)

## Otázky?

- 📖 Přečtěte si [README.md](README.md)
- 🔧 Podívejte se na [SCRAPER_GUIDE.md](SCRAPER_GUIDE.md)
- 💬 Otevřete Discussion v GitHubu
- 📧 Kontaktujte maintainera

Děkujeme za přispívání! ❤️
