# Analyse: Supply chain-fokus for VulnSite

**Opprettet:** 2026-03-28
**Beslutningslogg:** [ADN-002](../beslutningslogg.md)
**Referanser:** GitHub Advisory Database REST API docs, NVD API 2.0 docs, ADN-001

## Bakgrunn

VulnSite viser i dag alle nylig oppdaterte CVE-er fra NVD. Brukeren ønsker å utvide med fokus på supply chain-angrep — sikkerhetshull knyttet til programvarepakker (npm, pip, Maven, etc.). Product-owner har gitt BETINGET ANBEFALT med krav om: én ny datakilde (GitHub Advisory), filter/visning (ikke erstatning), og pakke-informasjon som merverdi.

---

## Nåsituasjon

VulnSite har:
- FastAPI-backend med NVD API 2.0 som eneste datakilde
- In-memory cache med polling hver 2. time
- Én CVE-modell med: id, description, cvss_score, severity, last_modified
- Frontend med én flat tabell over alle CVE-er
- Ingen konsept for «pakker», «ecosystems» eller filtrering

---

## Analyse

### Alternativ A: GitHub Advisory som separat datakilde med sammenslåing

**Beskrivelse:** Legg til en ny klient (`github_client.py`) som henter advisories fra GitHub Advisory Database REST API. Advisories berikes med pakke-informasjon (ecosystem, pakkenavn, sårbare versjoner, patchet versjon). Data slås sammen med NVD-data der CVE-ID matcher; advisories uten CVE-ID vises separat. Frontend får et filter for «Alle» vs «Supply chain» og viser pakke-kolonner når relevant.

| Egenskap | Vurdering |
|----------|-----------|
| Datakvalitet | Høy — GitHub-reviewed advisories er kuraterte med pakke-info |
| API-tilgang | Enkel — fungerer uten auth (60 req/t), bedre med token (5000 req/t) |
| Paginering | Cursor-basert (Link-header) — litt mer kompleks enn NVD |
| Pakke-info | Ecosystem, pakkenavn, vulnerable_version_range, first_patched_version |
| Sammenslåing | Mulig via CVE-ID, men ikke alle GHSA har CVE |
| Vedlikehold | Moderat — to datakilder å vedlikeholde |

**Fordeler:**
- Reell pakke-informasjon gjør data *handlingsbar* for utviklere
- `type=reviewed` gir høy datakvalitet (kuratert av GitHub security team)
- `type=malware` gir tilgang til kjent ondsinnet programvare (typosquatting etc.)
- Filter gir brukeren kontroll uten å miste generell CVE-oversikt
- Uautentisert tilgang fungerer for lav polling-frekvens

**Ulemper:**
- To datakilder øker kompleksiteten i backend
- Sammenslåing på CVE-ID er ikke 1:1 — noen GHSA mangler CVE
- Cursor-basert paginering krever annerledes logikk enn NVD

### Alternativ B: NVD CWE-filtrering for supply chain-kategorier

**Beskrivelse:** Bruk eksisterende NVD-data og filtrer på CWE-kategorier relatert til supply chain (CWE-1357: Reliance on Insufficiently Trustworthy Component, CWE-506: Embedded Malicious Code, etc.). Frontend får et filter basert på CWE-koder.

| Egenskap | Vurdering |
|----------|-----------|
| Datakvalitet | Lav — CWE-kategorisering er inkonsekvent for supply chain |
| API-tilgang | Ingen ekstra — bruker eksisterende NVD-data |
| Pakke-info | Ingen — NVD har CPE men ikke pakke/versjon-info |
| Vedlikehold | Lavt — kun frontend-filter |

**Fordeler:**
- Ingen ny datakilde — enkel implementering
- Ingen ekstra API-kall

**Ulemper:**
- CWE-klassifisering for supply chain er svak og inkonsekvent
- Ingen pakke-informasjon — data er ikke handlingsbar
- Gir falsk trygghet — mange supply chain-CVE-er har ikke riktig CWE

### Sammenligning

| Egenskap | Alt. A (GitHub Advisory) | Alt. B (CWE-filter) |
|----------|--------------------------|---------------------|
| Pakke-info | ✅ Ecosystem, pakke, versjoner | ❌ Ingen |
| Datakvalitet | ✅ Kuratert | ⚠️ Inkonsekvent |
| Handlingsbar for utvikler | ✅ «Oppdater pakke X til Y» | ❌ Bare generell CVE |
| Malware-deteksjon | ✅ `type=malware` | ❌ Ikke mulig |
| Implementeringskompleksitet | Middels | Lav |
| Ny datakilde | Ja (1 ekstra) | Nei |

---

## Anbefaling

**Alternativ A: GitHub Advisory som separat datakilde med sammenslåing.**

