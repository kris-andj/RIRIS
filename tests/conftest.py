import os
from pathlib import Path

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://avtotrg:avtotrg@localhost:5433/avtotrg_test",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app import app
from backend.models import Listing, Offer, User, hash_password
from backend.settings import engine, now_utc

SCHEMA = Path(__file__).resolve().parent.parent / "schema.sql"


@pytest.fixture(scope="session", autouse=True)
def pripravi_bazo():
    if not engine.url.database.endswith("_test"):
        pytest.exit("Testi se lahko izvajajo samo na testni bazi (ime se konca z _test).")
    with engine.begin() as conn:
        conn.exec_driver_sql(SCHEMA.read_text(encoding="utf-8"))
    yield


@pytest.fixture(autouse=True)
def pocisti_bazo():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE offers, listings, users RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def db():
    with Session(engine) as session:
        yield session


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def ustvari_uporabnika(db, email, role="buyer", geslo="geslo1234", blokiran=False):
    user = User(
        email=email,
        password_hash=hash_password(geslo),
        full_name=email.split("@")[0],
        city="Maribor",
        role=role,
        is_dealer=False,
        is_blocked=blokiran,
        created_at=now_utc(),
    )
    db.add(user)
    db.commit()
    return user


def ustvari_oglas(db, prodajalec, make="BMW", model="320d", cena=15000, status="aktivni"):
    listing = Listing(
        seller_id=prodajalec.id,
        make=make,
        model=model,
        year=2018,
        mileage_km=120000,
        fuel="dizel",
        transmission="ročni",
        price_eur=cena,
        status=status,
        created_at=now_utc(),
        updated_at=now_utc(),
    )
    db.add(listing)
    db.commit()
    return listing


def ustvari_ponudbo(db, oglas, kupec, znesek=14000):
    offer = Offer(
        listing_id=oglas.id,
        buyer_id=kupec.id,
        amount_eur=znesek,
        status="pending",
        created_at=now_utc(),
    )
    db.add(offer)
    db.commit()
    return offer


def prijava(client, email, geslo="geslo1234"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": geslo},
        follow_redirects=False,
    )

