"""
Client pool for managing Z-Library client instances.

This module provides a pool of Z-Library client instances, each associated with
a credential. Clients are cached and reused to avoid repeated authentication.
"""

from typing import Dict, Optional

from .client import Zlibrary
from .credential import Credential
from .credential_manager import CredentialManager


class ZlibraryClientPool:
    """
    Manages a pool of Z-Library client instances with credential awareness.

    The pool caches client instances by credential identifier to avoid repeated
    authentication. It integrates with CredentialManager for rotation and
    credential lifecycle management.

    Attributes:
        credential_manager: CredentialManager instance for credential operations
        clients: Dictionary mapping credential identifiers to Zlibrary clients
    """

    def __init__(self, credential_manager: CredentialManager):
        """
        Initialize ZlibraryClientPool.

        Args:
            credential_manager: CredentialManager instance to use for credentials
        """
        self.credential_manager = credential_manager
        self.clients: Dict[str, Zlibrary] = {}

    def _create_client(self, credential: Credential) -> Optional[Zlibrary]:
        """
        Create a new Zlibrary client instance for a credential.

        Args:
            credential: The credential to create client for

        Returns:
            Optional[Zlibrary]: New client instance, or None if creation failed
        """
        try:
            client = Zlibrary(
                email=credential.email,
                password=credential.password,
                remix_userid=credential.remix_userid,
                remix_userkey=credential.remix_userkey,
            )

            # Verify client is logged in
            if not client.isLoggedIn():
                return None

            return client

        except Exception:
            return None

    def get_current_client(self) -> Optional[Zlibrary]:
        """
        Get the client for the currently active credential.

        Returns cached client if available and authenticated, otherwise creates a new one.
        Re-authenticates if the cached client session has expired.

        Returns:
            Optional[Zlibrary]: Current Zlibrary client, or None if unavailable

        Raises:
            RuntimeError: If no credentials are loaded in CredentialManager
        """
        current_credential = self.credential_manager.get_current()

        if current_credential is None:
            return None

        # Check if we have a cached client
        if current_credential.identifier in self.clients:
            cached_client = self.clients[current_credential.identifier]
            
            # Verify the cached client is still authenticated
            try:
                if cached_client.isLoggedIn():
                    return cached_client
                else:
                    # Session expired - remove from cache and create new client
                    del self.clients[current_credential.identifier]
            except Exception:
                # Error checking login status - remove from cache
                del self.clients[current_credential.identifier]

        # Create new client and cache it
        client = self._create_client(current_credential)
        if client:
            self.clients[current_credential.identifier] = client

        return client

    def rotate_client(self) -> Optional[Zlibrary]:
        """
        Rotate to the next available credential and return its client.

        Rotates the credential manager to the next available credential,
        then returns the client for that credential (creating it if needed).
        Re-authenticates if the cached client session has expired.

        Returns:
            Optional[Zlibrary]: Client for next credential, or None if all exhausted

        Raises:
            RuntimeError: If no credentials are loaded in CredentialManager
        """
        next_credential = self.credential_manager.rotate()

        if next_credential is None:
            return None  # All credentials exhausted

        # Check if we have a cached client
        if next_credential.identifier in self.clients:
            cached_client = self.clients[next_credential.identifier]
            
            # Verify the cached client is still authenticated
            try:
                if cached_client.isLoggedIn():
                    return cached_client
                else:
                    # Session expired - remove from cache and create new client
                    del self.clients[next_credential.identifier]
            except Exception:
                # Error checking login status - remove from cache
                del self.clients[next_credential.identifier]

        # Create new client and cache it
        client = self._create_client(next_credential)
        if client:
            self.clients[next_credential.identifier] = client

        return client

    def validate_all(self) -> Dict[str, tuple[bool, Optional[str]]]:
        """
        Validate all credentials in the credential manager.

        Tests each credential against the Z-Library API using
        CredentialManager.validate_credential().

        Returns:
            Dict[str, tuple[bool, Optional[str]]]: Dictionary mapping credential
                identifiers to (is_valid, error_message) tuples
        """
        results = {}

        for credential in self.credential_manager.credentials:
            is_valid, error_msg = self.credential_manager.validate_credential(credential)
            results[credential.identifier] = (is_valid, error_msg)

        return results

    def refresh_client(self, identifier: str) -> Optional[Zlibrary]:
        """
        Recreate the client for a specific credential.

        Removes the cached client (if any) and creates a new one.
        Useful when credentials have been updated or client is in bad state.

        Args:
            identifier: Identifier of the credential to refresh

        Returns:
            Optional[Zlibrary]: New client instance, or None if creation failed

        Raises:
            ValueError: If credential with given identifier not found
        """
        # Find credential with matching identifier
        credential = None
        for cred in self.credential_manager.credentials:
            if cred.identifier == identifier:
                credential = cred
                break

        if credential is None:
            raise ValueError(f"Credential with identifier '{identifier}' not found")

        # Remove cached client if exists
        if identifier in self.clients:
            del self.clients[identifier]

        # Create new client
        client = self._create_client(credential)
        if client:
            self.clients[identifier] = client

        return client

    def clear_cache(self) -> None:
        """
        Clear all cached clients.

        Useful when credentials have been reloaded or when you want to
        force recreation of all clients.
        """
        self.clients.clear()
