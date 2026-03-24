import httpx
from config import LMS_API_URL, LMS_API_KEY


def _headers() -> dict:
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


def get_items() -> list:
    with httpx.Client() as client:
        r = client.get(f"{LMS_API_URL}/items/", headers=_headers(), timeout=10)
        r.raise_for_status()
        return r.json()


def get_pass_rates(lab: str) -> list:
    with httpx.Client() as client:
        r = client.get(
            f"{LMS_API_URL}/analytics/pass-rates",
            params={"lab": lab},
            headers=_headers(),
            timeout=10,
        )
        r.raise_for_status()
        return r.json()