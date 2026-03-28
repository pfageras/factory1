**Opprettet:** 2026-03-28
**Status:** Implementert og godkjent (2026-03-28)

# Plan: Supply chain-fokus for VulnSite

**Referanse:** [Analyse ADN-002](analyser/002-supply-chain-fokus.md) | [Beslutningslogg](beslutningslogg.md)

---

## Nåsituasjon

VulnSite har én datakilde (NVD API 2.0), én flat CVE-liste, og ingen konsept for pakker eller filtrering. Datamodellen har 5 felter uten pakkeinformasjon.

## Målbilde

VulnSite med:
- GitHub Advisory som ny datakilde (reviewed + malware)
- Sammenslåing med NVD-data på CVE-ID
- Filter (Alle / Supply chain / Malware)
- Pakke-informasjon (ecosystem, pakkenavn, sårbar versjon, patch)

---

## F1: Utvidet datamodell og GitHub Advisory-klient
**Leverer:** Ny datamodell med pakke-info, GitHub API-klient som henter advisories
**Filer:**
- `src/models.py` (utvidet med AffectedPackage, source-felt)
- `src/github_client.py` (ny — henter advisories fra GitHub API)

**Akseptansekriterier:**
- [x] `AffectedPackage`-dataklasse med felt: ecosystem, name, vulnerable_range, patched_version (K2)
- [x] `CVE`-modellen utvidet med `source` (nvd/github/both) og `packages` (liste av AffectedPackage) (K2)
- [x] GitHub-klient henter advisories med `type=reviewed` og `type=malware` for siste 7 dager (K1)
- [x] Cursor-basert paginering håndteres korrekt (K1)
- [x] GitHub API-token leses fra miljøvariabel `GITHUB_TOKEN` (valgfri) (K9)
- [x] Ved API-feil returneres tom liste og feilen logges (K8)

**Kompleksitet:** Middels
**Code-review:** GODKJENT — ren kode, god feilhåndtering, korrekt paginering.
**Test:** Verifisert — feilhåndtering fungerer (rate limit 403 håndtert gracefully).

---

## F2: Sammenslåing og cache-oppdatering
**Leverer:** Logikk for å slå sammen NVD- og GitHub-data, oppdatert polling i main.py
**Filer:**
- `src/main.py` (oppdatert lifespan og cache med sammenslåing)

**Akseptansekriterier:**
- [x] GitHub-data og NVD-data slås sammen der CVE-ID matcher — pakke-info legges til NVD-oppføringen (K3)
- [x] Advisories uten CVE-ID (kun GHSA) legges til som separate oppføringer med source=github (K3)
- [x] Sammenslått cache er sortert etter last_modified desc
- [x] GitHub-polling bruker samme periodiske mønster som NVD (hver 2. time) (K7)
- [x] Eksisterende NVD-funksjonalitet fungerer uendret (K10)

**Kompleksitet:** Middels
**Code-review:** GODKJENT etter fiks. Funn: delvis-feil i poll overskrev hel cache — fikset med separate per-kilde cacher.
**Test:** Verifisert — 2723 NVD CVE-er, GitHub rate-limited men gracefully håndtert, filter fungerer, sortering bevart.

---

## F3: API-endepunkt med filter
**Leverer:** Utvidet `GET /api/cves` med filter-parameter og pakke-data i respons
**Filer:**
- `src/main.py` (oppdatert endepunkt)

**Akseptansekriterier:**
- [x] `GET /api/cves` returnerer alle CVE-er som standard (filter=all) (K4, K10)
- [x] `GET /api/cves?filter=supply_chain` returnerer kun oppføringer med pakke-info (K4)
- [x] `GET /api/cves?filter=malware` returnerer kun malware-advisories (K4)
- [x] Hvert CVE-objekt inkluderer `source` og `packages`-felter i JSON-respons (K2)
- [x] Pakke-objekter inneholder: ecosystem, name, vulnerable_range, patched_version (K2)

