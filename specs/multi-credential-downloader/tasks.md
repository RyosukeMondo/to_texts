# Multi-Credential Account Downloading - Implementation Tasks

## Phase 1: Core Infrastructure

### Task 1: Create Credential Data Model
- [ ] Define `Credential` dataclass with fields
- [ ] Define `CredentialStatus` enum (ACTIVE, INACTIVE, EXHAUSTED, ERROR)
- [ ] Add validation methods to Credential class
- [ ] Add serialization/deserialization methods
- [ ] Write unit tests for Credential model

**Files to create/modify:**
- `zlibrary_downloader/credential.py` (new)

**Dependencies:** None

---

### Task 2: Implement Credential Manager
- [ ] Create `CredentialManager` class
- [ ] Implement `load_credentials()` from .env file
- [ ] Implement credential validation logic
- [ ] Add support for both email/password and remix token formats
- [ ] Implement credential status tracking
- [ ] Add credential filtering (get_available_credentials)
- [ ] Write comprehensive unit tests

**Files to create/modify:**
- `zlibrary_downloader/credential_manager.py` (new)
- Test file: `tests/test_credential_manager.py` (new)

**Dependencies:** Task 1

---

### Task 3: Implement State Persistence
- [ ] Define state file format (JSON)
- [ ] Implement state save functionality
- [ ] Implement state load functionality
- [ ] Handle missing or corrupted state files
- [ ] Add state migration logic
- [ ] Write unit tests for state management

**Files to create/modify:**
- `zlibrary_downloader/rotation_state.py` (new)
- Test file: `tests/test_rotation_state.py` (new)

**Dependencies:** Task 1

---

### Task 4: Implement Client Pool
- [ ] Create `ZlibraryClientPool` class
- [ ] Implement client caching mechanism
- [ ] Add `get_current_client()` method
- [ ] Add `rotate_to_next_client()` method
- [ ] Add `validate_all_clients()` method
- [ ] Implement error handling for client creation
- [ ] Write unit tests for client pool

**Files to create/modify:**
- `zlibrary_downloader/client_pool.py` (new)
- Test file: `tests/test_client_pool.py` (new)

**Dependencies:** Task 2

---

## Phase 2: CLI Integration

### Task 5: Update CLI for Multi-Credential Support
- [ ] Update `load_credentials()` to use CredentialManager
- [ ] Update `initialize_zlibrary()` to use ClientPool
- [ ] Add display of credential status on startup
- [ ] Show available downloads per account
- [ ] Add new `--list-accounts` command
- [ ] Update help text and documentation
- [ ] Write integration tests

**Files to create/modify:**
- `zlibrary_downloader/cli.py` (existing)
- Test file: `tests/test_cli_integration.py` (update)

**Dependencies:** Task 2, Task 3, Task 4

---

### Task 6: Implement Automatic Credential Rotation
- [ ] Integrate rotation into search operation
- [ ] Integrate rotation into download operation
- [ ] Update state after each operation
- [ ] Handle credential exhaustion during operations
- [ ] Log credential usage for debugging
- [ ] Write integration tests

**Files to create/modify:**
- `zlibrary_downloader/cli.py` (existing)
- `zlibrary_downloader/client_pool.py` (existing)

**Dependencies:** Task 4, Task 5

---

## Phase 3: Enhanced Features

### Task 7: Implement Download Limit Tracking
- [ ] Fetch download limits from Z-Library API
- [ ] Track remaining downloads per credential
- [ ] Pre-check before operations
- [ ] Update limits after successful downloads
- [ ] Warn users when approaching limits
- [ ] Write unit and integration tests

**Files to create/modify:**
- `zlibrary_downloader/client_pool.py` (existing)
- `zlibrary_downloader/credential_manager.py` (existing)

**Dependencies:** Task 2, Task 4, Task 6

---

### Task 8: Implement Graceful Fallback
- [ ] Handle credential failures during operations
- [ ] Retry with next available credential
- [ ] Skip exhausted credentials
- [ ] Provide clear error messages
- [ ] Log fallback attempts
- [ ] Write comprehensive error handling tests

