from typing import Optional, Dict, Any

from tgtg import TgtgClient

from ...config import TGTGSettings
from ...utils import TGTGLogger


class AuthenticationHandler:
    """Klasa obsługująca proces autentykacji TGTG"""

    def __init__(self):
        self.logger = TGTGLogger("AuthHandler").get_logger()
        self.client: Optional[TgtgClient] = None
        self.settings = TGTGSettings()

        self.logger.debug(f"Inicjalizacja AuthenticationHandler. Ścieżka konfig: {self.settings.config_path}")

    async def send_verification_email(self, email: str) -> bool:
        """
        Wysyła email z kodem weryfikacyjnym

        Returns:
            bool: True, jeśli wysłanie się powiodło
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
        Weryfikuje kod i zapisuje credentials w konfiguracji

        Args:
            email: Adres email użytkownika
            code: Kod weryfikacyjny z emaila

        Returns:
            Dict[str, Any]: Słownik z danymi uwierzytelniającymi
        """
        try:
            self.logger.info(f"Rozpoczęcie weryfikacji kodu dla {email}...")
            self.logger.debug(f"Otrzymany kod: {code}")

            credentials = self.client.get_credentials()

            # Aktualizacja konfiguracji
            self.settings.config.update({
                "email": email,
                "access_token": credentials["access_token"],
                "refresh_token": credentials["refresh_token"],
                "user_id": credentials["user_id"],
                "cookie": credentials["cookie"]
            })

            # Zapisz konfigurację
            self.settings.save_config(self.settings.config)
            self.logger.info("Credentials zostały pomyślnie zapisane w konfiguracji")

            return credentials

        except Exception as e:
            self.logger.error(f"Błąd podczas weryfikacji kodu lub zapisu credentials: {e}")
            raise
