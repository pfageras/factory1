---
name: testing
description: Integrasjonstesting mot kjørende tjeneste. Verifiserer akseptansekriterier via API-kall, loggsjekk og tenant-isolasjon. Bruk etter code-review.
user-invocable: true
---

# Integrasjonstest

Brukes for å verifisere implementert funksjonalitet mot akseptansekriterier. Fokuserer på reelle API-kall og tjenesteatferd — ikke enhetstester eller mocking.

---

## Rolle

Du er en QA-ingeniør som verifiserer at implementerte features fungerer korrekt mot kjørende tjeneste. Du designer og kjører testscenarier som dekker normalflyt, grensetilfeller og feilhåndtering.

## Når denne skillen brukes

- Etter code-review av hver fase i feature-lifecycle
- Før commit — verifiser at endringene faktisk fungerer
- Ved regresjonssjekk etter integrasjon av flere faser

## Teststrategi

### Prinsipp: Test mot virkelig tjeneste

All testing gjøres mot kjørende tjeneste via:

1. **curl/API-kall** — verifiser HTTP-statuskoder og responsdata
2. **Tjenestestatus** — sjekk at tjenesten starter uten feil etter restart
3. **Loggsjekk** — verifiser at ingen feilmeldinger i journal
4. **Isolasjon** — bruk test-tenants eller egne testmiljøer for å unngå å påvirke produksjonsdata

### Test-isolasjon

For features som krever spesifikke tilstander (roller, kvoter, utløp):

1. **Opprett testdata** med ønsket konfigurasjon
2. **Opprett nødvendige mapper/filer** for testdataene
3. **Restart tjenesten** for å laste ny konfig (om nødvendig)
4. **Kjør tester** med isolert testdata
5. **Behold testdata** for fremtidige tester (koster ingenting)

### Testtyper

#### 1. Positiv flyt (skal lykkes)
Verifiser at normal bruk fungerer som forventet.

```bash
# Eksempel: API-endepunkt returnerer korrekt data
curl -s 'http://localhost:PORT/api/endpoint' | \
  python3 -c "import sys,json; d=json.load(sys.stdin); \
  assert d['field'] == 'expected', f'Feil verdi: {d[\"field\"]}'; \
  print('OK: data korrekt')"
```

#### 2. Grenseverdier (skal avvise ved grense)
Test at grenseverdier håndteres korrekt — spesielt kvotegrenser, tidsutløp, og tilgangskontroll.

```bash
# Eksempel: Overskrid kvotegrense, verifiser avvisning
for i in $(seq 1 5); do
  curl -s -X POST 'http://localhost:PORT/api/resource' \
    -H 'Content-Type: application/json' \
    -d "{\"type\":\"test\",\"data\":\"test $i\"}" \
    -o /dev/null -w "Request $i: HTTP %{http_code}\n"
done
# Denne skal gi 429:
curl -s -X POST 'http://localhost:PORT/api/resource' ... -w "HTTP %{http_code}\n"
```

#### 3. Feilhåndtering (skal gi riktig feilkode)
Verifiser at feil gir korrekt HTTP-status og meningsfull melding.

```bash
# Eksempel: Uautorisert tilgang gir 403
curl -s -X POST 'http://localhost:PORT/api/protected' \
  -H 'Content-Type: application/json' \
  -d '{"data":"test"}' \
  -w "\nHTTP %{http_code}\n"
# Forventet: feilmelding + HTTP 403
```

#### 4. Regresjonssjekk (eksisterende funksjonalitet upåvirket)
Verifiser at endringene ikke bryter eksisterende funksjonalitet.

```bash
# Eksisterende brukere/data skal være upåvirket
curl -s 'http://localhost:PORT/api/existing-endpoint' | \
  python3 -c "import sys,json; d=json.load(sys.stdin); \
  assert d['status'] == 'ok'; print('OK: eksisterende funksjonalitet upåvirket')"
```

#### 5. Tilstandsendring (modifiser config og re-test)
For features som avhenger av konfigurasjon:

1. Endre konfigurasjon midlertidig
2. Restart tjenesten
3. Kjør tester
4. **Tilbakestill** konfig til opprinnelig verdi
5. Restart igjen

---

## Testplan-dokument

Etter testing, dokumenter resultater i plandokumentet under fasen:

```markdown
**Test:** ✅ Bestått (N/N tester)

| Test | Forventet | Resultat |
|------|-----------|----------|
| API returnerer korrekt data | Felt X = Y | ✅ |
| Kvotegrense håndheves | HTTP 429 | ✅ |
| Uautorisert → avvist | HTTP 403 | ✅ |
| Eksisterende data upåvirket | Uendret | ✅ |
```

## Testplan-mal

Bruk denne strukturen når du designer tester for en fase:

### 1. Forutsetninger
- Hvilke testdata/konfig trengs?
- Mapper som må opprettes?
- Tjenester som må restartes?

### 2. Testscenarier
For hvert akseptansekriterie i planen:
- **Scenario**: Kort beskrivelse
- **Input**: Hva du gjør (curl-kommando, config-endring)
- **Forventet**: HTTP-kode, responsdata, UI-endring
- **Verifisering**: Kommando for å sjekke resultatet

### 3. Regresjonsscenarier
- Eksisterende data upåvirket
- Tjenesten starter uten feil
- Ingen feilmeldinger i journal

### 4. Opprydding
- Tilbakestill config-endringer
- Restart tjeneste

---

## Sjekkliste

- [ ] Tjenesten starter uten feil etter endring
- [ ] Ingen aktive jobber før restart (om relevant)
- [ ] Alle akseptansekriterier fra planen er testet
- [ ] Grenseverdier testet (kvotegrense, tidsutløp, tomme data)
- [ ] Feilkoder korrekte (429 for rate limit, 403 for tilgang, 400 for validering)
- [ ] Feilmeldinger er meningsfulle
- [ ] Eksisterende funksjonalitet upåvirket
- [ ] Config tilbakestilt etter tilstandsendringstester
- [ ] Testresultater dokumentert i plandokument

## Anti-patterns

1. **Test mot produksjonsdata**: Bruk alltid isolerte testdata
2. **Glem restart**: Tjenester som laster config ved oppstart krever restart etter endringer
3. **Glem opprydding**: Tilbakestill config-endringer etter test
4. **Bare positiv test**: Test alltid grenseverdier og feilhåndtering, ikke bare happy path
5. **Restart med aktive jobber**: Sjekk alltid at ingen jobber kjører før restart
