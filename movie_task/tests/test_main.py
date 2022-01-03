import json
import uuid
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from .. import main, dependencies

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@sa.event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    dbapi_connection.isolation_level = None


@pytest.fixture()
def session():
    connection = engine.connect()
    session = TestingSessionLocal(bind=connection)

    yield session
    session.close()
    connection.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    main.app.dependency_overrides[dependencies.get_db] = override_get_db
    yield TestClient(main.app)
    del main.app.dependency_overrides[dependencies.get_db]


HEADERS = {"accept": "application/json", "Content-Type": "application/json"}

USERNAME = str(uuid.uuid4())
PASSWORD = str(uuid.uuid4())
EMAIL = str(uuid.uuid4()) + "@gmail.com"


def test_user_register(client):
    payload = {
        "password": PASSWORD,
        "email": "josh@gmail.com",
        "first_name": str(uuid.uuid4()),
        "last_name": str(uuid.uuid4()),
    }

    response = client.post(
        "/users",
        headers=HEADERS,
        json=payload,
    )
    response = json.loads(response.text)
    assert response["email"] == "josh@gmail.com"


def test_user_register_with_missing_field(client):
    payload = {
        "email": str(uuid.uuid4()),
        "first_name": str(uuid.uuid4()),
        "last_name": str(uuid.uuid4()),
    }

    response = client.post(
        "/api/v1/register",
        headers=HEADERS,
        json=payload,
    )
    response = json.loads(response.text)

    assert response["detail"] == "Not Found"


def test_login_with_wrong_credentails(client):
    HEADERS["Content-Type"] = "application/x-www-form-urlencoded"

    data = {
        "grant_type": "",
        "username": str(uuid.uuid4()),
        "password": str(uuid.uuid4()),
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    response = client.post(
        "/api/v1/login",
        headers=HEADERS,
        json=data,
    )
    response = json.loads(response.text)
    assert response["detail"] == "Not Found"


def test_get_user_token(client):
    HEADERS["Content-Type"] = "application/x-www-form-urlencoded"

    data = {
        "grant_type": "",
        "username": "josh@gmail.com",
        "password": PASSWORD,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    response = client.post(
        "/login",
        headers=HEADERS,
        data=data,
    )
    response = json.loads(response.text)
    HEADERS["Authorization"] = "Bearer {}".format(response["access_token"])
    HEADERS["Content-Type"] = "application/json"
    return response["access_token"]


def test_forgot_password(client):
    header_new = {"accept": "application/json"}
    response = client.post(
        "/forgetPass?email=josh@gmail.com", headers=header_new)
    response = json.loads(response.text)
    assert response["message"] == 'email has been sent'


def test_get_users_data(client):
    response = client.get("/users")
    assert response.status_code == 200
    response = json.loads(response.text)
    assert response[0]["id"] > 0


def test_user_with_id(client):
    response = client.get("/users/1")
    assert response.status_code == 200
    response = json.loads(response.text)
    assert response["id"] == 1


def test_user_moveis(client):
    data = {
        "name": USERNAME,
        "release_year": 2021,
        "genres": "string"
    }
    response = client.post(
        "/users/movies",
        headers=HEADERS,
        json=data,
    )
    assert response.status_code == 200
    response = json.loads(response.text)
    assert response["name"] == data["name"]


def test_delete_user(client):
    response = client.delete(
        "/delete/user",
        headers=HEADERS,
    )
    assert response.status_code == 200
    response = json.loads(response.text)
    assert response["detail"] == "successfull deleted"


def test_get_movie_detail_with_wrong_credential(client):
    response = client.get(
        "/movies/123",
    )
    assert response.status_code == 404


def test_delete_movie_with_worng_id(client):
    response = client.delete(
        "/movies/123",
    )
    assert response.status_code == 404


def test_edit_movie_data(client):
    data = {
        "name": "string",
        "release_year": 2000,
        "genres": "string"
    }
    response = client.put(
        "/movies/1",
        json=data
    )
    assert response.status_code == 200
