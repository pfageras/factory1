# Analyse: Site for nylig oppdaterte sikkerhetshull

**Opprettet:** 2026-03-26
**Beslutningslogg:** [ADN-001](../beslutningslogg.md)
**Referanser:** NVD API 2.0 docs, CVE.org API, GitHub Advisory Database API, OSV API

## Bakgrunn

Factory1 skal levere sitt første produkt: en webside som henter og viser nylig oppdaterte sikkerhetshull (CVE-er). Product-owner har gitt BETINGET ANBEFALT med krav om strengt avgrenset scope, tydelig backend/frontend-separasjon, og definisjon av «nylig oppdatert».

Målmiljø: Raspberry Pi 5 (aarch64, 16 GB RAM, 4 kjerner), Debian 12, Python 3.11, Node.js 22, Java 17, systemd.

---

## Nåsituasjon

Prosjektet har ingen eksisterende kode — kun skill-definisjoner for den autonome utviklingspipelinen. Det finnes ingen webserver, database, eller prosjektinfrastruktur. Alt må etableres fra bunnen av.

---

## Datakilder

Undersøkte kilder for sårbarhetsinformasjon:

| Kilde | Autentisering | «Nylig endret»-støtte | CVSS-score | Pakke-info | Vurdering |
|-------|--------------|----------------------|------------|------------|-----------|
| **NVD API 2.0** | Gratis API-nøkkel (anbefalt) | Ja — `lastModStartDate/EndDate` | Ja (v2, v3.0, v3.1) | Nei (CPE) | **Beste primærkilde** |
| CVE.org API | Ingen | Ja — `time_modified.gt` | Kun CNA-score | Nei | God sekundærkilde |
| GitHub Advisory | Gratis PAT | Ja — `sort=updated` | Ja | Ja (npm, pip, etc.) | Best for open source-pakker |
| OSV API | Ingen | Nei (kun bulk) | Kun CVSS-vektor | Ja | Vanskelig å polle |

**Anbefalt datakilde:** NVD API 2.0 — mest komplett, gratis, god støtte for inkrementelle oppdateringer.

**Definisjon av «nylig oppdatert»:** CVE-er endret siste 7 dager. NVD API støtter dette direkte via `lastModStartDate`/`lastModEndDate`. Maks 120 dagers spenn per forespørsel.

---

## Analyse

### Alternativ A: Python (FastAPI) + Vanilla HTML/JS

**Backend:** FastAPI med uvicorn. Henter CVE-data fra NVD API, cacher i minne eller SQLite, eksponerer REST-endepunkt.
**Frontend:** Statisk HTML med vanilla JavaScript som henter data fra backend-API.

| Egenskap | Vurdering |
|----------|-----------|
| Implementeringskompleksitet | Lav — FastAPI er minimalistisk, god async-støtte |
| Ressursforbruk | Lavt — Python + uvicorn er lett på RPi |
| Backend/frontend-separasjon | Tydelig — API serverer JSON, frontend er statisk |
| Vedlikehold | Enkelt — lite kode, kjente biblioteker |
| Testbarhet | God — FastAPI har innebyggd testklient |
| Drift | systemd-tjeneste, enkel å administrere |
| Pakker aarch64 | Alle tilgjengelige — ingen native-kompilering nødvendig |

**Fordeler:**
- Raskest til fungerende MVP
- Minimal kodemengde
- Godt økosystem for HTTP-klienter (httpx/aiohttp)
- Naturlig async for API-polling

**Ulemper:**
- Ingen type-sjekking uten ekstra verktøy
- Ytelse er tilstrekkelig men ikke optimal for høy last (irrelevant for MVP)

### Alternativ B: Node.js (Express) + Vanilla HTML/JS

**Backend:** Express.js med node-cron for polling. Henter CVE-data fra NVD, cacher i minne, eksponerer REST-endepunkt.
**Frontend:** Statisk HTML med vanilla JavaScript.

| Egenskap | Vurdering |
|----------|-----------|
| Implementeringskompleksitet | Lav — Express er minimalistisk |
| Ressursforbruk | Moderat — Node.js bruker mer minne enn Python for enkel API |
| Backend/frontend-separasjon | Tydelig — samme mønster som Alt. A |
| Vedlikehold | OK — npm-økosystemet har mange avhengigheter |
| Testbarhet | OK — krever mer oppsett (jest/mocha) |
| Drift | systemd-tjeneste, enkel å administrere |
| Pakker aarch64 | Tilgjengelige — Node 22 støtter aarch64 |

**Fordeler:**
- Ett språk for backend og frontend (JS)
- God async I/O

**Ulemper:**
- Mer boilerplate enn FastAPI for REST-API
- npm dependency-treet kan bli stort
- Ingen innebyggd API-testramme som FastAPI TestClient

### Alternativ C: Java (Quarkus) + Vanilla HTML/JS

Droppet fra videre vurdering. For tungt for en MVP på Raspberry Pi — lang oppstartstid, høyt minneforbruk, mye boilerplate. Passer bedre for større systemer.

### Sammenligning