Begrunnelse:
1. **Handlingsbar data** — pakke, versjon og patch-info er det som gjør supply chain-data verdifull
2. **Malware-oversikt** — `type=malware` gir unikt innhold som NVD ikke har
3. **Kuratert kvalitet** — GitHub-reviewed advisories har høyere kvalitet enn rå CWE-filtrering
4. **Naturlig filter** — «har pakke-info» er et bedre filter enn CWE-koder

### Datamodell-utvidelse

Nåværende CVE-modell utvides med valgfrie pakke-felter:

```
CVE (eksisterende)
  + source: "nvd" | "github" | "both"
  + packages: list[AffectedPackage]  (tom for rene NVD-CVE-er)

AffectedPackage (ny)
  - ecosystem: str       (npm, pip, maven, go, etc.)
  - name: str            (pakkenavn)
  - vulnerable_range: str (f.eks. "< 4.17.21")
  - patched_version: str | None
```

### Frontend-utvidelse

```
┌─────────────────────────────────────────────────┐
│ Nylige sikkerhetshull                           │
│ [Alle] [Supply chain] [Malware]    ← filter-tabs│
│                                                 │
│ CVE-ID | Beskrivelse | Pakker | CVSS | Alvl | Dato │
│ CVE-.. | ...         | npm:lodash <4.17 → 4.17 | 7.5 | HIGH | ... │
│ GHSA-. | ...         | pip:requests ≤2.28 → 2.29 | 6.1 | MED  | ... │
└─────────────────────────────────────────────────┘
```

---

## Krav

| ID | Krav | Verifiseringsmetode |
|----|------|---------------------|
| K1 | Backend SKAL hente advisories fra GitHub Advisory Database REST API (`type=reviewed` og `type=malware`) for siste 7 dager | Integrasjonstest: verifiser at respons inneholder GHSA-data |
| K2 | Backend SKAL parse pakke-informasjon: ecosystem, pakkenavn, vulnerable_version_range, first_patched_version | Integrasjonstest: verifiser at pakke-felter er populert |
| K3 | Backend SKAL slå sammen GitHub-data med NVD-data der CVE-ID matcher; advisories uten CVE-ID SKAL vises separat | Integrasjonstest: verifiser at sammenslåtte og separate oppføringer finnes |
| K4 | `GET /api/cves` SKAL støtte valgfri query-parameter `filter` med verdier: `all` (standard), `supply_chain`, `malware` | Integrasjonstest: kall med ulike filter-verdier, verifiser filtrering |
| K5 | Frontend SKAL vise filter-valg (tabs/knapper) for «Alle», «Supply chain», «Malware» | Manuell inspeksjon + integrasjonstest |
| K6 | Frontend SKAL vise pakke-informasjon (ecosystem:pakkenavn, sårbar versjon → patchet versjon) der det finnes | Manuell inspeksjon av frontend |
| K7 | GitHub Advisory-polling SKAL bruke samme periodiske mønster som NVD (hver 2. time) og cache i minne | Verifiser at GitHub-data er tilgjengelig etter oppstart |
| K8 | Backend SKAL håndtere GitHub API-feil gracefully — returnere cached data, ikke krasje | Integrasjonstest: simuler feil, verifiser respons |
| K9 | GitHub API-token SKAL leses fra miljøvariabel `GITHUB_TOKEN` (valgfri — fungerer uten, men med lavere rate limit) | Kode-review |
| K10 | Eksisterende NVD-funksjonalitet SKAL fungere uendret (regresjon) | Integrasjonstest: eksisterende /api/cves uten filter returnerer NVD-data |

---

## Integrasjonspunkter

| System | Type | Retning | Detaljer |
|--------|------|---------|----------|
| GitHub Advisory API | REST API | Utgående | Polling hver 2. time. Valgfri token via `GITHUB_TOKEN`. |
| NVD API 2.0 | REST API | Utgående | Uendret fra V1 |
| Nettleser | HTTP | Innkommende | Utvidet frontend med filter og pakke-kolonne |

---

## Risiko

| Risiko | Sannsynlighet | Konsekvens | Mottiltak |
|--------|--------------|------------|-----------|
| GitHub API rate limit (60/t uten token) | Middels | Stale data | Bruk token, poll sjelden (hver 2. time) |
| Cursor-basert paginering gir kompleksitet | Lav | Bug i paginering | Grundig testing |
| Mange advisories uten CVE-ID | Middels | Duplikater eller manglende kobling | Vis GHSA-ID som fallback-identifikator |
| Malware-advisories kan inneholde støy | Lav | Lav datakvalitet | `type=malware` er kuratert av GitHub |

---

## Videre arbeid

1. Bruker godkjenner denne analysen
2. Software-developer lager faset implementeringsplan basert på K1-K10
3. Implementering, code-review og testing per fase
