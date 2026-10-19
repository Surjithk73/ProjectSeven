import httpx

API_URL = "https://parcel.example.test"


def create_label(package_id, weight_grams):
    """Business Intent: Create a label preserving package and gram weight."""
    response = httpx.post(f"{API_URL}/labels", json={"package_id": package_id, "weight_grams": weight_grams})
    response.raise_for_status()
    return response.json()
