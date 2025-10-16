"""
Credential manager for Z-Library downloader.

This module provides functionality to manage multiple Z-Library credentials,
supporting both TOML-based configuration files and backward-compatible .env files.
"""

import contextlib
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Import tomllib (Python 3.11+) or tomli (older versions)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "tomli is required for Python <3.11. " "Install it with: pip install tomli"
        )

from dotenv import load_dotenv

from .credential import Credential, CredentialStatus
from .rotation_state import RotationState


class CredentialManager:
    """
    Manages Z-Library credentials with support for multiple accounts.

    Supports two configuration formats:
    1. TOML file (zlibrary_credentials.toml) - supports unlimited accounts
    2. .env file - backward compatible single-credential format

    Attributes:
        credentials: List of Credential objects
        current_index: Index of currently active credential
        rotation_state: RotationState instance for state persistence
    """

    DEFAULT_TOML_FILE = "zlibrary_credentials.toml"
    DEFAULT_STATE_FILE = Path.home() / ".zlibrary" / "rotation_state.json"

    def __init__(self, state_file: Optional[Path] = None):
        """
        Initialize CredentialManager.

        Args:
            state_file: Path to rotation state file (optional)
        """
        self.credentials: List[Credential] = []
        self.current_index: int = 0
        self.rotation_state: RotationState = RotationState(state_file or self.DEFAULT_STATE_FILE)

    def detect_credential_source(self) -> str:
        """
        Detect which credential source is available.

        Priority:
        1. zlibrary_credentials.toml in current directory
        2. .env file in current directory

        Returns:
            str: "toml" or "env"

        Raises:
            FileNotFoundError: If no credential source is found
        """
        if Path(self.DEFAULT_TOML_FILE).exists():
            return "toml"
        elif Path(".env").exists():
            return "env"
        else:
            raise FileNotFoundError(
                "No credential configuration found. "
                f"Please create either '{self.DEFAULT_TOML_FILE}' or '.env' file."
            )

    def _validate_toml_structure(self, config: Dict[str, Any]) -> None:
        """Validate TOML configuration structure."""
        if "credentials" not in config:
            raise ValueError(
                "Invalid TOML file: missing 'credentials' section. "
                "Expected [[credentials]] entries."
            )

        if not isinstance(config["credentials"], list):
            raise ValueError(
                "Invalid TOML file: 'credentials' must be a list of tables. "
                "Use [[credentials]] syntax."
            )

        if len(config["credentials"]) == 0:
            raise ValueError("TOML file contains no credentials")

    def _parse_credential_from_toml(
        self, idx: int, cred_data: Dict[str, Any]
    ) -> Optional[Credential]:
        """Parse a single credential from TOML data."""
        if not isinstance(cred_data, dict):
            raise ValueError(f"Credential {idx} is not a valid table")

        identifier = cred_data.get("identifier")
        if not identifier:
            raise ValueError(f"Credential {idx} missing required field 'identifier'")

        has_email_auth = "email" in cred_data and "password" in cred_data
        has_remix_auth = "remix_userid" in cred_data and "remix_userkey" in cred_data

        if not has_email_auth and not has_remix_auth:
            raise ValueError(
                f"Credential '{identifier}' must have either "
                "email/password or remix_userid/remix_userkey"
            )

        credential = Credential(
            identifier=identifier,
            email=cred_data.get("email"),
            password=cred_data.get("password"),
            remix_userid=cred_data.get("remix_userid"),
            remix_userkey=cred_data.get("remix_userkey"),
            status=CredentialStatus.VALID,
            enabled=cred_data.get("enabled", True),
        )

        return credential if credential.enabled else None

    def load_from_toml(self, toml_file: str = DEFAULT_TOML_FILE) -> None:
        """
        Load credentials from TOML configuration file.

        Args:
            toml_file: Path to TOML file

        Raises:
            FileNotFoundError: If TOML file doesn't exist
            ValueError: If TOML file is malformed or missing required fields
        """
        toml_path = Path(toml_file)
        if not toml_path.exists():
            raise FileNotFoundError(f"TOML file not found: {toml_file}")

        try:
            with open(toml_path, "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse TOML file: {e}")

        self._validate_toml_structure(config)

        self.credentials = []
        for idx, cred_data in enumerate(config["credentials"]):
            credential = self._parse_credential_from_toml(idx, cred_data)
            if credential:
                self.credentials.append(credential)

        if len(self.credentials) == 0:
            raise ValueError("No enabled credentials found in TOML file")

        self._load_state()

    def _create_credential_from_env(self) -> Credential:
        """Create a Credential from environment variables."""
        remix_userid = os.getenv("ZLIBRARY_REMIX_USERID")
        remix_userkey = os.getenv("ZLIBRARY_REMIX_USERKEY")
        email = os.getenv("ZLIBRARY_EMAIL")
        password = os.getenv("ZLIBRARY_PASSWORD")

        has_remix_auth = remix_userid and remix_userkey
        has_email_auth = email and password

        if not has_remix_auth and not has_email_auth:
            raise ValueError(
                "No valid credentials found in .env file. "
                "Please set either ZLIBRARY_REMIX_USERID/ZLIBRARY_REMIX_USERKEY "
                "or ZLIBRARY_EMAIL/ZLIBRARY_PASSWORD"
            )

        return Credential(
            identifier="default",
            email=email,
            password=password,
            remix_userid=remix_userid,
            remix_userkey=remix_userkey,
            status=CredentialStatus.VALID,
            enabled=True,
        )

    def load_from_env(self) -> None:
        """
        Load single credential from .env file (backward compatible).

        Raises:
            ValueError: If no valid credentials found in .env
        """
        load_dotenv()
        credential = self._create_credential_from_env()
        self.credentials = [credential]
        self.current_index = 0
        self._load_state()

    def load_credentials(self) -> None:
        """
        Auto-detect and load credentials from available source.

        Automatically detects whether to use TOML or .env format.

        Raises:
            FileNotFoundError: If no credential configuration is found
            ValueError: If credential configuration is invalid
        """
        source = self.detect_credential_source()

        if source == "toml":
            self.load_from_toml()
        elif source == "env":
            self.load_from_env()

    def get_current(self) -> Optional[Credential]:
        """
        Get the currently active credential.

        Returns:
            Optional[Credential]: Current credential, or None if no credentials available
        """
        if not self.credentials:
            return None

        if 0 <= self.current_index < len(self.credentials):
            return self.credentials[self.current_index]

        return None

    def get_available(self) -> List[Credential]:
        """
        Get list of available (usable) credentials.

        Filters out credentials that are:
        - Disabled (enabled=False)
        - Invalid (status=INVALID)
        - Exhausted (status=EXHAUSTED or downloads_left=0)

        Returns:
            List[Credential]: List of available credentials
        """
        return [cred for cred in self.credentials if cred.is_available()]

    def rotate(self) -> Optional[Credential]:
        """
        Rotate to the next available credential.

        Skips over disabled, invalid, and exhausted credentials.
        Wraps around to the beginning if at the end.

        Returns:
            Optional[Credential]: Next available credential, or None if all exhausted

        Raises:
            RuntimeError: If no credentials are loaded
        """
        if not self.credentials:
            raise RuntimeError("No credentials loaded")

        available = self.get_available()
        if not available:
            return None  # All credentials exhausted

        # Try each credential starting from next index
        attempts = 0
        max_attempts = len(self.credentials)

        while attempts < max_attempts:
            # Move to next credential with wrap-around
            self.current_index = (self.current_index + 1) % len(self.credentials)
            attempts += 1

            current = self.credentials[self.current_index]
            if current.is_available():
                # Save state after successful rotation
                self._save_state()
                return current

        # No available credentials found
        return None

    def _restore_credential_from_state(
        self, credential: Credential, saved_cred: Dict[str, Any]
    ) -> None:
        """Restore a credential's metadata from saved state."""
        if "status" in saved_cred:
            with contextlib.suppress(ValueError):
                credential.status = CredentialStatus(saved_cred["status"])

        if "downloads_left" in saved_cred:
            credential.downloads_left = saved_cred["downloads_left"]

        if "last_used" in saved_cred:
            with contextlib.suppress(ValueError, TypeError):
                from datetime import datetime

                credential.last_used = datetime.fromisoformat(saved_cred["last_used"])

        if "last_validated" in saved_cred:
            with contextlib.suppress(ValueError, TypeError):
                from datetime import datetime

                credential.last_validated = datetime.fromisoformat(saved_cred["last_validated"])

    def _load_state(self) -> None:
        """Load persisted rotation state from file."""
        state = self.rotation_state.load_or_initialize(
            default_index=0,
            default_credentials=[],
        )

        if 0 <= state["current_index"] < len(self.credentials):
            self.current_index = state["current_index"]

        if state["credentials"]:
            state_creds_map = {cred["identifier"]: cred for cred in state["credentials"]}

            for credential in self.credentials:
                if credential.identifier in state_creds_map:
                    self._restore_credential_from_state(
                        credential, state_creds_map[credential.identifier]
                    )

    def _save_state(self) -> None:
        """Save current rotation state to file."""
        credentials_data = [cred.to_dict() for cred in self.credentials]

        with contextlib.suppress(Exception):
            self.rotation_state.save(self.current_index, credentials_data)

    def _validate_profile_response(
        self, credential: Credential, profile_response: Any
    ) -> tuple[bool, Optional[str]]:
        """Validate profile response and update credential status."""
        from datetime import datetime

        if not profile_response:
            credential.status = CredentialStatus.INVALID
            credential.last_validated = datetime.now()
            return False, "Authentication failed: Empty response from API"

        if not profile_response.get("success", False):
            credential.status = CredentialStatus.INVALID
            credential.last_validated = datetime.now()
            error_msg = profile_response.get("error", "Unknown authentication error")
            return False, f"Authentication failed: {error_msg}"

        credential.status = CredentialStatus.VALID
        credential.last_validated = datetime.now()
        self._update_downloads_from_profile(credential, profile_response)
        return True, None

    def _handle_validation_error(
        self, credential: Credential, error: Exception, attempt: int, max_retries: int
    ) -> tuple[bool, Optional[str]]:
        """Handle validation errors with retry logic."""
        from datetime import datetime

        should_retry = attempt < max_retries - 1
        is_network_error = isinstance(
            error, (requests.exceptions.Timeout, requests.exceptions.RequestException)
        )

        if is_network_error and should_retry:
            return True, None  # Signal to retry

        credential.status = CredentialStatus.INVALID
        credential.last_validated = datetime.now()

        if isinstance(error, requests.exceptions.Timeout):
            return False, f"Timeout after {max_retries} attempts: {str(error)}"
        if isinstance(error, requests.exceptions.RequestException):
            return False, f"Network error after {max_retries} attempts: {str(error)}"
        return False, f"Unexpected error during validation: {str(error)}"

    def validate_credential(
        self, credential: Credential, max_retries: int = 2
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a credential by testing it with the Z-Library API.

        Uses getProfile() API call to verify credential validity and fetch download limits.
        Implements retry logic for network errors.

        Args:
            credential: The credential to validate
            max_retries: Maximum number of retry attempts (default: 2)

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)

        Side effects:
            - Updates credential.status based on validation result
            - Updates credential.last_validated timestamp
            - Updates credential.downloads_left if validation successful
        """
        from .client import Zlibrary

        for attempt in range(max_retries):
            try:
                client = Zlibrary(
                    email=credential.email,
                    password=credential.password,
                    remix_userid=credential.remix_userid,
                    remix_userkey=credential.remix_userkey,
                )

                profile_response = client.getProfile()
                return self._validate_profile_response(credential, profile_response)

            except Exception as e:
                should_retry, error_msg = self._handle_validation_error(
                    credential, e, attempt, max_retries
                )
                if not should_retry:
                    return False, error_msg

        return False, "Validation failed: Unknown error"

    def _update_downloads_from_profile(
        self, credential: Credential, profile_response: Dict[str, Any]
    ) -> None:
        """Extract and update download limits from profile response."""
        user_data = profile_response.get("user", {})
        downloads_limit = user_data.get("downloads_limit", 10)
        downloads_today = user_data.get("downloads_today", 0)
        credential.downloads_left = downloads_limit - downloads_today

        if credential.downloads_left <= 0:
            credential.status = CredentialStatus.EXHAUSTED

    def update_downloads_left(self, credential: Credential) -> tuple[bool, Optional[str]]:
        """
        Update the downloads_left field for a credential.

        Fetches current download limit and usage from Z-Library API.

        Args:
            credential: The credential to update

        Returns:
            tuple[bool, Optional[str]]: (success, error_message)

        Side effects:
            - Updates credential.downloads_left
            - Updates credential.status if exhausted
        """
        from .client import Zlibrary

        try:
            client = Zlibrary(
                email=credential.email,
                password=credential.password,
                remix_userid=credential.remix_userid,
                remix_userkey=credential.remix_userkey,
            )

            profile_response = client.getProfile()

            if not profile_response or not profile_response.get("success", False):
                return False, "Failed to fetch profile from API"

            self._update_downloads_from_profile(credential, profile_response)
            return True, None

        except Exception as e:
            return False, f"Error updating download limits: {str(e)}"
