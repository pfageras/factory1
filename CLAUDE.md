# VulnSite — Sikkerhetshull-oversikt

Webapplikasjon som henter og viser nylig oppdaterte sikkerhetshull (CVE-er) med fokus på supply chain-angrep.

## Datakilder

- **NVD API 2.0** — alle CVE-er oppdatert siste 7 dager (generell sårbarhetsoversikt)
- **GitHub Advisory Database** — reviewed advisories + malware (pakke-spesifikk info: ecosystem, pakkenavn, sårbar versjon, patch)

## Teknologi

- **Backend:** Python 3.11, FastAPI, uvicorn, httpx
- **Frontend:** Vanilla HTML/CSS/JS (ingen rammeverk)
- **Datakilder:** NVD API 2.0, GitHub Advisory Database
- **Drift:** systemd på Raspberry Pi 5 (aarch64)

## Prosjektstruktur

```
factory1/
├── CLAUDE.md
├── requirements.txt
├── src/
│   ├── main.py          # FastAPI-app, endepunkter, lifespan
│   ├── nvd_client.py    # NVD API-klient
│   ├── github_client.py # GitHub Advisory API-klient
│   ├── models.py        # Dataklasser for CVE- og pakkedata
│   └── static/          # Frontend (HTML/CSS/JS)
│       ├── index.html
│       ├── style.css
│       └── app.js
├── deploy/
│   └── vulnsite.service # systemd unit-fil
└── docs/
    ├── beslutningslogg.md
    ├── plan-sikkerhetshull-site.md
    └── analyser/
        └── 001-sikkerhetshull-site.md
```

## Utvikling

```bash
# Opprett og aktiver virtuelt miljø
python3 -m venv .venv
source .venv/bin/activate

# Installer avhengigheter
pip install -r requirements.txt

# Start utviklingsserver
python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Valgfri: API-nøkler for høyere rate limits
export NVD_API_KEY=din-nøkkel-her
export GITHUB_TOKEN=ghp_din-token-her
```

## Drift

```bash
# Kopier og aktiver systemd-tjeneste
sudo cp deploy/vulnsite.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vulnsite
sudo systemctl start vulnsite

# Valgfri: konfigurer NVD API-nøkkel
cp deploy/vulnsite.env.example deploy/vulnsite.env
# Rediger deploy/vulnsite.env og legg inn nøkkelen

# Sjekk status
sudo systemctl status vulnsite
journalctl -u vulnsite -f
```

Applikasjonen er tilgjengelig på `http://<pi-ip>:8000`.
