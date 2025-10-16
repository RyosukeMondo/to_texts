# Tasks Document

## Phase 1: Core Infrastructure

- [x] 1. Create Credential Data Model
  - File: packages/python/zlibrary-downloader/zlibrary_downloader/credential.py
  - Define CredentialStatus enum (VALID, INVALID, EXHAUSTED)
  - Define Credential dataclass with all required fields (identifier, email, password, remix_userid, remix_userkey, status, downloads_left, last_used, last_validated)
  - Add is_available() method to check if credential can be used
  - Add to_dict() and from_dict() methods for serialization
  - Purpose: Establish type-safe credential data model
  - _Leverage: Python dataclasses, enum, datetime_
  - _Requirements: 1.1, 1.2_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer specializing in data modeling and type systems | Task: Create comprehensive Credential data model in packages/python/zlibrary-downloader/zlibrary_downloader/credential.py with CredentialStatus enum and Credential dataclass following requirements 1.1 and 1.2. The dataclass should use type hints and include methods for availability checking and serialization. | Restrictions: Use Python 3.8+ features, follow PEP 8 naming conventions, do not add external dependencies beyond standard library | Success: Credential model is well-defined with proper type hints, serialization methods work correctly, is_available() logic is sound. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [x] 2. Add TOML Parsing Dependency
  - File: packages/python/zlibrary-downloader/setup.py or requirements.txt or pyproject.toml
  - Add tomli dependency for Python <3.11 (Python 3.11+ has built-in tomllib)
  - Add conditional dependency: tomli;python_version<"3.11"
  - Update project dependencies configuration
  - Purpose: Enable TOML configuration file parsing
  - _Leverage: Existing dependency management setup_
  - _Requirements: 5.1_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: DevOps Engineer with expertise in Python packaging | Task: Add tomli dependency to project dependencies in packages/python/zlibrary-downloader/ following requirement 5.1. Add conditional dependency for Python versions <3.11 since Python 3.11+ has built-in tomllib. Update setup.py, requirements.txt, or pyproject.toml as appropriate for the project structure. | Restrictions: Use conditional dependency syntax (tomli;python_version<"3.11"), do not break existing dependencies, follow project's dependency management pattern | Success: tomli dependency added correctly with version constraint, conditional for Python <3.11, project can be installed successfully on both Python 3.10 and 3.11+. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [x] 3. Write Credential Model Unit Tests
  - File: packages/python/zlibrary-downloader/tests/test_credential.py
  - Test CredentialStatus enum values
  - Test Credential dataclass instantiation with various combinations
  - Test is_available() method logic
  - Test to_dict() and from_dict() serialization
  - Achieve >80% code coverage
  - Purpose: Ensure credential model reliability
  - _Leverage: pytest framework_
  - _Requirements: 1.1, 1.2_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in Python unit testing and pytest | Task: Create comprehensive unit tests for Credential model in packages/python/zlibrary-downloader/tests/test_credential.py covering requirements 1.1 and 1.2. Test all enum values, dataclass instantiation, availability logic, and serialization/deserialization. | Restrictions: Use pytest framework, test both success and failure scenarios, ensure test isolation, aim for >80% coverage | Success: All Credential functionality is tested, edge cases covered, tests run independently and pass consistently. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [x] 4. Implement Rotation State Persistence
  - File: packages/python/zlibrary-downloader/zlibrary_downloader/rotation_state.py
  - Define RotationState class with state_file path
  - Implement save() method to write JSON state file
  - Implement load() method to read JSON state file
  - Implement exists() and validate() methods
  - Handle missing and corrupted state files gracefully
  - Set proper file permissions (chmod 600 on Unix)
  - Purpose: Provide persistent rotation state storage
  - _Leverage: json, pathlib, os modules_
  - _Requirements: 5.1, 5.2_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in file I/O and state management | Task: Create RotationState class in packages/python/zlibrary-downloader/zlibrary_downloader/rotation_state.py for persistent state storage following requirements 5.1 and 5.2. Implement JSON-based save/load with corruption handling and proper file permissions. | Restrictions: Use only standard library (json, pathlib, os), handle file permissions cross-platform, ensure atomic writes, validate JSON structure | Success: State can be saved and loaded reliably, corrupted files handled gracefully, file permissions set correctly on Unix systems. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 5. Write Rotation State Unit Tests
  - File: packages/python/zlibrary-downloader/tests/test_rotation_state.py
  - Test save() and load() methods
  - Test handling of missing state files
  - Test handling of corrupted JSON
  - Test file permissions on Unix systems
  - Test state validation logic
  - Achieve >80% code coverage
  - Purpose: Ensure state persistence reliability
  - _Leverage: pytest, tempfile for test isolation_
  - _Requirements: 5.1, 5.2_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in file I/O testing and pytest | Task: Create comprehensive unit tests for RotationState in packages/python/zlibrary-downloader/tests/test_rotation_state.py covering requirements 5.1 and 5.2. Test save/load operations, corruption handling, and file permissions. | Restrictions: Use pytest and tempfile, test cross-platform behavior where applicable, ensure test cleanup, aim for >80% coverage | Success: All state persistence functionality tested, edge cases like corruption and missing files covered, tests are isolated and reliable. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 6. Implement Credential Manager Core
  - File: packages/python/zlibrary-downloader/zlibrary_downloader/credential_manager.py
  - Create CredentialManager class with credentials list and current_index
  - Implement detect_credential_source() to check for TOML file or .env
  - Implement load_from_toml() to parse zlibrary_credentials.toml using tomllib/tomli
  - Implement load_from_env() to parse single credential from .env (backward compatible)
  - Implement get_current() to return currently active credential
  - Implement rotate() to move to next available credential with wrap-around
  - Implement get_available() to filter out invalid/exhausted/disabled credentials
  - Integrate with RotationState for state persistence
  - Purpose: Manage credential lifecycle and rotation logic
  - _Leverage: Credential model, RotationState, tomllib/tomli for TOML, python-dotenv for .env_
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 5.1_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer specializing in business logic and configuration management | Task: Create CredentialManager class in packages/python/zlibrary-downloader/zlibrary_downloader/credential_manager.py following requirements 1.1, 2.1, 2.2, 2.3, and 5.1. Implement auto-detection of configuration source (zlibrary_credentials.toml or .env), TOML parsing using tomllib (Python 3.11+) or tomli (older versions), and maintain backward compatibility with single-credential .env format. Implement rotation logic with wrap-around and state persistence integration. | Restrictions: Must support backward compatibility with single-credential .env, handle edge cases like all credentials exhausted, skip disabled credentials in TOML, follow single responsibility principle, use try/except for tomllib import fallback | Success: Credentials load from TOML file with unlimited accounts, .env single-credential format still works, rotation works with proper wrap-around, state persists correctly, disabled credentials are filtered out. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 7. Implement Credential Validation
  - File: packages/python/zlibrary-downloader/zlibrary_downloader/credential_manager.py (extend)
  - Add validate_credential() method that tests credential with Zlibrary client
  - Use getProfile() API call to verify credential validity
  - Update credential status based on validation result
  - Fetch download limits during validation
  - Add update_downloads_left() method
  - Handle network errors with retry logic (2 attempts)
  - Purpose: Verify credential validity and track quotas
  - _Leverage: Existing Zlibrary client (packages/python/zlibrary-downloader/zlibrary_downloader/client.py)_
  - _Requirements: 1.3, 1.4, 4.1, 4.2_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in API integration and error handling | Task: Extend CredentialManager in packages/python/zlibrary-downloader/zlibrary_downloader/credential_manager.py with validation methods following requirements 1.3, 1.4, 4.1, and 4.2. Implement credential validation using Zlibrary client's getProfile() method, download limit tracking, and robust error handling with retries. | Restrictions: Reuse existing Zlibrary client, never log passwords, implement retry logic (max 2 attempts), handle network timeouts gracefully | Success: Credentials validate correctly against Z-Library API, download limits fetched and tracked, network errors handled with retries, no sensitive data logged. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 8. Write Credential Manager Unit Tests
  - File: packages/python/zlibrary-downloader/tests/test_credential_manager.py
  - Test credential loading from TOML file with multiple accounts
  - Test credential loading from .env (single credential, backward compatibility)
  - Test auto-detection logic (TOML vs .env)
  - Test disabled credential filtering from TOML
  - Test rotation logic and wrap-around behavior
  - Test get_available() filtering
  - Test validation with mocked Zlibrary client
  - Test state persistence integration
  - Test error handling (all credentials exhausted, invalid, malformed TOML, etc.)
  - Achieve >80% code coverage
  - Purpose: Ensure credential management reliability
  - _Leverage: pytest, unittest.mock for mocking Zlibrary client, tempfile for test TOML files_
  - _Requirements: 1.1, 1.3, 1.4, 2.1, 2.2, 2.3, 4.1, 4.2, 5.1_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in Python testing, mocking, and pytest | Task: Create comprehensive unit tests for CredentialManager in packages/python/zlibrary-downloader/tests/test_credential_manager.py covering requirements 1.1, 1.3, 1.4, 2.1, 2.2, 2.3, 4.1, 4.2, and 5.1. Mock Zlibrary client for validation tests, test TOML parsing with multiple accounts, test single-credential .env format for backward compatibility, test disabled credential filtering, rotation logic, and error scenarios including malformed TOML. | Restrictions: Use pytest and unittest.mock, mock external dependencies (Zlibrary client), use tempfile to create test TOML files, test both success and failure paths, ensure test isolation, aim for >80% coverage | Success: All CredentialManager functionality tested including TOML parsing, .env parsing, auto-detection, rotation, validation, disabled credential filtering, and error handling. Tests are reliable and cover edge cases. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 9. Implement Client Pool
  - File: packages/python/zlibrary-downloader/zlibrary_downloader/client_pool.py
  - Create ZlibraryClientPool class with credential_manager and clients dict
  - Implement get_current_client() to return cached or create new Zlibrary client
  - Implement rotate_client() to rotate credential and return new client
  - Implement validate_all() to test all credentials
  - Implement refresh_client() to recreate client for a credential
  - Cache Zlibrary client instances by credential identifier
  - Purpose: Manage Zlibrary client instances with credential awareness
  - _Leverage: CredentialManager, existing Zlibrary client_
  - _Requirements: 2.1, 3.1, 3.2, 3.3_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer specializing in resource management and caching patterns | Task: Create ZlibraryClientPool class in packages/python/zlibrary-downloader/zlibrary_downloader/client_pool.py following requirements 2.1, 3.1, 3.2, and 3.3. Implement client caching by credential identifier, rotation integration with CredentialManager, and validation methods. | Restrictions: Cache clients to avoid repeated authentication, handle credential rotation transparently, properly handle client creation failures, maintain separation of concerns | Success: Clients are properly cached and reused, rotation triggers client switching, validation tests all credentials, client creation errors handled gracefully. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 10. Write Client Pool Unit Tests
  - File: packages/python/zlibrary-downloader/tests/test_client_pool.py
  - Test client caching (same credential returns cached client)
  - Test get_current_client() and rotate_client()
  - Test validate_all() with various credential states
  - Test refresh_client() recreates client
  - Test error handling for client creation failures
  - Achieve >80% code coverage
  - Purpose: Ensure client pool reliability
  - _Leverage: pytest, unittest.mock for mocking CredentialManager and Zlibrary_
  - _Requirements: 2.1, 3.1, 3.2, 3.3_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in caching patterns and integration testing | Task: Create comprehensive unit tests for ZlibraryClientPool in packages/python/zlibrary-downloader/tests/test_client_pool.py covering requirements 2.1, 3.1, 3.2, and 3.3. Test caching behavior, rotation, validation, and error scenarios. | Restrictions: Use pytest and unittest.mock, mock CredentialManager and Zlibrary client, verify caching effectiveness, test error handling, aim for >80% coverage | Success: All ClientPool functionality tested including caching, rotation, validation, and error handling. Tests verify clients are reused appropriately. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

