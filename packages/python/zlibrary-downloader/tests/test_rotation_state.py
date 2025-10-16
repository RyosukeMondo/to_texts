"""
Unit tests for the RotationState persistence module.
"""

import json
import os
from pathlib import Path
import pytest
from zlibrary_downloader.rotation_state import RotationState


class TestRotationStateInit:
    """Tests for RotationState initialization."""

    def test_init_with_path_string(self, tmp_path):
        """Test initialization with string path."""
        state_file = tmp_path / "state.json"
        state = RotationState(str(state_file))
        assert state.state_file == Path(state_file)

    def test_init_with_pathlib_path(self, tmp_path):
        """Test initialization with pathlib.Path."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)
        assert state.state_file == state_file


class TestRotationStateSave:
    """Tests for RotationState.save() method."""

    def test_save_creates_file(self, tmp_path):
        """Test that save() creates a state file."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        credentials_data = [
            {"identifier": "user1@example.com", "email": "user1@example.com"},
            {"identifier": "user2@example.com", "email": "user2@example.com"},
        ]
        state.save(current_index=0, credentials_data=credentials_data)

        assert state_file.exists()

    def test_save_creates_parent_directories(self, tmp_path):
        """Test that save() creates parent directories if they don't exist."""
        state_file = tmp_path / "nested" / "dir" / "state.json"
        state = RotationState(state_file)

        credentials_data = [{"identifier": "user@example.com"}]
        state.save(current_index=0, credentials_data=credentials_data)

        assert state_file.exists()
        assert state_file.parent.exists()

    def test_save_writes_correct_structure(self, tmp_path):
        """Test that save() writes the correct JSON structure."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        credentials_data = [
            {"identifier": "user1@example.com", "status": "valid"},
            {"identifier": "user2@example.com", "status": "exhausted"},
        ]
        state.save(current_index=1, credentials_data=credentials_data)

        # Read and verify the saved JSON
        with open(state_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data["current_index"] == 1
        assert saved_data["credentials"] == credentials_data

    def test_save_overwrites_existing_file(self, tmp_path):
        """Test that save() overwrites an existing state file."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        # Save initial state
        state.save(current_index=0, credentials_data=[{"identifier": "user1"}])

        # Save updated state
        state.save(current_index=1, credentials_data=[{"identifier": "user2"}])

        # Verify the file contains the updated state
        with open(state_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data["current_index"] == 1
        assert len(saved_data["credentials"]) == 1
        assert saved_data["credentials"][0]["identifier"] == "user2"

    def test_save_sets_file_permissions_unix(self, tmp_path):
        """Test that save() sets file permissions to 600 on Unix systems."""
        if os.name == 'nt':  # Skip on Windows
            pytest.skip("File permission test only applies to Unix systems")

        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        state.save(current_index=0, credentials_data=[{"identifier": "user"}])

        # Check file permissions
        file_stat = state_file.stat()
        file_mode = file_stat.st_mode & 0o777
        assert file_mode == 0o600

    def test_save_empty_credentials_list(self, tmp_path):
        """Test that save() works with an empty credentials list."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        state.save(current_index=0, credentials_data=[])

        with open(state_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data["current_index"] == 0
        assert saved_data["credentials"] == []


class TestRotationStateLoad:
    """Tests for RotationState.load() method."""

    def test_load_existing_file(self, tmp_path):
        """Test loading a valid state file."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        # Create a state file
        test_data = {
            "current_index": 2,
            "credentials": [
                {"identifier": "user1"},
                {"identifier": "user2"},
                {"identifier": "user3"},
            ],
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # Load and verify
        loaded = state.load()
        assert loaded["current_index"] == 2
        assert len(loaded["credentials"]) == 3

    def test_load_nonexistent_file(self, tmp_path):
        """Test that load() raises FileNotFoundError for missing file."""
        state_file = tmp_path / "nonexistent.json"
        state = RotationState(state_file)

        with pytest.raises(FileNotFoundError):
            state.load()

    def test_load_corrupted_json(self, tmp_path):
        """Test that load() raises JSONDecodeError for corrupted file."""
        state_file = tmp_path / "corrupted.json"
        state = RotationState(state_file)

        # Write invalid JSON
        with open(state_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid json content }")

        with pytest.raises(json.JSONDecodeError):
            state.load()

    def test_load_invalid_structure_missing_current_index(self, tmp_path):
        """Test that load() raises ValueError for missing current_index."""
        state_file = tmp_path / "invalid.json"
        state = RotationState(state_file)

        # Write JSON without current_index
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump({"credentials": []}, f)

        with pytest.raises(ValueError):
            state.load()

    def test_load_invalid_structure_missing_credentials(self, tmp_path):
        """Test that load() raises ValueError for missing credentials."""
        state_file = tmp_path / "invalid.json"
        state = RotationState(state_file)

        # Write JSON without credentials
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump({"current_index": 0}, f)

        with pytest.raises(ValueError):
            state.load()

    def test_load_roundtrip(self, tmp_path):
        """Test that save and load are inverses."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        original_data = {
            "current_index": 3,
            "credentials": [
                {"identifier": "user1@example.com", "status": "valid"},
                {"identifier": "user2@example.com", "status": "exhausted"},
            ],
        }

        # Save and load
        state.save(
            current_index=original_data["current_index"],
            credentials_data=original_data["credentials"]
        )
        loaded = state.load()

        # Verify data matches
        assert loaded["current_index"] == original_data["current_index"]
        assert loaded["credentials"] == original_data["credentials"]


class TestRotationStateExists:
    """Tests for RotationState.exists() method."""

    def test_exists_true_for_existing_file(self, tmp_path):
        """Test that exists() returns True for existing file."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        # Create the file
        state.save(current_index=0, credentials_data=[])

        assert state.exists() is True

    def test_exists_false_for_nonexistent_file(self, tmp_path):
        """Test that exists() returns False for nonexistent file."""
        state_file = tmp_path / "nonexistent.json"
        state = RotationState(state_file)

        assert state.exists() is False


class TestRotationStateValidate:
    """Tests for RotationState.validate() static method."""

    def test_validate_valid_state(self):
        """Test validation of a valid state structure."""
        valid_state = {
            "current_index": 0,
            "credentials": [
                {"identifier": "user1"},
            ],
        }
        assert RotationState.validate(valid_state) is True

    def test_validate_empty_credentials(self):
        """Test validation with empty credentials list."""
        state = {
            "current_index": 0,
            "credentials": [],
        }
        assert RotationState.validate(state) is True

    def test_validate_not_dict(self):
        """Test validation fails for non-dict input."""
        assert RotationState.validate("not a dict") is False
        assert RotationState.validate([]) is False
        assert RotationState.validate(None) is False

    def test_validate_missing_current_index(self):
        """Test validation fails without current_index."""
        state = {"credentials": []}
        assert RotationState.validate(state) is False

    def test_validate_missing_credentials(self):
        """Test validation fails without credentials."""
        state = {"current_index": 0}
        assert RotationState.validate(state) is False

    def test_validate_invalid_current_index_type(self):
        """Test validation fails with non-integer current_index."""
        state = {
            "current_index": "0",  # String instead of int
            "credentials": [],
        }
        assert RotationState.validate(state) is False

    def test_validate_invalid_credentials_type(self):
        """Test validation fails with non-list credentials."""
        state = {
            "current_index": 0,
            "credentials": "not a list",
        }
        assert RotationState.validate(state) is False

    def test_validate_credential_without_identifier(self):
        """Test validation fails if credential lacks identifier."""
        state = {
            "current_index": 0,
            "credentials": [
                {"email": "user@example.com"},  # Missing identifier
            ],
        }
        assert RotationState.validate(state) is False

    def test_validate_credential_not_dict(self):
        """Test validation fails if credential is not a dict."""
        state = {
            "current_index": 0,
            "credentials": ["not a dict"],
        }
        assert RotationState.validate(state) is False

    def test_validate_multiple_valid_credentials(self):
        """Test validation with multiple valid credentials."""
        state = {
            "current_index": 1,
            "credentials": [
                {"identifier": "user1", "email": "user1@example.com"},
                {"identifier": "user2", "email": "user2@example.com"},
                {"identifier": "user3", "email": "user3@example.com"},
            ],
        }
        assert RotationState.validate(state) is True


class TestRotationStateLoadOrInitialize:
    """Tests for RotationState.load_or_initialize() method."""

    def test_load_or_initialize_loads_existing_file(self, tmp_path):
        """Test that load_or_initialize loads existing valid file."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        # Create a valid state file
        state.save(current_index=2, credentials_data=[{"identifier": "user1"}])

        # Load or initialize
        loaded = state.load_or_initialize(default_index=0, default_credentials=[])

        assert loaded["current_index"] == 2
        assert len(loaded["credentials"]) == 1

    def test_load_or_initialize_returns_defaults_for_missing_file(self, tmp_path):
        """Test that load_or_initialize returns defaults for missing file."""
        state_file = tmp_path / "nonexistent.json"
        state = RotationState(state_file)

        default_credentials = [{"identifier": "default_user"}]
        loaded = state.load_or_initialize(
            default_index=5,
            default_credentials=default_credentials
        )

        assert loaded["current_index"] == 5
        assert loaded["credentials"] == default_credentials

    def test_load_or_initialize_returns_defaults_for_corrupted_file(self, tmp_path):
        """Test that load_or_initialize returns defaults for corrupted file."""
        state_file = tmp_path / "corrupted.json"
        state = RotationState(state_file)

        # Write corrupted JSON
        with open(state_file, 'w', encoding='utf-8') as f:
            f.write("{ corrupted json }")

        loaded = state.load_or_initialize(default_index=0, default_credentials=[])

        assert loaded["current_index"] == 0
        assert loaded["credentials"] == []

    def test_load_or_initialize_returns_defaults_for_invalid_structure(self, tmp_path):
        """Test that load_or_initialize returns defaults for invalid structure."""
        state_file = tmp_path / "invalid.json"
        state = RotationState(state_file)

        # Write valid JSON but invalid structure
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump({"wrong_field": "value"}, f)

        loaded = state.load_or_initialize(default_index=0, default_credentials=[])

        assert loaded["current_index"] == 0
        assert loaded["credentials"] == []

    def test_load_or_initialize_with_none_default_credentials(self, tmp_path):
        """Test load_or_initialize with None as default_credentials."""
        state_file = tmp_path / "nonexistent.json"
        state = RotationState(state_file)

        loaded = state.load_or_initialize(default_index=0, default_credentials=None)

        assert loaded["current_index"] == 0
        assert loaded["credentials"] == []


class TestRotationStateAtomicWrite:
    """Tests for atomic write behavior."""

    def test_atomic_write_uses_temp_file(self, tmp_path):
        """Test that save uses a temporary file during write."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        # Mock a failure scenario isn't feasible without monkey-patching,
        # but we can verify basic atomic behavior by checking the temp file doesn't remain
        state.save(current_index=0, credentials_data=[{"identifier": "user"}])

        # Verify temp file doesn't exist after successful save
        temp_file = state_file.with_suffix('.tmp')
        assert not temp_file.exists()

    def test_save_replaces_file_atomically(self, tmp_path):
        """Test that save replaces the file atomically."""
        state_file = tmp_path / "state.json"
        state = RotationState(state_file)

        # Create initial state
        state.save(current_index=0, credentials_data=[{"identifier": "user1"}])

        # Verify we can load it
        loaded1 = state.load()
        assert loaded1["current_index"] == 0

        # Overwrite with new state
        state.save(current_index=1, credentials_data=[{"identifier": "user2"}])

        # Verify new state loaded correctly
        loaded2 = state.load()
        assert loaded2["current_index"] == 1
        assert loaded2["credentials"][0]["identifier"] == "user2"
