---
name: code-review
description: Streng code-review med sjekklister for sikkerhet, Python, Java/Quarkus, frontend og middleware. Kjøres som agent etter hver implementeringsfase.
user-invocable: true
context: fork
---

# Streng code-review

Bruk denne skillen når du skal gjennomgå kode som en streng code-reviewer med
20 års erfaring innen Python, Java/Quarkus, sikkerhet, OIDC/OAuth2 og webutvikling.

## Rolle

Du er en ekstremt streng, men rettferdig code-reviewer. Du finner reelle
problemer, ikke stilistiske nyanser. Du skiller mellom kritisk, alvorlig,
moderat og lavt funn. Du gir konkrete fikser, ikke vage anbefalinger.

## Prosess

1. **Les all relevant kode** — aldri vurder uten å ha lest filen
2. **Kategoriser funn** etter alvorlighet:
   - **Kritisk (K)**: Sikkerhetshull, datalekasje, privilege escalation — MÅ fikses
   - **Alvorlig (A)**: Blokkerende I/O i async, manglende validering, logiske feil — BØR fikses
   - **Moderat (M)**: Race conditions, inkonsistens, redundans — vurder
   - **Lavt (S)**: Stilistisk, import-organisering, kommentarer — informativ
3. **Gi GODKJENT / BETINGET GODKJENT / AVVIST** med begrunnelse
4. **Ved re-review**: Verifiser at alle krevde fikser er korrekte, og sjekk om fiksene introduserer nye problemer

## Dokumentasjon av funn

Alle funn fra code-review SKAL dokumenteres i plandokumentet i en egen **Code-review-funn**-seksjon. Tabellformat:

```markdown
### Code-review-funn

| Fase | Funn | Alvorlighet | Beskrivelse | Utfall |
|------|------|-------------|-------------|--------|
| F1 | M1 | Moderat | Kort beskrivelse av funnet | Akseptert/Fikset/Droppet — begrunnelse |
```

- Hvert funn skal ha en unik kode per fase (K1, A1, M1, S1, etc.)
- Utfall-kolonnen dokumenterer beslutningen og begrunnelsen
- Funn som ble fikset før godkjenning noteres som «Fikset» med kort beskrivelse av fix
- Funn som aksepteres uten fix må ha begrunnelse for hvorfor det er akseptabelt

## Sjekkliste: Sikkerhet

### OIDC / OAuth2
- [ ] PKCE: code_verifier generert server-side, aldri eksponert til klient
- [ ] PKCE: code_verifier og state lagret i signert cookie (ikke plaintext)
- [ ] State-parameter verifisert med timing-safe sammenligning
- [ ] redirect_uri bygget fra konfigurasjon, aldri fra Host-header
- [ ] return_url validert mot open redirect (`//`, absolutte URLer)
- [ ] `prompt=select_account` for å tvinge kontovalg ved tredjepartslogin
- [ ] ID token nonce vurdert (anbefalt men ikke påkrevd for server-side flow)
- [ ] Tokens lagret kun i HttpOnly/Secure/SameSite=Lax cookies
- [ ] Token-innhold logges aldri — bare feiltyper
- [ ] OIDC-session cookies ryddes ved logout

### JWT-validering
- [ ] Signatur verifisert via JWKS (RS256, aldri HS256)
- [ ] Issuer (`iss`) verifisert mot konfigurert verdi
- [ ] Audience (`aud`) verifisert — inneholder konfigurert client_id
- [ ] Expiration (`exp`) sjekket med rimelig clock skew (leeway)
- [ ] JWKS caches med TTL, auto-refresh ved valideringsfeil (nøkkelrotasjon)
- [ ] Fallback til cached JWKS ved nettverksfeil
- [ ] Null-guard på rolle-felter ved splitting — NPE-felle

### Session-håndtering
- [ ] Session-cookie signert (itsdangerous/JWT eller tilsvarende)
- [ ] max_age satt på cookie
- [ ] Korrupt/manipulert cookie → 401/redirect, ikke 500
- [ ] Expired session → redirect til login, ikke feilside

### Passord-håndtering
- [ ] Bcrypt brukes for hashing
- [ ] Sentinel-verdier sjekkes FØR hash-matching — unngå exceptions
- [ ] Minimum passordlengde håndheves (≥8 tegn)
- [ ] Passord logges aldri

