"""
Rotation state persistence for Z-Library credential rotation.

This module provides functionality to persist and load the rotation state,
including the current credential index and credential metadata.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


class RotationState:
    """
    Manages persistent state for credential rotation.

    Attributes:
        state_file: Path to the JSON state file
    """

    def __init__(self, state_file: Path):
        """
        Initialize RotationState with a file path.

        Args:
            state_file: Path to the JSON state file
        """
        self.state_file = Path(state_file)
        self._state: Dict[str, Any] = {}

    def save(self, current_index: int, credentials_data: List[Dict[str, Any]]) -> None:
        """
        Save rotation state to file.

        Args:
            current_index: Index of the current credential
            credentials_data: List of credential dictionaries

        Raises:
            IOError: If file cannot be written
            OSError: If file permissions cannot be set
        """
        self._state = {
            "current_index": current_index,
            "credentials": credentials_data,
        }

        # Ensure parent directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Write state to temporary file first (atomic write)
        temp_file = self.state_file.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2)

            # Set file permissions to 600 (owner read/write only) on Unix systems
            if os.name != "nt":  # Not Windows
                os.chmod(temp_file, 0o600)

            # Atomically replace the old file
            temp_file.replace(self.state_file)

        except Exception as e:
            # Clean up temp file if something went wrong
            if temp_file.exists():
                temp_file.unlink()
            raise e

    def load(self) -> Dict[str, Any]:
        """
        Load rotation state from file.

        Returns:
            Dict containing current_index and credentials list

        Raises:
            FileNotFoundError: If state file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
            ValueError: If state structure is invalid
        """
        if not self.state_file.exists():
            raise FileNotFoundError(f"State file not found: {self.state_file}")

        with open(self.state_file, "r", encoding="utf-8") as f:
            self._state = json.load(f)

        # Validate state structure
        if not self.validate(self._state):
            raise ValueError(f"Invalid state file structure in {self.state_file}")

        return self._state

    def exists(self) -> bool:
        """
        Check if state file exists.

        Returns:
            bool: True if state file exists, False otherwise
        """
        return self.state_file.exists()

    @staticmethod
    def validate(state: Any) -> bool:
        """
        Validate the structure of a state dictionary.

        Args:
            state: State dictionary to validate

        Returns:
            bool: True if state structure is valid, False otherwise
        """
        if not isinstance(state, dict):
            return False

        # Check required fields
        if "current_index" not in state:
            return False

        if "credentials" not in state:
            return False

        # Validate current_index is an integer
        if not isinstance(state["current_index"], int):
            return False

        # Validate credentials is a list
        if not isinstance(state["credentials"], list):
            return False

        # Validate each credential has an identifier
        for cred in state["credentials"]:
            if not isinstance(cred, dict):
                return False
            if "identifier" not in cred:
                return False

        return True

    def load_or_initialize(
        self, default_index: int = 0, default_credentials: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Load state from file, or return default values if file doesn't exist or is corrupted.

        Args:
            default_index: Default current_index if state cannot be loaded
            default_credentials: Default credentials list if state cannot be loaded

        Returns:
            Dict containing current_index and credentials list
        """
        try:
            return self.load()
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            # Return default state if file doesn't exist or is corrupted
            return {
                "current_index": default_index,
                "credentials": default_credentials or [],
            }
