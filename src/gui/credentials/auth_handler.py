import json
from pathlib import Path
from typing import Optional, Dict, Any

from tgtg import TgtgClient

from ...utils import TGTGLogger


class AuthenticationHandler:
    """Klasa obsługująca proces autentykacji TGTG"""

    def __init__(self):
        self.logger = TGTGLogger("AuthHandler").get_logger()
        self.client: Optional[TgtgClient] = None
        self.config_dir = Path.home() / "Documents" / "TGTG Detector"
        self.config_path = self.config_dir / "config.json"

        self.logger.debug(f"Inicjalizacja AuthenticationHandler. Ścieżka konfig: {self.config_path}")

    async def send_verification_email(self, email: str) -> bool:
        """
        Wysyła email z kodem weryfikacyjnym

        Returns:
            bool: True jeśli wysłanie się powiodło
        """
        try:
            self.logger.info(f"Wysyłanie emaila weryfikacyjnego do: {email}")
            self.client = TgtgClient(email=email)
            self.logger.info("Email weryfikacyjny został wysłany")
            return True

        except Exception as e:
            self.logger.error(f"Błąd podczas wysyłania emaila: {e}")
            raise

    async def verify_code(self, email: str, code: str) -> Dict[str, Any]:
        """
        Weryfikuje kod i pobiera credentials

        Returns:
            Dict[str, Any]: Słownik z danymi uwierzytelniającymi
        """
        try:
            self.logger.info("Rozpoczęcie weryfikacji kodu...")
            credentials = self.client.get_credentials()

            await self._save_credentials(email, credentials)

            self.logger.info("Weryfikacja kodu zakończona sukcesem")
            return credentials

        except Exception as e:
            self.logger.error(f"Błąd podczas weryfikacji kodu: {e}")
            raise

    async def _save_credentials(self, email: str, credentials: Dict[str, Any]):
        """Zapisuje credentials do pliku konfiguracyjnego"""
        try:
            self.logger.debug("Tworzenie struktury konfiguracyjnej...")

            # Utwórz katalog jeśli nie istnieje
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Przygotuj domyślną konfigurację
            config = {
                "refresh_interval": 30,
                "locations": [
                    {
                        "lat": 52.2297,
                        "lng": 21.0122,
                        "radius": 5
                    }
                ],
                "notification_methods": ["console"],
                "favorite_stores": [],
                "min_price": 0,
                "max_price": 1000,
                "auto_reserve": False
            }

            # Wczytaj istniejącą konfigurację jeśli istnieje
            if self.config_path.exists():
                self.logger.debug("Wczytywanie istniejącej konfiguracji...")
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config.update(json.load(f))

            # Dodaj/aktualizuj credentials
            self.logger.debug("Aktualizacja credentials w konfiguracji...")
            config.update({
                "email": email,
                "access_token": credentials["access_token"],
                "refresh_token": credentials["refresh_token"],
                "user_id": credentials["user_id"],
                "cookie": credentials["cookie"]
            })

            # Zapisz zaktualizowaną konfigurację
            self.logger.debug("Zapisywanie zaktualizowanej konfiguracji...")
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            self.logger.info("Credentials zostały pomyślnie zapisane")

        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania credentials: {e}")
            raise
