# Multi-Credential Account Downloading - Implementation Tasks

## Phase 1: Core Infrastructure

### Task 1: Create Credential Data Model
- [ ] Create `zlibrary_downloader/credential.py`
- [ ] Define `CredentialStatus` enum
- [ ] Define `Credential` dataclass with required fields
- [ ] Add validation methods
- [ ] Add serialization/deserialization
- [ ] Write unit tests (`tests/test_credential.py`)
- [ ] Achieve >80% code coverage

**Deliverables:**
- credential.py with Credential and CredentialStatus
- test_credential.py with comprehensive tests

**Dependencies:** None

---

### Task 2: Implement Credential Manager
- [ ] Create `zlibrary_downloader/credential_manager.py`
- [ ] Implement credential loading from .env
- [ ] Support single credential format (backward compatible)
- [ ] Support multiple credential format (ZLIBRARY_ACCOUNT_N_*)
- [ ] Implement credential validation
- [ ] Implement rotation logic
- [ ] Implement credential filtering (get_available)
- [ ] Write unit tests (`tests/test_credential_manager.py`)

**Deliverables:**
- credential_manager.py with CredentialManager class
- test_credential_manager.py with comprehensive tests

**Dependencies:** Task 1

---

### Task 3: Implement State Persistence
- [ ] Create `zlibrary_downloader/rotation_state.py`
- [ ] Define state file format (JSON)
- [ ] Implement state save functionality
- [ ] Implement state load functionality
- [ ] Handle missing state files gracefully
- [ ] Handle corrupted state files
- [ ] Implement state validation
- [ ] Write unit tests (`tests/test_rotation_state.py`)

**Deliverables:**
- rotation_state.py with RotationState class
- test_rotation_state.py with comprehensive tests

**Dependencies:** Task 1

---

### Task 4: Implement Client Pool
- [ ] Create `zlibrary_downloader/client_pool.py`
- [ ] Implement client caching mechanism
- [ ] Implement get_current_client()
- [ ] Implement rotate_to_next_client()
- [ ] Implement validate_all_clients()
- [ ] Handle client creation errors
- [ ] Write unit tests (`tests/test_client_pool.py`)

**Deliverables:**
- client_pool.py with ZlibraryClientPool class
- test_client_pool.py with comprehensive tests

**Dependencies:** Task 2

---

## Phase 2: CLI Integration

### Task 5: Update CLI for Multi-Credential Support
- [ ] Update cli.py load_credentials() function
- [ ] Update cli.py initialize_zlibrary() function
- [ ] Add credential status display on startup
- [ ] Display available downloads per account
- [ ] Update help text documentation
- [ ] Write integration tests

**Deliverables:**
- Updated cli.py
- Integration test coverage
- Updated help messages

**Dependencies:** Task 2, Task 3, Task 4

---

### Task 6: Implement Automatic Credential Rotation
- [ ] Integrate rotation into search_books()
- [ ] Integrate rotation into download_book()
- [ ] Update state after each operation
- [ ] Handle credential exhaustion
- [ ] Add logging for credential usage
- [ ] Write integration tests

**Deliverables:**
- Updated cli.py with rotation
- Integration tests
- Logging implementation

**Dependencies:** Task 4, Task 5

---

## Phase 3: Enhanced Features

### Task 7: Implement Download Limit Tracking
- [ ] Fetch download limits from Z-Library API
- [ ] Track remaining downloads per credential
- [ ] Pre-check before operations
- [ ] Update limits after successful downloads
- [ ] Warn users approaching limits
- [ ] Write unit and integration tests

**Deliverables:**
- Updated credential_manager.py
- Updated client_pool.py
- Test coverage for limit tracking

**Dependencies:** Task 2, Task 4, Task 6

---

### Task 8: Implement Graceful Fallback
- [ ] Handle credential failures during operations
- [ ] Implement retry logic with next credential
- [ ] Skip exhausted credentials automatically
- [ ] Provide clear error messages
- [ ] Log all fallback attempts
- [ ] Write comprehensive error handling tests

**Deliverables:**
- Updated client_pool.py
- Updated cli.py
- Error handling test coverage

**Dependencies:** Task 6, Task 7

---

## Phase 4: Testing & Documentation