| Egenskap | Alt. A (Python/FastAPI) | Alt. B (Node/Express) |
|----------|------------------------|----------------------|
| Tid til MVP | ⭐⭐⭐ Kort | ⭐⭐ Moderat |
| Kodemengde | ⭐⭐⭐ Minimal | ⭐⭐ Noe mer |
| Ressursforbruk RPi | ⭐⭐⭐ Lavt | ⭐⭐ Moderat |
| Testbarhet | ⭐⭐⭐ Innebyggd | ⭐⭐ Krever oppsett |
| Async-støtte | ⭐⭐⭐ Nativt | ⭐⭐⭐ Nativt |
| Avhengigheter | ⭐⭐⭐ Få | ⭐⭐ Mange |

---

## Anbefaling

**Alternativ A: Python (FastAPI) + Vanilla HTML/JS.**

Begrunnelse:
1. **Lavest kompleksitet** — FastAPI gir mest funksjonalitet per linje kode
2. **Best egnet for RPi** — lavt ressursforbruk
3. **Best testbarhet** — innebyggd TestClient forenkler integrasjonstesting
4. **Færrest avhengigheter** — enklere vedlikehold
5. **Demonstrerer fabrikkens evne** — tydelig backend/frontend-separasjon, kvalitetsporter, full pipeline

### Arkitektur

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   NVD API 2.0   │────►│  FastAPI Backend  │────►│  Statisk    │
│   (ekstern)     │     │  - /api/cves      │     │  Frontend   │
└─────────────────┘     │  - Polling/cache  │     │  HTML/JS    │
                        └──────────────────┘     └─────────────┘
                         systemd-tjeneste         Servert av FastAPI
```

**Dataflyt:**
1. Backend poller NVD API periodisk (hver 2. time, som NVD anbefaler)
2. Svar caches i minne (dict/liste — ingen database i V1)
3. Frontend henter data fra `/api/cves` og rendrer en tabell
4. Frontend serveres som statiske filer fra FastAPI

---

## Krav

| ID | Krav | Verifiseringsmetode |
|----|------|---------------------|
| K1 | Backend SKAL hente CVE-data fra NVD API 2.0 med `lastModStartDate`/`lastModEndDate` for siste 7 dager | Integrasjonstest: kall backend-API, verifiser at respons inneholder CVE-data med gyldige felter |
| K2 | Backend SKAL eksponere et REST-endepunkt (`GET /api/cves`) som returnerer CVE-liste i JSON | Integrasjonstest: HTTP GET mot endepunktet, verifiser JSON-respons med korrekt struktur |
| K3 | Frontend SKAL vise en liste over CVE-er med: ID, beskrivelse, CVSS-score, alvorlighetsgrad og dato for siste endring | Manuell inspeksjon + integrasjonstest som verifiserer at HTML-respons inneholder forventede elementer |
| K4 | CVE-listen SKAL sorteres etter dato for siste endring (nyeste først) | Integrasjonstest: verifiser at datoer i JSON-respons er synkende |
| K5 | Backend SKAL cache NVD-data i minne og oppdatere periodisk (minst hver 2. time) | Verifiser at to kall til `/api/cves` innen kort tid ikke trigger to NVD API-kall |
| K6 | Backend SKAL håndtere NVD API-feil gracefully — returnere cached data eller tom liste med feilmelding, ikke krasje | Integrasjonstest: simuler NVD-feil, verifiser at backend returnerer gyldig respons |
| K7 | Frontend SKAL fungere uten JavaScript-rammeverk — vanilla HTML/CSS/JS | Kode-review: ingen rammeverk-importer i frontend-kode |
| K8 | Applikasjonen SKAL kunne kjøres som systemd-tjeneste på Raspberry Pi (aarch64) | Verifiser at systemd-unit-fil finnes og tjenesten starter uten feil |
| K9 | Alvorlighetsgrad SKAL vises med fargekoding (kritisk=rød, høy=oransje, medium=gul, lav=grønn) | Manuell inspeksjon av frontend |
| K10 | Prosjektet SKAL ha CLAUDE.md med prosjektbeskrivelse og utviklingsinstruksjoner | Verifiser at filen finnes og inneholder relevant informasjon |

---

## Integrasjonspunkter

| System | Type | Retning | Detaljer |
|--------|------|---------|----------|
| NVD API 2.0 | REST API | Utgående | Polling hver 2. time. API-nøkkel via miljøvariabel. |
| Nettleser | HTTP | Innkommende | Frontend serveres på port 8000 (konfigurerbar) |
| systemd | Prosesstyring | Lokal | Starter/stopper applikasjonen |

---

## Risiko

| Risiko | Sannsynlighet | Konsekvens | Mottiltak |
|--------|--------------|------------|-----------|
| NVD API nede/treg | Middels | Stale data | Cache alltid siste gyldige respons, vis tidsstempel for siste oppdatering |
| NVD API endrer format | Lav | Parsing feiler | Robust feilhåndtering, logg advarsler |
| Rate limiting (uten API-nøkkel) | Høy | Blokkert | Bruk API-nøkkel (gratis), poll maks hver 2. time |
| Mange CVE-er (>2000 siste 7 dager) | Middels | Paginering nødvendig | Implementer paginering i NVD-kallet |

---

## Videre arbeid

1. Bruker godkjenner denne analysen
2. Software-developer lager faset implementeringsplan basert på krav K1-K10
3. Implementering, code-review og testing per fase
