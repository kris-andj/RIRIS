from backend.models import Listing, Offer

from .conftest import (
    prijava,
    ustvari_oglas,
    ustvari_ponudbo,
    ustvari_uporabnika,
)


def test_domaca_stran_preusmeri_na_oglase(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/listings"


def test_prijava_z_napacnim_geslom(client, db):
    ustvari_uporabnika(db, "kupec@test.si")
    r = prijava(client, "kupec@test.si", "napacno")
    assert r.headers["location"] == "/auth/login"
    assert "Napačna e-pošta ali geslo." in client.get("/auth/login").text


def test_prijava_in_odjava(client, db):
    ustvari_uporabnika(db, "kupec@test.si")
    r = prijava(client, "kupec@test.si")
    assert r.headers["location"] == "/"
    assert client.get("/buyer/dashboard").status_code == 200
    client.post("/auth/logout")
    r = client.get("/buyer/dashboard", follow_redirects=False)
    assert r.headers["location"] == "/auth/login"


def test_blokiran_uporabnik_se_ne_more_prijaviti(client, db):
    ustvari_uporabnika(db, "blok@test.si", blokiran=True)
    prijava(client, "blok@test.si")
    r = client.get("/buyer/dashboard", follow_redirects=False)
    assert r.status_code == 303


def test_kupec_nima_dostopa_do_prodajalca(client, db):
    ustvari_uporabnika(db, "kupec@test.si")
    prijava(client, "kupec@test.si")
    assert client.get("/seller/dashboard").status_code == 403


def test_iskanje_ne_loci_velikih_crk(client, db):
    prodajalec = ustvari_uporabnika(db, "prod@test.si", role="seller")
    ustvari_oglas(db, prodajalec, make="BMW", model="X5")
    ustvari_oglas(db, prodajalec, make="Renault", model="Clio")
    r = client.get("/listings", params={"q": "bmw"})
    assert "X5" in r.text
    assert "Clio" not in r.text


def test_api_vrne_samo_aktivne_oglase(client, db):
    prodajalec = ustvari_uporabnika(db, "prod@test.si", role="seller")
    ustvari_oglas(db, prodajalec, model="Aktiven")
    ustvari_oglas(db, prodajalec, model="Prodan", status="prodan")
    data = client.get("/api/listings").json()
    assert data["total"] == 1
    assert data["listings"][0]["model"] == "Aktiven"


def test_kupec_odda_ponudbo(client, db):
    prodajalec = ustvari_uporabnika(db, "prod@test.si", role="seller")
    ustvari_uporabnika(db, "kupec@test.si")
    oglas = ustvari_oglas(db, prodajalec)
    prijava(client, "kupec@test.si")
    client.post(
        f"/listings/{oglas.id}/offers",
        data={"amount_eur": "14500", "message": "Pozdravljeni"},
    )
    ponudba = db.query(Offer).one()
    assert ponudba.status == "pending"
    assert int(ponudba.amount_eur) == 14500


def test_negativna_ponudba_se_zavrne(client, db):
    prodajalec = ustvari_uporabnika(db, "prod@test.si", role="seller")
    ustvari_uporabnika(db, "kupec@test.si")
    oglas = ustvari_oglas(db, prodajalec)
    prijava(client, "kupec@test.si")
    client.post(f"/listings/{oglas.id}/offers", data={"amount_eur": "-10"})
    assert db.query(Offer).count() == 0


def test_prodajalec_ne_more_objaviti_oglasa_z_napacnim_letnikom(client, db):
    ustvari_uporabnika(db, "prod@test.si", role="seller")
    prijava(client, "prod@test.si")
    client.post(
        "/seller/listings/new",
        data={
            "make": "Fiat", "model": "Punto", "year": "1900", "mileage_km": "1000",
            "fuel": "bencin", "transmission": "ročni", "price_eur": "3000",
        },
    )
    assert db.query(Listing).count() == 0


def test_prodajalec_objavi_oglas(client, db):
    ustvari_uporabnika(db, "prod@test.si", role="seller")
    prijava(client, "prod@test.si")
    client.post(
        "/seller/listings/new",
        data={
            "make": "Fiat", "model": "Punto", "year": "2015", "mileage_km": "90000",
            "fuel": "bencin", "transmission": "ročni", "price_eur": "5000",
        },
    )
    oglas = db.query(Listing).one()
    assert oglas.status == "aktivni"


def test_sprejem_ponudbe_samodejno_zavrne_ostale(client, db):
    prodajalec = ustvari_uporabnika(db, "prod@test.si", role="seller")
    kupec1 = ustvari_uporabnika(db, "k1@test.si")
    kupec2 = ustvari_uporabnika(db, "k2@test.si")
    oglas = ustvari_oglas(db, prodajalec)
    p1 = ustvari_ponudbo(db, oglas, kupec1, 14000)
    p2 = ustvari_ponudbo(db, oglas, kupec2, 13500)
    prijava(client, "prod@test.si")
    client.post(f"/seller/offers/{p1.id}/accept")
    db.expire_all()
    assert db.get(Offer, p1.id).status == "accepted"
    assert db.get(Offer, p2.id).status == "rejected"
    assert db.get(Listing, oglas.id).status == "rezerviran"


def test_zavrnitev_pusti_oglas_aktiven(client, db):
    prodajalec = ustvari_uporabnika(db, "prod@test.si", role="seller")
    kupec = ustvari_uporabnika(db, "k1@test.si")
    oglas = ustvari_oglas(db, prodajalec)
    p = ustvari_ponudbo(db, oglas, kupec)
    prijava(client, "prod@test.si")
    client.post(f"/seller/offers/{p.id}/reject")
    db.expire_all()
    assert db.get(Offer, p.id).status == "rejected"
    assert db.get(Listing, oglas.id).status == "aktivni"


def test_prodan_samo_iz_rezerviranega(client, db):
    prodajalec = ustvari_uporabnika(db, "prod@test.si", role="seller")
    aktiven = ustvari_oglas(db, prodajalec, model="A")
    rezerviran = ustvari_oglas(db, prodajalec, model="B", status="rezerviran")
    prijava(client, "prod@test.si")
    client.post(f"/seller/listings/{aktiven.id}/sold")
    client.post(f"/seller/listings/{rezerviran.id}/sold")
    db.expire_all()
    assert db.get(Listing, aktiven.id).status == "aktivni"
    assert db.get(Listing, rezerviran.id).status == "prodan"
