---
name: privacy-gdpr
description: GDPR og personvern-ekspertise. Rettslig grunnlag, DPA-vurdering, DPIA, og sjekklister for databehandling. Bruk ved personopplysninger eller nye dataflyter.
user-invocable: true
---

# Personvern og GDPR

Bruk denne kompetansen ved GDPR-vurderinger, DPA-spørsmål, personvernkonsekvensvurderinger (DPIA), og juridisk analyse av databehandling.

---

## Rolleforståelse: Controller vs. processor

Avklar tidlig om virksomheten opptrer som **behandlingsansvarlig** (controller) eller **databehandler** (processor) for den aktuelle behandlingen. Skillet styrer hvilke plikter som gjelder.

### Indikatorer på controller-rolle
1. **Selvstendig metodevalg** — virksomheten bestemmer kilder, metoder og presentasjon
2. **Ingen kundedata mottas** — kunden bestiller en tjeneste, ikke databehandling
3. **Offentlige kilder** — informasjon hentes fra offentlig tilgjengelige kilder

### Konsekvens

- **DPA med kunder:** Kun påkrevd når virksomheten behandler kundens personopplysninger (processor-rolle)
- **DPA med AI-leverandører:** Virksomhetens eget ansvar som controller
- **Rettslig grunnlag:** Virksomhetens eget valg basert på behandlingens art

---

## Rettslig grunnlag: Vanlige alternativer

### Alternativ A: Journalistisk/analytisk unntak (Personopplysningsloven §3)

Sterkeste posisjon for analyse- og informasjonsvirksomhet. §3 unntar behandling som «utelukkende skjer for journalistiske, akademiske, kunstneriske eller litterære formål.» EU-domstolens rettspraksis:

- **Satakunnan Markkinapörssi (C-73/07):** Automatisert innsamling/publisering av offentlige data kan være journalistisk virksomhet
- **Buivids (C-345/17):** Vidt tolkningsrom — enhver aktivitet som formidler informasjon til allmennheten

### Alternativ B: Berettiget interesse — artikkel 6(1)(f)

Solid alternativ. Tre-trinns test:

1. **Legitim interesse:** Virksomhetens formål er legitimt
2. **Nødvendighet:** Behandlingen er nødvendig for formålet
3. **Balansetest:** Virksomhetens interesse veies mot den registrertes:
   - Er informasjonen allerede offentlig tilgjengelig?
   - Omtales personene i kraft av offentlige roller?
   - Tilfører behandlingen analyse, ikke ny eksponering?
   - Rimelig forventning: forventer de registrerte å bli analysert?

### Alternativ C: Samtykke — artikkel 6(1)(a)

Nødvendig når ingen andre grunnlag passer. Krav:
- Frivillig, spesifikt, informert og utvetydig
- Lett å trekke tilbake
- Dokumenterbart

---

## DPA vs. tjenesteavtale — beslutningstre

```
Mottar virksomheten kundens egne personopplysninger?
  ├── Ja → Virksomheten er databehandler → DPA kreves (art. 28)
  └── Nei → Kunden bestiller en tjeneste
        ├── Virksomheten bestemmer metode selvstendig?
        │     └── Ja → Selvstendig controller → Tjenesteavtale
        └── Kunden instruerer i detalj?
              └── Ja → Mulig felles behandlingsansvar (art. 26) → Fellesavtale
```

---

## Personopplysninger fra offentlige kilder

At informasjonen er offentlig tilgjengelig endrer IKKE klassifiseringen som personopplysninger (art. 4(1)). Men det påvirker:

- **Balansetesten** under berettiget interesse — enklere å bestå
- **Informasjonsplikten** — kan fravikes der det er uforholdsmessig (art. 14(5)(b))
- **Innsynsretten** — gjelder fortsatt, men journalistunntaket kan frita

### Risikokategorisering av behandlingstyper

| Risiko | Behandlingstyper | Merknad |
|--------|-----------------|---------|
| Lav | Selskapsanalyse, bransjetrender, markedsdata | Ingen direkte personprofiler |
| Moderat | Analyser som nevner navngitte offentlige personer | Kontekstuell omtale |
| Høyere | Direkte profilering av enkeltpersoner | Vurdér DPIA |

---

## AI-verktøy — juridisk vurdering

Virksomheten som selvstendig controller velger sine egne verktøy. Vurder:

| Faktor | CLI/Desktop-verktøy | API med DPA |
|--------|---------------------|-------------|
| Juridisk forsvarlig? | Avhenger av datatype | **Ja** — med DPA |
| Treningsrisiko | Les vilkårene nøye | Garantert nei (standard DPA) |
| Beste praksis? | Akseptabelt for ikke-sensitiv data | **Ja** |
| Kostnad | Flat abonnement | Per-bruk |

**Tommelregel:** For offentlige, ikke-sensitive data er begge forsvarlige. For personopplysninger foretrekk API med DPA.

---

## DPIA-krav (personvernkonsekvensvurdering)

GDPR artikkel 35(3) krever DPIA ved:
- **(a)** Systematisk og omfattende vurdering av personlige aspekter (profilering)
- **(b)** Stor skala behandling av sensitive kategorier
- **(c)** Systematisk overvåking av offentlig tilgjengelig område

Direkte profilering av navngitte personer kan utløse **(a)**. Gjennomfør DPIA for slike behandlinger.

---

## Sjekkliste: Ny GDPR-vurdering

```
[ ] Identifiser behandlingen — hva, hvem, hvorfor
[ ] Rollefordeling — er virksomheten controller eller processor?
[ ] Rettslig grunnlag — §3 (journalistisk), art. 6(1)(f) (berettiget interesse), eller annet
[ ] Offentlige vs. ikke-offentlige kilder — påvirker balansetest, ikke klassifisering
[ ] DPIA nødvendig? — profilering og direkte personvurdering: ja
[ ] Informasjonsplikt — personvernerklæring dekkende?
[ ] Lagringsperioder — definert og dokumentert?
[ ] Sikkerhetstiltak — dokumentert?
[ ] DPA med underleverandører — nødvendig for databehandlere?
```

---

## Referanser

- GDPR artikkel 4 (definisjoner), 6 (rettslig grunnlag), 28 (databehandler), 30 (protokoll), 35 (DPIA)
- Personopplysningsloven §3 (journalistisk unntak)
- C-73/07 Satakunnan Markkinapörssi (offentlige data som journalistikk)
- C-345/17 Buivids (vid tolkning av journalistisk formål)
- Datatilsynets veileder om berettiget interesse
