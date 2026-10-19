import httpx
from src.parcel import create_label


def test_shipping_preserves_package_and_weight(monkeypatch):
    def post(url, *, json):
        assert url == "https://parcel.example.test/labels/create"
        assert json == {"package_id": "p-1", "weight_grams": 2501}
        return httpx.Response(200, json={"label_id": "label-1"}, request=httpx.Request("POST", url))
    monkeypatch.setattr(httpx, "post", post)
    assert create_label("p-1", 2501) == {"label_id": "label-1"}