### Task 9: Write Comprehensive Tests
- [-] Unit tests for credential.py (>80% coverage)
- [ ] Unit tests for credential_manager.py (>80% coverage)
- [ ] Unit tests for rotation_state.py (>80% coverage)
- [ ] Unit tests for client_pool.py (>80% coverage)
- [ ] Integration tests for full workflows
- [ ] Error handling and edge case tests
- [ ] Performance tests for rotation overhead
- [ ] Run full test suite
- [ ] Fix any failing tests
- [ ] Generate coverage report

**Deliverables:**
- All test files with >80% coverage
- Coverage report
- All tests passing

**Dependencies:** All Phase 1-3 tasks

---

### Task 10: Update Documentation
- [ ] Update README.md with multi-credential setup
- [ ] Create `.env.example` with multiple credential format
- [ ] Create `docs/multi-credential-guide.md`
- [ ] Add troubleshooting guide
- [ ] Add configuration examples
- [ ] Add migration guide from single to multi-credential
- [ ] Update API documentation

**Deliverables:**
- Updated README.md
- .env.example
- User guide
- Troubleshooting guide

**Dependencies:** Task 5

---

## Phase 5: Validation & Release

### Task 11: End-to-End Testing
- [ ] Test backward compatibility (single credential)
- [ ] Test multiple credentials (2-3 accounts)
- [ ] Test rotation across 50+ operations
- [ ] Test fallback when credential exhausted
- [ ] Test error recovery
- [ ] Manual testing with real accounts (if available)
- [ ] Performance testing

**Deliverables:**
- E2E test results
- Performance metrics
- Verification of backward compatibility

**Dependencies:** All Phase 1-4 tasks

---

### Task 12: Code Review & Cleanup
- [ ] Full code review for quality
- [ ] Remove debug logging
- [ ] Optimize performance
- [ ] Ensure consistent style
- [ ] Update type hints
- [ ] Update docstrings
- [ ] Final bug fixes
- [ ] Prepare for release

**Deliverables:**
- Clean, reviewed code
- Performance optimizations
- Documentation completeness

**Dependencies:** Task 11

---

## Summary of New Files

### Source Files (4 new)
1. `zlibrary_downloader/credential.py`
2. `zlibrary_downloader/credential_manager.py`
3. `zlibrary_downloader/rotation_state.py`
4. `zlibrary_downloader/client_pool.py`

### Modified Files (3)
1. `zlibrary_downloader/cli.py`
2. `zlibrary_downloader/__init__.py`
3. `tests/test_cli_integration.py`

### Test Files (5 new)
1. `tests/test_credential.py`
2. `tests/test_credential_manager.py`
3. `tests/test_rotation_state.py`
4. `tests/test_client_pool.py`
5. `tests/test_multi_credential_integration.py`

### Documentation Files (4 new)
1. `.env.example`
2. `docs/multi-credential-guide.md`
3. `docs/troubleshooting.md`
4. Updated `README.md`

## Effort Estimation

| Phase | Tasks | Estimated Hours | Priority |
|-------|-------|-----------------|----------|
| 1: Infrastructure | 1-4 | 8-10 | HIGH |
| 2: CLI Integration | 5-6 | 4-6 | HIGH |
| 3: Enhanced Features | 7-8 | 4-6 | MEDIUM |
| 4: Testing & Docs | 9-10 | 9-12 | HIGH |
| 5: Validation | 11-12 | 4-6 | HIGH |
| **TOTAL** | **12** | **29-40** | - |

## Dependencies

```
Task 1 (Credential)
    ↓
Task 2 (Manager) ← Task 1
    ↓
Task 3 (State) ← Task 1
    ↓
Task 4 (Pool) ← Task 2
    ↓
Task 5 (CLI) ← Task 2, 3, 4
    ↓
Task 6 (Rotation) ← Task 4, 5
    ↓
Task 7 (Limits) ← Task 2, 4, 6
    ↓
Task 8 (Fallback) ← Task 6, 7
    ↓
Task 9 (Tests) ← All Phase 1-3
    ↓
Task 10 (Docs) ← Task 5
    ↓
Task 11 (E2E) ← All Phase 1-4
    ↓
Task 12 (Review) ← Task 11
```

## Quality Gates

### Before Phase Completion
- [ ] All tests passing
- [ ] >80% code coverage
- [ ] No linting errors
- [ ] Type checking passing
- [ ] Code review approved
- [ ] Documentation complete
- [ ] Performance acceptable

### Before Release
- [ ] All phases completed
- [ ] E2E tests passing
- [ ] Backward compatibility verified
- [ ] Security review completed
- [ ] Documentation reviewed
- [ ] Release notes prepared