**Files to create/modify:**
- `zlibrary_downloader/client_pool.py` (existing)
- `zlibrary_downloader/cli.py` (existing)

**Dependencies:** Task 6, Task 7

---

## Phase 4: Testing & Documentation

### Task 9: Write Comprehensive Tests
- [ ] Unit tests for all new modules (80%+ coverage)
- [ ] Integration tests for full workflows
- [ ] Error handling and edge case tests
- [ ] Performance tests for credential rotation
- [ ] Run and fix any failing tests
- [ ] Generate coverage report

**Files to create/modify:**
- `tests/test_credential.py` (new)
- `tests/test_credential_manager.py` (new)
- `tests/test_rotation_state.py` (new)
- `tests/test_client_pool.py` (new)
- `tests/test_cli_integration.py` (update)

**Dependencies:** All Phase 1-3 tasks

---

### Task 10: Update Documentation
- [ ] Update README with multi-credential setup instructions
- [ ] Create `.env.example` with multiple credential format
- [ ] Add troubleshooting guide for credential issues
- [ ] Document credential rotation behavior
- [ ] Add examples for different credential formats
- [ ] Create migration guide from single to multi-credential

**Files to create/modify:**
- `README.md` (existing)
- `.env.example` (new)
- `docs/multi-credential-guide.md` (new)
- `docs/troubleshooting.md` (update)

**Dependencies:** Task 5

---

## Phase 5: Validation & Release

### Task 11: End-to-End Testing
- [ ] Test with single credential (backward compatibility)
- [ ] Test with multiple credentials
- [ ] Test credential rotation across multiple operations
- [ ] Test fallback when credential exhausted
- [ ] Test error handling and recovery
- [ ] Manual testing with real Z-Library accounts (if available)

**Files involved:**
- All implementation files

**Dependencies:** All Phase 1-4 tasks

---

### Task 12: Code Review & Cleanup
- [ ] Code review for quality and standards
- [ ] Remove debug logging
- [ ] Optimize performance where needed
- [ ] Ensure consistent style with existing code
- [ ] Update type hints and docstrings
- [ ] Final testing and bug fixes

**Files involved:**
- All implementation files

**Dependencies:** Task 11

---

## Summary of New Files

### Source Files
1. `zlibrary_downloader/credential.py` - Credential data model
2. `zlibrary_downloader/credential_manager.py` - Credential management
3. `zlibrary_downloader/rotation_state.py` - State persistence
4. `zlibrary_downloader/client_pool.py` - Client pool management

### Test Files
1. `tests/test_credential.py` - Credential model tests
2. `tests/test_credential_manager.py` - CredentialManager tests
3. `tests/test_rotation_state.py` - State persistence tests
4. `tests/test_client_pool.py` - ClientPool tests

### Documentation Files
1. `.env.example` - Example environment configuration
2. `docs/multi-credential-guide.md` - Setup and usage guide
3. `docs/troubleshooting.md` - Troubleshooting guide

### Modified Files
1. `zlibrary_downloader/cli.py` - CLI updates for multi-credential support
2. `zlibrary_downloader/__init__.py` - Export new classes
3. `README.md` - Update main documentation
4. `tests/test_cli_integration.py` - Update existing tests

## Implementation Priority

**High Priority (Core Functionality):**
- Task 1, 2, 3, 4 (Infrastructure)
- Task 5, 6 (CLI Integration)

**Medium Priority (Features):**
- Task 7, 8 (Enhanced Features)

**High Priority (Quality):**
- Task 9 (Comprehensive Testing)
- Task 11 (E2E Testing)

**Medium Priority (Polish):**
- Task 10 (Documentation)
- Task 12 (Code Review)

## Estimated Effort

- Infrastructure (Tasks 1-4): 8-10 hours
- CLI Integration (Tasks 5-6): 4-6 hours
- Enhanced Features (Tasks 7-8): 4-6 hours
- Testing (Task 9): 6-8 hours
- Documentation (Task 10): 3-4 hours
- Validation (Tasks 11-12): 4-6 hours

**Total Estimated Time:** 29-40 hours (depending on complexity and testing depth)
