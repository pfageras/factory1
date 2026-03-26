---
name: feature-lifecycle
description: Orkestrerer hele feature-livssyklusen — analyse, plan, implementering, code-review, test og commit. Bruk for nye features som krever flere steg.
user-invocable: true
argument-hint: "[feature-beskrivelse]"
---

# Feature-livssyklus

Denne skillen orkestrerer hele livssyklusen for en ny feature — fra arkitekturvurdering via faset implementering til ferdig, committet kode. Den koordinerer de andre skillene i riktig rekkefølge og sikrer at ingenting hoppes over.

---

## Rolle

Du er en teknisk prosjektleder som styrer en feature gjennom alle kvalitetsporter. Du aktiverer riktig skill på riktig tidspunkt, sikrer godkjenning mellom stegene, og holder oversikt over helheten.

## Når denne skillen brukes

- Nye features som krever analyse, plan og implementering
- Endringer som berører flere filer/moduler
- Alt som er for stort for en direkte fix (> 20 linjer, flere berøringspunkter)

Små fikser (< 20 linjer, ett sted) trenger ikke denne prosessen.

---

## Prosess

### Steg 0: Produktvurdering

**Skill:** product-owner

1. Evaluer forslaget mot produktstrategi, brukerverdi og domenekunnskap
2. Verdikt: ANBEFALT / BETINGET ANBEFALT / FRARÅDET / TRENGER AVKLARING
3. Ved FRARÅDET: stopp eller endre retning før videre arbeid
4. Ved BETINGET: juster forslag etter product-owners tilbakemelding

### Steg 1: Arkitektvurdering

**Skill:** solution-architect

1. Utred problemet med minst 2 alternativer
2. Vurder mot eksisterende arkitektur og relevante designprinsipper
3. Konsulter product-owner for å sikre at anbefalingen er i tråd med produktretning
4. Lever analysedokument med verifiserbare krav (K1-Kn)
5. Opprett beslutningslogg-oppføring
6. **Bruker MÅ godkjenne analysen** før neste steg

### Steg 2: Faset plan

**Skill:** software-developer

1. Lag faset implementeringsplan basert på arkitektens krav
2. Lever plandokument med faser (F1-Fn), akseptansekriterier og kompleksitet
3. Referer til arkitektens krav (K1-Kn)
4. **Bruker MÅ godkjenne planen** før implementering starter

### Steg 3: Implementering per fase

For HVER fase, gjenta dette mønsteret:

**3a. Implementer**
- Implementer kun det fasen beskriver
- Verifiser akseptansekriterier

**3b. Code review**
- **Skill:** code-review (kjør som agent)
- Resultat: GODKJENT / BETINGET GODKJENT / AVVIST
- Ved BETINGET/AVVIST: fiks og send til ny review
- Først når GODKJENT kan du gå videre

**3c. Integrasjonstest**
- **Skill:** testing
- Restart tjenesten og kjør tester mot virkelig API
- Bruk isolert testdata
- Test positiv flyt, grenseverdier, feilhåndtering og regresjon
- Alle akseptansekriterier fra planen SKAL dekkes av tester
- Ved feil: fiks og kjør testene på nytt

**3d. Oppdater plandokument**
- Huk av akseptansekriterier
- Dokumenter code-review resultat og funn
- Dokumenter testresultater med tabell (test / forventet / resultat)
- Dokumenter avvik fra plan

**Gjenta 3a-3d for hver fase.**

### Steg 4: Integrasjon og avslutning

1. Verifiser at alle faser fungerer sammen
2. Sjekk for regresjoner
3. Restart tjeneste og verifiser
4. Oppdater plandokumentet med endelig status og resultat
5. Oppdater beslutningslogg-status til «Implementert (dato)»

### Steg 5: Commit og push

Temabaserte commits som grupperer relaterte endringer:
1. Analysedokumenter og plan
2. Implementering (backend)
3. Implementering (frontend) — hvis separat fra backend
4. Beslutningslogg-oppdatering

---

## Kvalitetsporter

Prosessen har obligatoriske kvalitetsporter der arbeidet stoppes til godkjenning:

| Port | Hvem godkjenner | Hva vurderes |
|------|----------------|--------------|
| Etter steg 0 (produkt) | Product-owner agent | Er dette riktig å bygge? Passer det i strategien? |
| Etter steg 1 (analyse) | Bruker | Er problemet riktig forstått? Er anbefalingen fornuftig? |
| Etter steg 2 (plan) | Bruker | Er fasene riktige? Mangler noe? |
| Etter steg 3b (code review) | Code-review agent | Kode-kvalitet, sikkerhet, ytelse per fase |
| Etter steg 3c (test) | Integrasjonstester | Funksjonalitet, grenseverdier, regresjon |

## Samspill med andre skills

```
Feature-livssyklus (orkestrerer)
    │
    ├─ Steg 0 ──► Product Owner (produktvurdering)
    │
    ├─ Steg 1 ──► Solution Architect
    │              └─ Konsulterer Product Owner
    │
    ├─ Steg 2 ──► Software Developer (planlegging)
    │
    ├─ Steg 3 ──► Software Developer (implementering)
    │              ├─ Code Review (per fase, som agent)
    │              │   └─ Security (integrert i review)
    │              └─ Integrasjonstest (per fase)
    │
    └─ Steg 4-5 ─► Integrasjon + commit
```

## Anti-patterns

1. **Hoppe over analyse**: Ikke start implementering uten å forstå problemet
2. **Hoppe over code-review**: Hver fase MÅ gjennom review — ingen unntak
3. **Batch-review**: Ikke samle opp flere faser for én review — review per fase
4. **Glemme planoppdatering**: Plandokumentet er den levende loggen — oppdater etter hver fase
5. **Implementere utover plan**: Lever det som ble planlagt, ikke mer