## Phase 2: CLI Integration

- [ ] 11. Update CLI for Multi-Credential Support
  - File: packages/python/zlibrary-downloader/zlibrary_downloader/cli.py
  - Refactor load_credentials() to use CredentialManager
  - Refactor initialize_zlibrary() to use ClientPool
  - Add display_credential_status() function to show account summary
  - Update help text and documentation
  - Maintain backward compatibility with single-credential format
  - Purpose: Integrate credential management into CLI
  - _Leverage: CredentialManager, ClientPool_
  - _Requirements: 1.1, 1.3, 1.4, 1.5, 5.1, 5.2, 5.3, 5.4_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Full-stack Python Developer with CLI application expertise | Task: Refactor CLI in packages/python/zlibrary-downloader/zlibrary_downloader/cli.py to integrate CredentialManager and ClientPool following requirements 1.1, 1.3, 1.4, 1.5, 5.1, 5.2, 5.3, and 5.4. Update initialization, add credential status display, maintain backward compatibility. | Restrictions: Do not break existing CLI interface, maintain backward compatibility with single credential, preserve existing command-line arguments, follow existing CLI patterns | Success: CLI initializes with CredentialManager and ClientPool, displays credential status on startup, single-credential format still works, help text updated. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 12. Implement Automatic Rotation in Operations
  - File: packages/python/zlibrary-downloader/zlibrary_downloader/cli.py (extend)
  - Add rotation call after successful search_books() operation
  - Add rotation call after successful download_book() operation
  - Update download limit tracking after downloads
  - Add logging for rotation events
  - Handle credential exhaustion gracefully
  - Purpose: Enable automatic credential switching
  - _Leverage: ClientPool, CredentialManager_
  - _Requirements: 2.2, 2.3, 3.2, 3.3, 4.2, 4.3_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Backend Python Developer with expertise in workflow automation | Task: Extend CLI operations in packages/python/zlibrary-downloader/zlibrary_downloader/cli.py to integrate automatic rotation following requirements 2.2, 2.3, 3.2, 3.3, 4.2, and 4.3. Add rotation after search/download operations, update download limits, implement proper logging. | Restrictions: Only rotate after successful operations, handle errors without losing state, log rotation events (not credentials), maintain operation transparency to user | Success: Rotation occurs automatically after operations, download limits update correctly, exhausted credentials skipped, rotation events logged appropriately. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 13. Implement Graceful Fallback and Error Handling
  - File: packages/python/zlibrary-downloader/zlibrary_downloader/cli.py (extend)
  - Add retry logic for failed operations with next credential
  - Implement automatic skip for exhausted credentials
  - Add clear error messages for credential issues
  - Handle "all credentials exhausted" scenario
  - Add warning messages for approaching limits
  - Purpose: Ensure robust error handling
  - _Leverage: ClientPool, CredentialManager error handling_
  - _Requirements: 3.4, 4.3, 4.4, 5.4_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer specializing in error handling and resilience patterns | Task: Implement comprehensive error handling in packages/python/zlibrary-downloader/zlibrary_downloader/cli.py following requirements 3.4, 4.3, 4.4, and 5.4. Add retry logic, exhaustion handling, clear error messages, and warning system. | Restrictions: Retry with next credential on failures, do not expose credentials in errors, provide actionable error messages, limit retry attempts to avoid infinite loops | Success: Operations retry with next credential on failure, exhausted credentials skipped automatically, clear error messages displayed, all-exhausted scenario handled gracefully. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 14. Write CLI Integration Tests
  - File: packages/python/zlibrary-downloader/tests/test_cli_integration.py
  - Test CLI initialization with multi-credential setup
  - Test search operation with rotation
  - Test download operation with rotation and limit tracking
  - Test backward compatibility with single credential
  - Test error scenarios (all exhausted, invalid credentials)
  - Test credential status display
  - Purpose: Ensure CLI integration works end-to-end
  - _Leverage: pytest, unittest.mock for API mocking_
  - _Requirements: All Phase 1-2 requirements_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in integration testing and CLI testing | Task: Create comprehensive integration tests for CLI in packages/python/zlibrary-downloader/tests/test_cli_integration.py covering all Phase 1-2 requirements. Test initialization, operations with rotation, backward compatibility, and error scenarios. | Restrictions: Use pytest and mocking for external APIs, test real workflow scenarios, ensure tests are independent, verify both success and failure paths | Success: All CLI integration scenarios tested including initialization, rotation during operations, error handling, and backward compatibility. Tests are reliable and comprehensive. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

