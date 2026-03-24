import httpx
import os
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

path = os.path.join(os.path.dirname(__file__), "..", ".env.bot.secret")
load_dotenv(dotenv_path=path)

class BackendClient:
    def __init__(self):
        self.base_url = os.getenv("LMS_API_URL", "http://localhost:42002")
        self.api_key = os.getenv("LMS_API_KEY")
        
        if not self.api_key:
            raise ValueError("LMS_API_KEY не установлен в .env.bot.secret")
    
    def _get_headers(self) -> Dict[str, str]:
        """Возвращает заголовки для авторизации"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str) -> Any:
        """Универсальный метод для запросов к бэкенду"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.request(
                    method, 
                    url, 
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.ConnectError:
            raise Exception(f"Не удалось подключиться к бэкенду ({self.base_url}). Проверьте, запущены ли сервисы.")
        except httpx.TimeoutException:
            raise Exception("Таймаут при подключении к бэкенду. Сервис отвечает слишком медленно.")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Бэкенд вернул ошибку: {e.response.status_code} {e.response.reason_phrase}")
        except Exception as e:
            raise Exception(f"Ошибка при обращении к бэкенду: {str(e)}")
    
    def get_items(self) -> List[Dict]:
        """GET /items/ — возвращает все лабы и задания"""
        return self._make_request("GET", "/items/")
    
    def get_labs(self) -> List[Dict]:
        """Возвращает список лабораторных работ (фильтрует по типу)"""
        items = self.get_items()
        # Предполагаем, что у items есть поле type = "lab"
        return [item for item in items if item.get("type") == "lab"]
    
    def get_pass_rates(self, lab_name: str) -> Dict:
        """GET /analytics/pass-rates?lab=lab-01"""
        return self._make_request("GET", f"/analytics/pass-rates?lab={lab_name}")
    
    def check_health(self) -> Tuple[bool, Any]:
        """Проверяет доступность бэкенда через GET /items/"""
        try:
            items = self.get_items()
            # Если получили данные — бэкенд работает
            return True, len(items) if items else 0
        except Exception as e:
            return False, str(e)