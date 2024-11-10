from typing import Optional, Dict, Any

from tgtg import TgtgClient

from ...config import TGTGSettings
from ...utils import NiceLogger


class AuthenticationHandler:
    """Klasa obsługująca proces autentykacji TGTG"""

    def __init__(self):
        self.logger = NiceLogger("AuthHandler").get_logger()
        self.client: Optional[TgtgClient] = None
        self.settings = TGTGSettings()
        self.is_auth_in_progress = False

        self.logger.debug(f"Inicjalizacja AuthenticationHandler. Ścieżka konfig: {self.settings.config_path}")

    async def start_login(self, email: str) -> Dict[str, Any]:
        """
        Rozpoczyna proces logowania — wysyła email z przyciskiem i czeka na jego kliknięcie
        """
        try:
            # Zabezpieczenie przed wielokrotnym logowaniem
            if self.is_auth_in_progress:
                self.logger.warning("Proces autentykacji jest już w toku")
                return {}

            self.is_auth_in_progress = True
            self.logger.info(f"Rozpoczęcie procesu logowania dla: {email}")

            # Inicjalizacja klienta i wysłanie maila
            self.client = TgtgClient(email=email)
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

            self.is_auth_in_progress = False
            return credentials

        except Exception as e:
            self.logger.error(f"Błąd podczas procesu logowania: {e}")
            self.is_auth_in_progress = False
            raise