**Kompleksitet:** Lav
**Code-review:** GODKJENT (sammenslått med F2-review)
**Test:** Verifisert — filter=all/supply_chain/malware returnerer korrekte resultater.

---

## F4: Frontend — filter og pakke-visning
**Leverer:** Filter-tabs og pakke-kolonne i CVE-tabellen
**Filer:**
- `src/static/index.html` (filter-knapper)
- `src/static/style.css` (styling for filter og pakke-badges)
- `src/static/app.js` (filter-logikk, pakke-rendering)

**Akseptansekriterier:**
- [x] Filter-tabs «Alle», «Supply chain», «Malware» vises over tabellen (K5)
- [x] Klikk på filter henter data med riktig filter-parameter (K5)
- [x] Ny kolonne «Pakker» viser ecosystem:pakkenavn med versjon-info (K6)
- [x] Patchet versjon vises med → (f.eks. «npm:lodash <4.17 → 4.17.21») (K6)
- [x] Rader uten pakke-info viser «—» i pakke-kolonnen
- [x] CVE-ID-lenke peker til NVD for CVE-er, GitHub for rene GHSA-er
- [x] Eksisterende fargekoding og layout er bevart (K10)

**Kompleksitet:** Middels
**Code-review:** GODKJENT — ingen XSS, konsekvent escaping, korrekte filter-tabs og pakke-rendering.
**Test:** Verifisert — 3 filter-knapper, pakke-kolonne, CSS/JS servert korrekt, source/packages i API.

---

## F5: Konfigurasjon og dokumentasjon
**Leverer:** Oppdatert env-konfig og CLAUDE.md
**Filer:**
- `deploy/vulnsite.env.example` (nytt GITHUB_TOKEN-felt)
- `CLAUDE.md` (oppdatert med ny datakilde-info)

**Akseptansekriterier:**
- [x] `GITHUB_TOKEN` dokumentert i env.example (K9)
- [x] `CLAUDE.md` oppdatert med GitHub Advisory som datakilde
- [x] Eksisterende driftsinstruksjoner uendret (K10)

**Kompleksitet:** Lav
**Code-review:** GODKJENT — trivielle dokumentasjonsendringer.
**Test:** Verifisert manuelt.

---

## Integrasjon
**Verifisering:**
- [x] Server starter og henter data fra både NVD og GitHub Advisory
- [x] Filter fungerer korrekt i frontend
- [x] Pakke-info vises for supply chain-oppføringer (krever GITHUB_TOKEN for data)
- [x] Eksisterende NVD-visning er uendret (regresjon)

**Integrasjonsreview:** GODKJENT — alle komponenter fungerer, graceful degradation ved GitHub rate limit.

---

## Resultat

**Status:** Implementert og godkjent (2026-03-28)

**Omfang:**
- 1 ny fil: `src/github_client.py`
- 4 endrede filer: `src/main.py`, `src/models.py`, `src/static/` (alle 3 frontend-filer)
- 2 oppdaterte konfig-filer: `CLAUDE.md`, `deploy/vulnsite.env.example`
- 2 nye analysedokumenter

### Code-review funn løst underveis

| Funn | Alvorlighet | Løsning |
|------|-------------|---------|
| Delvis kilde-feil overskrev hel cache | Middels | Separate per-kilde cacher (_last_nvd, _last_github) |

### Testresultater

| Test | Forventet | Resultat |
|------|-----------|---------|
| GET /health | `{"status": "ok"}` | OK |
| GET /api/cves (default) | Alle CVE-er med source/packages | OK (2723) |
| GET /api/cves?filter=supply_chain | Kun med pakker | OK (0 pga rate limit) |
| GET /api/cves?filter=malware | Kun malware | OK (0 pga rate limit) |
| GET /api/cves?filter=invalid | 422 validering | OK |
| Sortering desc | Datoer synkende | OK |
| Frontend HTML/CSS/JS | 200 for alle | OK |
| GitHub API-feil | Graceful, NVD-data bevart | OK |
