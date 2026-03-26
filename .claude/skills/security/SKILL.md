---
name: security
description: Sikkerhetsregler og sjekklister for webapplikasjoner. Auth, HTML-escape, SQL-injeksjon, filsti-validering, subprocess-sikkerhet. Referanse for alle agenter.
user-invocable: false
---

# Sikkerhets-skills

Obligatoriske sikkerhetsregler og sjekklister for alle utviklingsoppgaver.

---

## Obligatoriske regler

Disse gjelder ALL kode. Brudd = sikkerhetsfeil.

### 1. Auth på alle nye endepunkter

Nye API-endepunkter MÅ ha eksplisitt auth-sjekk:
- Muterende operasjoner → krever admin-rolle
- Sensitive lese-operasjoner → krever autentisering
- Kun read-only offentlige endepunkter (health, status) kan stå uten

**Bakgrunn:** Debug-endepunkter uten auth kan lekke tokens og headers.

### 2. HTML-escape all brukerdata i HTML-kontekst

All data fra bruker eller database som settes inn i HTML MÅ escapes.
Gjelder også data som "bare" admins kan sette.

```python
# RIKTIG
from html import escape as html_escape
parts.append(f"<b>Notat:</b> {html_escape(row['comment'])}")

# FEIL
parts.append(f"<b>Notat:</b> {row['comment']}")
```

### 3. Parameterisert SQL — alltid

```python
# RIKTIG
conn.execute("SELECT * FROM t WHERE x = ?", (val,))

# FEIL
conn.execute(f"SELECT * FROM t WHERE x = '{val}'")
```

Dynamiske `IN()`-klausuler: bruk tellingskontrollerte placeholders.
```python
placeholders = ",".join("?" * len(items))
conn.execute(f"SELECT * FROM t WHERE x IN ({placeholders})", items)
```

### 4. Filstier — valider mot path traversal

Alle filnavn fra brukerinput MÅ valideres mot path traversal:
```python
# Eksempel: resolv og sjekk at stien er innenfor tillatt mappe
resolved = base_dir.joinpath(filename).resolve()
if not resolved.is_relative_to(base_dir):
    raise ValueError("Path traversal attempt")
```

### 5. Subprocess — aldri shell=True

```python
# RIKTIG
await asyncio.create_subprocess_exec("cmd", arg1, arg2)

# FEIL
await asyncio.create_subprocess_shell(f"cmd {arg1} {arg2}")
```

Listebasert exec er primærforsvaret mot kommandoinjeksjon.

### 6. Tjenester binder til localhost

Alle nye tjenester (uvicorn, Docker, etc.) SKAL binde til `127.0.0.1`.
```yaml
# Docker — RIKTIG
ports: ["127.0.0.1:8080:80"]

# Docker — FEIL
ports: ["8080:80"]  # Eksponerer på 0.0.0.0
```

### 7. Ingen hemmeligheter i kode

API-nøkler, passord og tokens hører hjemme i:
- Miljøvariabler (via systemd service-filer eller .env)
- Filer med begrenset tilgang (chmod 600)
- Aldri i kildekode, aldri i git

---

## Sjekklister

### Nytt endepunkt

```
[ ] Auth-sjekk satt? (admin / autentisert / bevisst offentlig)
[ ] Brukerinput validert? (filnavn → path-validering, SQL → parameterisert, HTML → escaped)
[ ] Returnerer sensitiv info? (e-poster, stier, nøkler = nei)
[ ] Muterende operasjon logget i audit?
```

### Ny tjeneste / infrastruktur

```
[ ] Binder til 127.0.0.1?
[ ] Lagt til i backup-rutiner?
[ ] Reverse proxy / tunnel-rute korrekt?
[ ] Filrettigheter: 600 for secrets, 700 for sensitive mapper
[ ] Lagt til i healthcheck?
```

### E-post / HTML-output

```
[ ] Brukerdata escaped med html.escape()?
[ ] Egne HTML-tags (b, br, div) ikke escaped — bare verdier
[ ] Subject sanitert?
```

---

## Anti-mønstre

| Gjør IKKE dette | Konsekvens | Gjør dette i stedet |
|-----------------|-----------|---------------------|
| Endepunkt uten auth-sjekk | Info-lekkasje, uautorisert mutasjon | Eksplisitt auth-dependency |
| `innerHTML = userdata` uten escaping | XSS | `escapeHtml()` eller `textContent` |
| `f"WHERE x = '{val}'"` | SQL-injeksjon | `"WHERE x = ?"` med parametre |
| `shell=True` i subprocess | Kommandoinjeksjon | `create_subprocess_exec()` |
| Docker `ports: ["8080:80"]` | LAN-eksponering | `"127.0.0.1:8080:80"` |
| Hemmeligheter i kildekode | Credential-lekkasje | Miljøvariabler / secrets-filer |
| Database uten backup | Datatap | Automatiserte backup-rutiner |
| Logger uten rotasjon | Diskfylling | `RotatingFileHandler` eller tilsvarende |