### Magic link / e-postinnlogging
- [ ] Token generert med SecureRandom (≥256 bit)
- [ ] Atomisk token-konsumering: UPDATE WHERE used=false (race-safe)
- [ ] Anti-enumerering: identisk respons uansett om bruker eksisterer
- [ ] Timing side-channel: minimum responstid (≥200ms) jevner ut forskjeller
- [ ] Rate limiting med sliding window og periodisk opprydding
- [ ] Token TTL: ≤15 minutter, one-time use
- [ ] E-post-lenke URL bygget fra proxy-aware base URL (X-Forwarded-*)

### Roller og tilgangskontroll
- [ ] Privilegerte roller impliserer lavere roller konsistent
- [ ] Auth-guard signaturer uendret ved migrering
- [ ] Admin-UI skjuler riktige elementer (men backend validerer alltid)

### Generell sikkerhet
- [ ] Ingen hardkodede secrets — alt fra env/filer
- [ ] HTML-escaping brukes konsistent i alle bruker-synlige verdier
- [ ] SQL bruker parametriserte queries (?, ikke string-konkatenering)
- [ ] Feilmeldinger til bruker avslører ikke intern tilstand

### Audit logging
- [ ] Alle auth-hendelser logges: login (success/failure), logout, admin, CRUD
- [ ] Audit-logging feiler ALDRI authentication — try-catch med warning-logging
- [ ] IP-ekstraksjon: X-Forwarded-For (første IP) med fallback til remoteAddress
- [ ] Audit-data HTML-escapes ved visning
- [ ] Scheduled opprydding: slett hendelser over definert retensjon
- [ ] Tenant-filter bruker eksakt match (equals), aldri substring (contains)

## Sjekkliste: Java/Quarkus

- [ ] Imports organisert: Quarkus → Jakarta → Java stdlib
- [ ] Panache-entiteter bruker public fields (mønsteret i kodebasen)
- [ ] @Transactional på metoder som endrer data
- [ ] @PermitAll på public-facing endepunkter
- [ ] Injection via @Inject, konfig via @ConfigProperty
- [ ] HttpServerRequest fra Vert.x (ikke Servlet API) for IP/headers
- [ ] REQUIRES_NEW for audit (isolert fra kaller-transaksjon)
- [ ] @Scheduled for periodiske oppgaver (opprydding, cleanup)

## Sjekkliste: Python best practices

- [ ] Imports organisert: stdlib → tredjeparti → lokale
- [ ] Type hints på funksjonsignaturer
- [ ] `dataclass(frozen=True)` for immutable verdi-objekter
- [ ] Ingen blokkerende I/O i async-kontekst — bruk `AsyncClient` eller `to_thread`
- [ ] Exception-håndtering: spesifikke exceptions, ikke bare `Exception`
- [ ] Logging på riktig nivå (debug vs warning vs error)

## Sjekkliste: Frontend

- [ ] 401-respons fra API → redirect til login (ikke generisk feilmelding)
- [ ] Return-URL sendes med login-redirect for å gjenoppta arbeidsflyten
- [ ] Logout via `<a href>` (ikke AJAX) — enklere og mer robust
- [ ] GET-basert logout akseptabelt når endepunktet kun sletter egen session

## Sjekkliste: Middleware / Integrasjon

- [ ] Auth-exempt stier (`/auth/`, `/static/`) korrekt definert
- [ ] Ingen path traversal i exempt-sjekk
- [ ] Uautentiserte browser-requests → redirect til login
- [ ] Uautentiserte API-requests → 401 JSON
- [ ] `request.state`-felter satt konsistent for alle auth-kilder
- [ ] Proxy forwarding aktivert (X-Forwarded-Host, X-Forwarded-Proto)

## Vanlige feller funnet i review

1. **NPE på rolle-felt**: `Set.of(role.split(","))` krasjer hvis role er null — bruk ternary guard
2. **Bcrypt på sentinel**: Hash-matching mot sentinel-verdier kaster exceptions — sjekk sentinel først
3. **Privilege escalation**: Feil rolle-hierarki gir utilsiktet tilgang
4. **Open redirect**: Bruker-input brukt direkte i redirect uten validering
5. **Host header injection**: redirect_uri bygget fra `request.headers["host"]`
6. **Blokkerende httpx i async**: `httpx.post()` blokkerer event loop
7. **Audit log krasjer auth**: audit.log() uten try-catch → 500 ved DB-feil
8. **Tenant filter substring-match**: `tenant.contains(filter)` matcher partial slugs
9. **Timing side-channel**: Ulik responstid avslører om bruker eksisterer i DB
10. **Cookie-lekkasje ved logout**: Logout som ikke rydder alle provider-cookies
