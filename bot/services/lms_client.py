import httpx
from config import LMS_API_URL, LMS_API_KEY


def _headers() -> dict:
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


def _get(path: str, params: dict = None) -> any:
    with httpx.Client() as client:
        r = client.get(f"{LMS_API_URL}{path}", headers=_headers(), params=params, timeout=10)
        r.raise_for_status()
        return r.json()


def get_items() -> list:
    return _get("/items/")

def get_learners() -> list:
    return _get("/learners/")

def get_scores(lab: str) -> list:
    return _get("/analytics/scores", {"lab": lab})

def get_pass_rates(lab: str) -> list:
    return _get("/analytics/pass-rates", {"lab": lab})

def get_timeline(lab: str) -> list:
    return _get("/analytics/timeline", {"lab": lab})

def get_groups(lab: str) -> list:
    return _get("/analytics/groups", {"lab": lab})

def get_top_learners(lab: str, limit: int = 5) -> list:
    return _get("/analytics/top-learners", {"lab": lab, "limit": limit})

def get_completion_rate(lab: str) -> dict:
    return _get("/analytics/completion-rate", {"lab": lab})

def trigger_sync() -> dict:
    with httpx.Client() as client:
        r = client.post(f"{LMS_API_URL}/pipeline/sync", headers=_headers(), timeout=30)
        r.raise_for_status()
        return r.json()