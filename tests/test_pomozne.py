from decimal import Decimal

from backend.models import hash_password, verify_password
from backend.settings import EMAIL_RE, parse_int, parse_money, valid_listing_form


def veljaven_oglas(**spremembe):
    polja = {
        "make": "Škoda",
        "model": "Octavia",
        "year": "2019",
        "mileage_km": "85000",
        "fuel": "dizel",
        "transmission": "ročni",
        "price_eur": "14990",
    }
    polja.update(spremembe)
    return polja


def test_parse_money_celo_stevilo():
    assert parse_money("12990") == Decimal("12990")


def test_parse_money_slovenski_zapis():
    assert parse_money("12.990,50") == Decimal("12990.50")


def test_parse_money_neveljaven_niz():
    assert parse_money("abc") is None


def test_parse_int():
    assert parse_int(" 42 ") == 42
    assert parse_int("x") is None


def test_veljaven_oglas_nima_napake():
    assert valid_listing_form(veljaven_oglas()) is None


def test_oglas_prestar_letnik():
    assert "Letnik" in valid_listing_form(veljaven_oglas(year="1900"))


def test_oglas_negativna_cena():
    assert "Cena" in valid_listing_form(veljaven_oglas(price_eur="-100"))


def test_oglas_negativni_kilometri():
    assert "kilometri" in valid_listing_form(veljaven_oglas(mileage_km="-5"))


def test_oglas_neveljavno_gorivo():
    assert valid_listing_form(veljaven_oglas(fuel="para")) == "Neveljavno gorivo."


def test_geslo_hash_in_preverjanje():
    h = hash_password("skrivnost123")
    assert h != "skrivnost123"
    assert verify_password("skrivnost123", h)
    assert not verify_password("napacno", h)


def test_email_regex():
    assert EMAIL_RE.match("kupec@avtotrg.si")
    assert not EMAIL_RE.match("ni-email")

    