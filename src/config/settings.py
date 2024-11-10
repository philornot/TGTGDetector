import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from src.utils import NiceLogger


@dataclass
class Location:
    street: str = ""
    city: str = ""
    coordinates: Optional[Tuple[float, float]] = None
    radius: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "street": self.street,
            "city": self.city,
            "coordinates": self.coordinates,
            "radius": self.radius
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        coords_data = data.get('coordinates')
        coordinates = None
        if coords_data and isinstance(coords_data, (list, tuple)) and len(coords_data) == 2:
            try:
                coordinates = (float(coords_data[0]), float(coords_data[1]))
            except (ValueError, TypeError):
                coordinates = None

        return cls(
            street=str(data.get('street', "")),
            city=str(data.get('city', "")),
            coordinates=coordinates,
            radius=int(data.get('radius', 5))
        )


@dataclass
class Filters:
    keywords: str = ""
    company: Optional[str] = None
    companies_list: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keywords": self.keywords,
            "company": self.company,
            "companies_list": self.companies_list or []
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Filters':
        return cls(
            keywords=str(data.get('keywords', "")),
            company=data.get('company'),
            companies_list=list(data.get('companies_list', []))
        )


class TGTGSettings:
    """Zarządzanie ustawieniami aplikacji"""

    DEFAULT_CONFIG = {
        "refresh_interval": 30,
        "location": {
            "street": "",
            "city": "",
            "coordinates": None,
            "radius": 5
        },
        "filters": {
            "keywords": "",
            "company": None,
            "companies_list": []
        },
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
        self.logger = NiceLogger("TGTGSettings").get_logger()
        self.logger.info("=== Inicjalizacja menedżera ustawień ===")

        # Użyj "Documents" zamiast "Dokumenty"
        self.config_dir = Path.home() / "Documents" / "TGTG Detector"
        self.config_path = self.config_dir / "config.json"

        self.logger.info(f"Ścieżka konfiguracji: {self.config_path}")

        # Utwórz katalog, jeśli nie istnieje
        if not self.config_dir.exists():
            self.logger.info(f"Tworzenie katalogu konfiguracji: {self.config_dir}")
            self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()
        self.logger.debug(f"Załadowana konfiguracja: {self.config}")

    def load_config(self) -> Dict[str, Any]:
        """Wczytuje konfigurację z pliku"""
        self.logger.debug("=== Wczytywanie konfiguracji ===")

        if not self.config_path.exists():
            self.logger.info(f"Plik konfiguracji nie istnieje, tworzę domyślny: {self.config_path}")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG

        try:
            self.logger.debug(f"Wczytywanie konfiguracji z: {self.config_path}")
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                merged_config = {**self.DEFAULT_CONFIG, **config}
                self.logger.debug(f"Załadowana konfiguracja: {merged_config}")
                return merged_config
        except Exception as e:
            self.logger.error(f"Błąd podczas wczytywania konfiguracji: {e}", exc_info=True)
            raise

    def save_config(self, config: Dict[str, Any]):
        """Zapisuje konfigurację do pliku"""
        self.logger.debug("=== Zapisywanie konfiguracji ===")

        try:
            self.logger.info(f"Zapisywanie konfiguracji do: {self.config_path}")
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
            self.logger.debug("Konfiguracja została pomyślnie zapisana")
            self.logger.debug(f"Zapisana konfiguracja: {config}")
        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania konfiguracji: {e}", exc_info=True)
            raise

    def get_location(self) -> Location:
        """Pobiera ustawienia lokalizacji"""
        self.logger.debug("Pobieranie ustawień lokalizacji")
        return Location.from_dict(self.config.get('location', {}))

    def get_filters(self) -> Filters:
        """Pobiera ustawienia filtrów"""
        self.logger.debug("Pobieranie ustawień filtrów")
        return Filters.from_dict(self.config.get('filters', {}))

    def update_location(self, location: Location):
        """Aktualizuje ustawienia lokalizacji"""
        self.logger.debug(f"Aktualizacja lokalizacji: {location}")
        self.config['location'] = location.to_dict()
        self.save_config(self.config)

    def update_filters(self, filters: Filters):
        """Aktualizuje ustawienia filtrów"""
        self.logger.debug(f"Aktualizacja filtrów: {filters}")
        self.config['filters'] = filters.to_dict()
        self.save_config(self.config)

    def update_credentials(self, credentials: Dict[str, str]):
        """Aktualizuje dane uwierzytelniające"""
        self.logger.info("=== Aktualizacja danych uwierzytelniających ===")
        self.logger.debug(f"Nowe credentials: {credentials}")

        self.config.update({
            "access_token": credentials.get("access_token", ""),
            "refresh_token": credentials.get("refresh_token", ""),
            "user_id": credentials.get("user_id", ""),
            "cookie": credentials.get("cookie", "")
        })
        self.save_config(self.config)