## Phase 3: Documentation and Testing

- [ ] 15. Create zlibrary_credentials.toml.example
  - File: packages/python/zlibrary-downloader/zlibrary_credentials.toml.example
  - Create TOML example file with multiple credential examples
  - Show email/password authentication format
  - Show remix token authentication format
  - Include comments explaining each field
  - Document the "enabled" flag for disabling accounts
  - Include optional state_file configuration
  - Add instructions on how to use the file
  - Purpose: Provide clear TOML configuration template
  - _Leverage: TOML format standards_
  - _Requirements: 1.1, 1.2, 5.1_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Technical Writer with expertise in configuration documentation | Task: Create comprehensive zlibrary_credentials.toml.example in packages/python/zlibrary-downloader/zlibrary_credentials.toml.example following requirements 1.1, 1.2, and 5.1. Create well-documented TOML example with multiple credentials showing both email/password and remix token auth, with clear comments explaining each field and the enabled/disabled feature. | Restrictions: Use clear, non-technical language, follow TOML syntax standards, include at least 3 example credentials, explain optional fields, show how to enable/disable accounts | Success: zlibrary_credentials.toml.example is clear and comprehensive, includes examples for all credential types with both auth methods, enabled flag is well-documented, easy for users to copy and customize. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 16. Update README.md with Multi-Credential Guide
  - File: packages/python/zlibrary-downloader/README.md
  - Add multi-credential setup section with TOML format
  - Document zlibrary_credentials.toml configuration structure
  - Explain TOML benefits (unlimited accounts, enable/disable, readable)
  - Document single-credential .env format (backward compatible)
  - Explain automatic detection (TOML vs .env)
  - Explain rotation behavior
  - Add troubleshooting tips (TOML syntax errors, file not found, etc.)
  - Include migration guide from .env to TOML
  - Document Python version requirements (tomli for <3.11)
  - Purpose: Provide user-facing documentation
  - _Leverage: Existing README.md structure_
  - _Requirements: All requirements_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Technical Writer specializing in user documentation | Task: Update README.md in packages/python/zlibrary-downloader/README.md to document TOML-based multi-credential feature covering all requirements. Add setup instructions for zlibrary_credentials.toml, explain TOML format benefits, document backward compatibility with .env, explain rotation, add troubleshooting, and provide migration guide from .env to TOML. | Restrictions: Write for end-users (not developers), include practical TOML examples, explain syntax clearly, maintain existing README structure, document tomli dependency for Python <3.11 | Success: README clearly explains TOML configuration format, setup instructions are easy to follow with TOML examples, backward compatibility with .env documented, troubleshooting addresses TOML-specific issues, migration path from .env to TOML is clear. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 17. Run Full Test Suite and Fix Issues
  - Files: All test files
  - Run pytest on all unit tests
  - Run integration tests
  - Generate coverage report (target >80%)
  - Fix any failing tests
  - Fix any coverage gaps
  - Purpose: Ensure all code is tested and working
  - _Leverage: pytest, coverage.py_
  - _Requirements: All requirements_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer responsible for test quality and coverage | Task: Execute complete test suite for multi-credential-downloader, generate coverage report, and fix any issues to achieve >80% coverage target. Run all unit and integration tests. | Restrictions: All tests must pass, coverage should be >80% for new code, do not skip or disable tests to achieve coverage, fix root causes not symptoms | Success: All tests pass consistently, coverage report shows >80% for new modules, no critical gaps in test coverage, test suite runs reliably. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 18. Perform End-to-End Manual Testing
  - Test backward compatibility with single credential .env
  - Test TOML multi-credential setup with 2-3 accounts
  - Test TOML file parsing with various configurations
  - Test enabled/disabled credential filtering
  - Perform 10+ operations to verify rotation
  - Test credential exhaustion scenario
  - Test "all credentials exhausted" scenario
  - Test application restart with state persistence
  - Test error recovery and fallback
  - Test TOML syntax error handling
  - Purpose: Validate real-world usage scenarios
  - _Leverage: Real or test Z-Library accounts_
  - _Requirements: All requirements_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer specializing in manual testing and user acceptance | Task: Perform comprehensive end-to-end manual testing of TOML-based multi-credential feature covering all requirements. Test backward compatibility with .env, TOML configuration with multiple accounts, enabled/disabled credentials, rotation across multiple operations, exhaustion scenarios, state persistence, TOML syntax error handling, and error recovery. | Restrictions: Test with real workflow scenarios, verify user-visible behavior, document any issues found, test both happy path and error scenarios, test TOML-specific features | Success: All user scenarios work as expected, TOML configuration loads correctly, backward compatibility with .env verified, enabled/disabled filtering works, rotation works across 10+ operations, state persists correctly, errors handled gracefully, TOML syntax errors reported clearly. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

