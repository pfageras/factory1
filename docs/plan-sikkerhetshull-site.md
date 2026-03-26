**Opprettet:** 2026-03-26
**Status:** Implementert og godkjent (2026-03-26)

# Plan: Site for nylig oppdaterte sikkerhetshull

**Referanse:** [Analyse ADN-001](analyser/001-sikkerhetshull-site.md) | [Beslutningslogg](beslutningslogg.md)

---

## Nåsituasjon

Prosjektet har ingen eksisterende kode. Kun skill-definisjoner finnes under `.claude/skills/`. Alt må etableres fra bunnen — prosjektstruktur, avhengigheter, backend, frontend og driftskonfigurasjon.

## Målbilde

En fungerende webapplikasjon som:
- Henter CVE-data fra NVD API 2.0 (siste 7 dager)
- Viser sårbarhetene i en sortert, fargekodert tabell
- Kjører som systemd-tjeneste på Raspberry Pi
- Har tydelig backend/frontend-separasjon

---

## F1: Prosjektstruktur og infrastruktur
**Leverer:** Prosjektskjelett med avhengigheter, CLAUDE.md, og kjørbar «hello world»-server
**Filer:**
- `CLAUDE.md`
- `requirements.txt`
- `src/main.py` (FastAPI-app med health-endepunkt)
- `src/static/` (tom katalog for frontend)

**Akseptansekriterier:**
- [x] `CLAUDE.md` finnes i prosjektroten med prosjektbeskrivelse og utviklingsinstruksjoner (K10)
- [x] `requirements.txt` inneholder fastapi, uvicorn, httpx
- [x] `python3 -m uvicorn src.main:app` starter serveren uten feil
- [x] `GET /health` returnerer `{"status": "ok"}`

**Kompleksitet:** Lav
**Code-review:** GODKJENT — ren kode, minimalt scope, ingen sikkerhetsfunn. Observasjon: StaticFiles mount på `/` fanger alle ruter — nye endepunkter må defineres før mount-linjen.
**Test:** Verifisert manuelt — server starter, /health returnerer ok, / returnerer 200.

---

## F2: NVD API-klient og caching
**Leverer:** Modul som henter CVE-data fra NVD API 2.0, parser respons og cacher i minne
**Filer:**
- `src/nvd_client.py` (NVD API-klient med async HTTP)
- `src/models.py` (dataklasser for CVE-data)
- `src/main.py` (oppdatert med lifespan for periodisk polling)

**Akseptansekriterier:**
- [x] NVD-klienten henter CVE-er med `lastModStartDate`/`lastModEndDate` for siste 7 dager (K1)
- [x] CVE-data parses til dataklasser med felt: id, beskrivelse, cvss_score, severity, last_modified (K1)
- [x] Data caches i minne og oppdateres periodisk via bakgrunnsoppgave (K5)
- [x] NVD API-nøkkel leses fra miljøvariabel `NVD_API_KEY` (valgfri — fungerer uten, men med lavere rate limit)
- [x] Ved NVD API-feil returneres cached data, og feilen logges (K6)
- [x] Paginering håndteres for resultatsett > 2000 CVE-er (K1)

**Kompleksitet:** Middels
**Code-review:** BETINGET GODKJENT → GODKJENT etter fiks. Funn: timestamp-format manglet tidssone-suffix (+00:00) — fikset. Ingen paginering på API-endepunktet notert som akseptabelt for MVP.
**Test:** Verifisert — 2674 CVE-er hentet fra NVD med paginering (2 sider), sortert korrekt.

---

## F3: REST API-endepunkt
**Leverer:** `GET /api/cves` endepunkt som returnerer cached CVE-data som JSON
**Filer:**
- `src/main.py` (nytt endepunkt)

**Akseptansekriterier:**
- [x] `GET /api/cves` returnerer JSON-liste med CVE-objekter (K2)
- [x] Hvert objekt inneholder: id, description, cvss_score, severity, last_modified (K2)
- [x] Listen er sortert etter last_modified, nyeste først (K4)
- [x] Ved tom cache returneres `{"cves": [], "last_updated": null}` (K6)
- [x] Respons inkluderer `last_updated`-tidsstempel for siste vellykkede NVD-henting

**Kompleksitet:** Lav
**Code-review:** GODKJENT (sammenslått med F2-review)
**Test:** Verifisert — JSON-respons med korrekt struktur, 2674 CVE-er, sortert nyeste først.

---

