from .test_main import *


def test_search_api(client):
    response = client.get(
        "/search?data=2000",
    )
    assert response.status_code == 200
    response = json.loads(response.text)
    assert response[0]["release_year"] == 2000