- [ ] 19. Code Review and Cleanup
  - Review all new code for quality
  - Ensure consistent code style (PEP 8)
  - Add type hints where missing
  - Update docstrings for all public methods
  - Remove debug logging
  - Optimize performance where applicable
  - Purpose: Ensure code quality and maintainability
  - _Leverage: pylint, mypy, black for formatting_
  - _Requirements: All requirements_
  - _Prompt: Implement the task for spec multi-credential-downloader. First run spec-workflow-guide to get the workflow guide then implement the task: Role: Senior Python Developer responsible for code quality | Task: Perform comprehensive code review and cleanup of all multi-credential code. Ensure PEP 8 compliance, complete type hints, proper docstrings, remove debug code, and optimize performance. | Restrictions: Follow PEP 8 strictly, ensure all public APIs documented, do not change behavior during cleanup, use automated tools (pylint, mypy, black), maintain backward compatibility | Success: All code follows PEP 8, type hints complete, docstrings comprehensive, no debug code remains, performance optimized where applicable, passes linting and type checking. Mark task as [-] when starting and [x] when complete in .spec-workflow/specs/multi-credential-downloader/tasks.md_

## Summary

**Total Tasks**: 19
**Estimated Effort**: 32-42 hours

### Task Dependencies

```
Phase 1: Core Infrastructure (Tasks 1-10)
1 → 3 (Credential model → tests)
2 (Add tomli dependency - can be done independently)
4 → 5 (Rotation state → tests)
1, 2, 4 → 6 (Models + tomli → CredentialManager core with TOML support)
6 → 7 (Manager core → validation)
7 → 8 (Validation → manager tests)
6 → 9 (Manager → ClientPool)
9 → 10 (ClientPool → tests)

Phase 2: CLI Integration (Tasks 11-14)
1-10 → 11 (All Phase 1 → CLI update)
11 → 12 (CLI update → rotation integration)
12 → 13 (Rotation → error handling)
1-13 → 14 (All → integration tests)

Phase 3: Documentation and Testing (Tasks 15-19)
1-14 → 15, 16 (All → documentation - TOML example + README)
1-16 → 17 (All → full test suite)
1-17 → 18 (All → E2E testing with TOML)
1-18 → 19 (All → final review)
```

### Quality Gates

- All unit tests passing (>80% coverage)
- All integration tests passing
- PEP 8 compliance (pylint score >8.0)
- Type checking passing (mypy --strict)
- Manual E2E testing completed
- Documentation complete and reviewed
- Backward compatibility verified