## F4: Frontend — HTML/CSS/JS
**Leverer:** Statisk webside som henter og viser CVE-data fra backend-API
**Filer:**
- `src/static/index.html`
- `src/static/style.css`
- `src/static/app.js`
- `src/main.py` (oppdatert for å servere statiske filer)

**Akseptansekriterier:**
- [x] Frontend viser CVE-tabell med kolonnene: ID, Beskrivelse, CVSS-score, Alvorlighet, Sist endret (K3)
- [x] Alvorlighetsgrad vises med fargekoding: kritisk=rød, høy=oransje, medium=gul, lav=grønn (K9)
- [x] Tabellen sorteres etter sist endret, nyeste først (K4)
- [x] Tidsstempel for siste oppdatering fra NVD vises på siden
- [x] Ingen JavaScript-rammeverk brukes — kun vanilla HTML/CSS/JS (K7)
- [x] Siden er lesbar og funksjonell på desktop-oppløsning

**Kompleksitet:** Middels
**Code-review:** BETINGET GODKJENT → GODKJENT etter fiks. Funn: cvss_score manglet typesjekk/escaping — fikset med typeof-sjekk og escapeHtml. XSS-beskyttelse ellers god.
**Test:** Verifisert — HTML, CSS og JS serveres korrekt, alle elementer på plass.

---

## F5: Systemd-tjeneste og driftskonfigurasjon
**Leverer:** Systemd unit-fil og instruksjoner for drift på Raspberry Pi
**Filer:**
- `deploy/vulnsite.service` (systemd unit-fil)
- `CLAUDE.md` (oppdatert med driftsinstruksjoner)

**Akseptansekriterier:**
- [x] Systemd unit-fil finnes og er korrekt konfigurert for applikasjonen (K8)
- [x] Tjenesten starter applikasjonen med uvicorn på konfigurerbar port (standard 8000) (K8)
- [x] Miljøvariabel `NVD_API_KEY` kan settes i unit-filen eller via environment-fil
- [x] `CLAUDE.md` inneholder instruksjoner for installasjon, oppstart og konfigurasjon (K10)

**Kompleksitet:** Lav
**Code-review:** BETINGET GODKJENT → GODKJENT etter fiks. Funn: port var hardkodet — gjort konfigurerbar via VULNSITE_PORT miljøvariabel.
**Test:** Verifisert — unit-fil er syntaktisk korrekt, env.example dokumenterer begge variabler.

---

## Integrasjon
**Verifisering:**
- [x] Alle faser fungerer sammen — server starter, henter data fra NVD, viser i frontend
- [x] Frontend viser reelle CVE-data hentet fra NVD API
- [x] Serveren håndterer NVD-feil uten å krasje (kode-review verifisert, try/except med logging)
- [ ] Systemd-tjenesten starter og kjører stabilt (krever `sudo` — verifiseres ved deploy)

**Integrasjonsreview:** GODKJENT — alle komponenter fungerer sammen, 2674 CVE-er hentet og vist.

---

## Resultat

**Status:** Implementert og godkjent (2026-03-26)

**Omfang:**
- 7 filer opprettet (main.py, nvd_client.py, models.py, index.html, style.css, app.js, vulnsite.service)
- 2 konfigurasjonsfiler (requirements.txt, vulnsite.env.example)
- 1 prosjektdokument (CLAUDE.md)
- 3 analysedokumenter (analyse, plan, beslutningslogg)

### Code-review funn løst underveis

| Funn | Alvorlighet | Løsning |
|------|-------------|---------|
| Timestamp-format uten tidssone i NVD-kall | Moderat | Lagt til `+00:00` suffix |
| cvss_score manglet typesjekk/escaping i frontend | Moderat | Lagt til `typeof`-sjekk og `escapeHtml` |
| Port hardkodet i systemd unit-fil | Lavt | Gjort konfigurerbar via `VULNSITE_PORT` miljøvariabel |

### Testresultater

| Test | Forventet | Resultat |
|------|-----------|---------|
| GET /health | `{"status": "ok"}` | OK |
| GET /api/cves — data hentet | >0 CVE-er | 2674 CVE-er |
| GET /api/cves — sortert desc | Datoer synkende | OK (verifisert programmatisk) |
| GET /api/cves — paginering | Håndterer >2000 resultater | OK (2 sider hentet) |
| GET / — frontend HTML | Inneholder cve-body | OK |
| GET /style.css — CSS servert | HTTP 200 | OK |
| GET /app.js — JS servert | HTTP 200 | OK |
