import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

from src.utils import TGTGLogger


@dataclass
class Location:
    lat: float
    lng: float
    radius: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lat": self.lat,
            "lng": self.lng,
            "radius": self.radius
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        return cls(
            lat=float(data['lat']),
            lng=float(data['lng']),
            radius=int(data.get('radius', 5))
        )


class TGTGSettings:
    """Zarządzanie ustawieniami aplikacji"""

    DEFAULT_CONFIG = {
        "refresh_interval": 30,
        "locations": [
            {
                "lat": 52.2297,
                "lng": 21.0122,
                "radius": 5
            }
        ],
        "email": "",
        "access_token": "",
        "refresh_token": "",
        "user_id": "",
        "cookie": "",
        "notification_methods": ["console"],
        "favorite_stores": [],
        "min_price": 0,
        "max_price": 1000,
        "auto_reserve": False,
        "blacklist": [],
        "quiet_hours": {
            "start": "23:00",
            "end": "07:00"
        }
    }

    def __init__(self):
        self.logger = TGTGLogger("TGTGSettings").get_logger()

        # Użyj "Documents" zamiast "Dokumenty"
        self.config_dir = Path.home() / "Documents" / "TGTG Detector"
        self.config_path = self.config_dir / "config.json"

        self.logger.info(f"Ścieżka konfiguracji: {self.config_path}")

        # Utwórz katalog jeśli nie istnieje
        if not self.config_dir.exists():
            self.logger.info(f"Tworzenie katalogu konfiguracji: {self.config_dir}")
            self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Wczytuje konfigurację z pliku"""
        if not self.config_path.exists():
            self.logger.info(f"Plik konfiguracji nie istnieje, tworzę domyślny: {self.config_path}")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG

        try:
            self.logger.debug(f"Wczytywanie konfiguracji z: {self.config_path}")
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**self.DEFAULT_CONFIG, **config}
        except Exception as e:
            self.logger.error(f"Błąd podczas wczytywania konfiguracji: {e}")
            raise

    def save_config(self, config: Dict[str, Any]):
        """Zapisuje konfigurację do pliku"""
        try:
            self.logger.info(f"Zapisywanie konfiguracji do: {self.config_path}")
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
            self.logger.debug("Konfiguracja została pomyślnie zapisana")
        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania konfiguracji: {e}")
            raise

    def get_location(self, index: int = 0) -> Optional[Location]:
        """Pobiera lokalizację o danym indeksie"""
        locations = self.config.get('locations', [])
        if index < len(locations):
            return Location.from_dict(locations[index])
        return None

    def update_credentials(self, credentials: Dict[str, str]):
        """Aktualizuje dane uwierzytelniające"""
        self.logger.info("Aktualizacja danych uwierzytelniających...")
        self.config.update({
            "access_token": credentials.get("access_token", ""),
            "refresh_token": credentials.get("refresh_token", ""),
            "user_id": credentials.get("user_id", ""),
            "cookie": credentials.get("cookie", "")
        })
        self.save_config(self.config)
