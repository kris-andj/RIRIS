# 07 – Pregled projekta AvtoTrg

## Zagon aplikacije

Projekt sem zagnala lokalno po navodilih iz README:

1. `docker compose up -d` (PostgreSQL 18 v Dockerju)
2. virtualno okolje in `pip install -r requirements.txt`
3. `schema.sql` v bazo
4. `python seed.py`
5. `python run.py` → http://127.0.0.1:8000

Zagon je deloval brez težav. Seed ustvari 85 uporabnikov, 800 oglasov in 1500 ponudb, demo računi delujejo.

## Implementirane MVP funkcionalnosti

| Funkcionalnost | Stanje |
|---|---|
| F-01 Registracija, prijava in odjava | implementirano |
| F-02 Nadzorne plošče po vlogi | implementirano |
| F-03 Iskanje in filtriranje oglasov | implementirano |
| F-04 Oddaja ponudbe | implementirano |
| F-07 Upravljanje oglasov (prodajalec) | implementirano |
| F-08 Sprejem/zavrnitev ponudbe z auto-reject | implementirano |
| F-09 Življenjski cikel oglasa (aktivni → rezerviran → prodan) | implementirano |

Vse MVP funkcionalnosti iz `02-funkcionalnosti-in-obseg.md` so implementirane.

## Pregled uporabniških zgodb

### US-02 – Prijava in odjava ✅

- Prijava s pravilnimi podatki preusmeri na nadzorno ploščo glede na vlogo.
- Ob napačnem geslu se izpiše "Napačna e-pošta ali geslo.".
- Blokiran uporabnik se ne more prijaviti.
- Odjava prekine sejo.

Opomba: po odjavi aplikacija preusmeri na seznam oglasov (`/listings`), ne na prijavno stran, kot piše v kriteriju 5.

### US-04 – Iskanje in filtriranje ✅

- Iskanje po znamki in modelu deluje z delnim ujemanjem in ne loči velikih in malih črk ("bmw" najde BMW).
- Filter po gorivu in cenovnem razponu deluje.
- Rezultati so razvrščeni od najnovejših, 25 na stran.
- Filtri ostanejo ob prehodu na naslednjo stran.

### US-05 – Oddaja ponudbe ✅

- Ponudba z zneskom in sporočilom se shrani s statusom `pending`.
- Negativen znesek ali 0 vrne napako "Znesek mora biti pozitivno število.".
- Ponudbe ni mogoče oddati na oglas, ki ni `aktivni`, ali na lasten oglas.

### US-08 – Upravljanje lastnih oglasov ✅

- Letnik izven 1950 – (tekoče leto + 1) vrne napako.
- Negativna cena in negativni kilometri vrnejo napako.
- Prodajalec lahko ureja in briše samo svoje oglase.
- Prodanega oglasa ni mogoče urejati.

### US-10 – Sprejem ponudbe z auto-reject ✅

- Sprejeta ponudba dobi status `accepted`, ostale `pending` ponudbe na istem oglasu se samodejno prestavijo v `rejected`.
- Oglas preide v `rezerviran`, potem ga prodajalec lahko označi kot `prodan`.
- Zavrnitev posamezne ponudbe pusti oglas `aktivni`.
- Vse se izvede v eni transakciji, dodatno pa unikatni indeks v bazi prepreči dve sprejeti ponudbi na istem oglasu.

## Dokumentacija in ADR

Dokumentacija (zasnova, podatkovni model, arhitektura, uporabniške zgodbe, wireframi) je pregledna in se ujema z aplikacijo.

Pri ADR 0003 sem opazila razliko: odločitev pravi, da bo poslovna logika v ločenem `services/` sloju, v kodi pa te mape ni. Logika (npr. sprejem ponudbe z auto-reject) je napisana neposredno v routerjih (`backend/routers/seller.py`).

## Ugotovitve

- Vse MVP funkcionalnosti so implementirane in izbrane uporabniške zgodbe so izpolnjene.
- Manjša odstopanja: preusmeritev po odjavi in manjkajoč `services/` sloj iz ADR 0003.
- Projekt ni imel testov, linterja in CI/CD, zato sem to dodala v drugem delu naloge.