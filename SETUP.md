# Setup Instructions - Detailní průvodce instalací

## Pokyny pro Windows

### 1. Připravte prostředí

Otevřete PowerShell jako Administrator:

```powershell
# Přejděte do složky projektu
cd "C:\Users\janys\Documents\Projekty\Soukromé\storechecker\storechecker"

# Vytvořte virtuální prostředí
python -m venv venv

# Aktivujte virtuální prostředí
.\venv\Scripts\Activate.ps1

# Pokud dostanete chybu o politice spouštění:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Nainstalujte závislosti

```powershell
pip install -r requirements.txt
```

### 3. Nakonfigurujte aplikaci

```powershell
# Zkopírujte příklad konfigurace
Copy-Item config.example.py config.py

# Otevřete config.py v editoru (přizpůsobte si jej)
notepad config.py
```

Vyplňte v `config.py`:

```python
# SMTP pro Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "vase_email@gmail.com"
SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"  # App password z https://myaccount.google.com/apppasswords

# Příjemci emailů
EMAIL_RECIPIENTS = ["vase_email@gmail.com"]  # Nebo více: ["email1@gmail.com", "email2@example.com"]

# Plánování
SCHEDULE_DAY = "monday"  # pondělí, úterý, ... neděle
SCHEDULE_TIME = "09:00"  # V 24hod formátu
```

**Pro Gmail:**
1. Jděte na https://myaccount.google.com/security
2. Zapněte 2-Factor Authentication
3. Jděte na https://myaccount.google.com/apppasswords
4. Vyberte "Mail" a "Windows Computer"
5. Zkopírujte vygenerovaný 16-znakový kód bez mezer (xxxx xxxx xxxx xxxx)

### 4. Otestujte instalaci

```powershell
# Spusťte kontrolu jednoho skladu (bez naplánování)
python main.py --once

# Měl byste vidět:
# - INFO zprávy s údaji o scrapingu
# - Zprávu o odeslání emailu
# - V složce data/ se vytvoří stores.db
```

### 5. Spusťte plánovaný běh

```powershell
# Spusťte scheduler (poběží na pozadí)
python main.py --schedule

# Aplikace nyní poběží a čeká na plánovaný čas
```

## Pokyny pro Linux/macOS

### 1. Připravte prostředí

```bash
cd ~/path/to/storechecker

# Vytvořte virtuální prostředí
python3 -m venv venv

# Aktivujte virtuální prostředí
source venv/bin/activate
```

### 2. Nainstalujte závislosti

```bash
pip3 install -r requirements.txt
```

### 3. Nakonfigurujte aplikaci

```bash
cp config.example.py config.py

# Upravte config.py (použijte nano, vim, nebo váš oblíbený editor)
nano config.py
```

### 4. Otestujte

```bash
python main.py --once
```

### 5. Spusťte scheduler

```bash
python main.py --schedule
```

Nebo pro běh na pozadí s nohup:

```bash
nohup python main.py --schedule > data/output.log 2>&1 &
```

## Trvalý běh (Background Execution)

### Windows - Task Scheduler

1. Otevřete **Plánovač úloh** (Task Scheduler)
2. V pravém panelu vyberte **Vytvořit základní úlohu** (Create Basic Task)
3. Nastavte:
   - **Jméno**: StoreChecker
   - **Trigger**: Jednodenní nebo Týdenní (dle config.py)
   - **Akce**: Spustit program
     - Program: `C:\path\to\venv\Scripts\python.exe`
     - Argumenty: `main.py --schedule`
     - Spustit v: `C:\path\to\storechecker`

### Linux - Systemd Service

Vytvořte soubor `/etc/systemd/system/storechecker.service`:

```ini
[Unit]
Description=StoreChecker Store Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/storechecker
ExecStart=/home/your_username/storechecker/venv/bin/python main.py --schedule
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Poté spusťte:

```bash
sudo systemctl enable storechecker
sudo systemctl start storechecker
sudo systemctl status storechecker
```

### Linux - Cron

Přidejte do crontab (`crontab -e`):

```cron
# Spustit každé pondělí v 9:00
0 9 * * 1 cd /home/user/storechecker && /home/user/storechecker/venv/bin/python main.py --once >> data/cron.log 2>&1
```

## Ověřte instalaci

### Kontrola databáze

```powershell
# Windows
# (budete potřebovat sqlite3.exe nebo Python)
python -c "import sqlite3; conn = sqlite3.connect('data/stores.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM stores'); print(f'Sklady v databázi: {cursor.fetchone()[0]}')"

# Linux/macOS
sqlite3 data/stores.db "SELECT COUNT(*) FROM stores;"
```

### Kontrola logů

```powershell
# Zobrazit poslední řádky
Get-Content -Tail 50 data/storechecker.log

# Linux/macOS
tail -50 data/storechecker.log

# Sledovat v reálném čase
tail -f data/storechecker.log
```

## Problémové řešení

### Chyba: "config.py not found"

```bash
copy config.example.py config.py
# nebo
cp config.example.py config.py
```

### Chyba: SMTP credentials rejected

- Ověřte username a password v `config.py`
- Zkontrolujte, zda máte zapnutou 2FA a správné App Password
- Pokud používáte Gmail, zkontrolujte, zda vám aplikace "meninger přístup" (Allow less secure apps)

### Chyba: Port 587 blocked

Zkuste port 465 místo 587:

```python
SMTP_PORT = 465
```

### Database is locked

Zavřete všechna ostatní připojení k databázi nebo vymažte `data/stores.db` a spusťte znovu.

### No stores scraped

Selektory jsou zatím placeholdery. Přečtěte si [SCRAPER_GUIDE.md](SCRAPER_GUIDE.md) a aktualizujte CSS selektory v souborech `src/scrapers/*.py`.

## Další kroky

1. 📖 Přečtěte si [README.md](README.md)
2. 🔧 Přečtěte si [SCRAPER_GUIDE.md](SCRAPER_GUIDE.md) - **Tohle je DŮLEŽITÉ!**
   - Scrapery mají zástupné CSS selektory
   - Musíte je aktualizovat skutečnými selektory z webů
3. 💾 Zkontrolujte databázi: `sqlite3 data/stores.db`
4. 📧 Ověřte emailové notifikace
5. ⏰ Nastavte plánování podle vašich potřeb

## Dotazy?

Viz [README.md#troubleshooting](README.md#troubleshooting) nebo [.instructions.md](.instructions.md).

Těšíme se, že StoreChecker použijete! 🚀
