# Multi-Credential Account Downloading Specification

## Overview

This specification outlines the implementation of multi-credential support for the Z-Library downloader. The feature enables users to configure multiple Z-Library accounts and the system will automatically rotate through them to avoid rate limiting and API access throttling.

## Document Structure

### 1. **requirements.md**
Defines all functional and non-functional requirements for the feature:
- Multiple credentials management
- Credential rotation strategy
- Search and download operations
- Rate limiting management
- Configuration and state management
- User stories and acceptance criteria

### 2. **design.md**
Provides the technical design and architecture:
- System architecture overview
- Core components (CredentialManager, ClientPool)
- Data models and class structures
- Credential format in `.env` file
- State management and persistence
- Workflow diagrams
- Error handling strategy
- Security and performance considerations

### 3. **tasks.md**
Details all implementation tasks organized by phase:
- **Phase 1:** Core infrastructure (5 tasks)
- **Phase 2:** CLI integration (2 tasks)
- **Phase 3:** Enhanced features (2 tasks)
- **Phase 4:** Testing & documentation (2 tasks)
- **Phase 5:** Validation & release (2 tasks)

Total: 12 implementation tasks

## Key Features

### Multi-Credential Support
- Load multiple credentials from `.env` file
- Support both email/password and remix token authentication
- Validate credentials on startup
- Display credential status and available downloads

### Automatic Rotation
- Round-robin credential rotation after each operation
- Transparent to the user
- Persistent state tracking
- Skip exhausted or invalid credentials

### Rate Limiting Handling
- Track download limits per credential
- Pre-check before operations
- Automatic fallback to next available account
- Clear user feedback on quota status

### Backward Compatibility
- Support existing single-credential setup
- Auto-detect credential format
- No breaking changes to existing CLI

## Credential Configuration Format

### Single Credential (Existing)
```env
ZLIBRARY_EMAIL=user@example.com
ZLIBRARY_PASSWORD=password123
```

### Multiple Credentials (New)
```env
# Account 1
ZLIBRARY_ACCOUNT_1_EMAIL=user1@example.com
ZLIBRARY_ACCOUNT_1_PASSWORD=password1

# Account 2
ZLIBRARY_ACCOUNT_2_EMAIL=user2@example.com
ZLIBRARY_ACCOUNT_2_PASSWORD=password2

# Account 3 (Remix tokens - recommended)
ZLIBRARY_ACCOUNT_3_USERID=123456
ZLIBRARY_ACCOUNT_3_USERKEY=token_key
```

## Component Architecture

```
CLI Interface
    ↓
Credential Manager (load, validate, rotate)
    ↓
Client Pool (manage Zlibrary instances)
    ↓
Zlibrary API Client
    ↓
Z-Library Service
```

## Implementation Phases

### Phase 1: Core Infrastructure
- Credential data model
- Credential manager
- State persistence
- Client pool

### Phase 2: CLI Integration
- Multi-credential loading
- Automatic rotation integration
- Status display

### Phase 3: Enhanced Features
- Download limit tracking
- Graceful fallback handling

### Phase 4: Testing & Documentation
- Comprehensive test suite
- User documentation

### Phase 5: Validation & Release
- End-to-end testing
- Code review and cleanup

## Expected Outcomes

1. **User can configure multiple Z-Library accounts** in `.env` file
2. **System automatically rotates credentials** after each operation
3. **Transparent credential management** without user intervention
4. **Clear feedback** on account status and quota
5. **Graceful handling** of rate limits and account exhaustion
6. **Backward compatible** with single-credential setup

## Success Criteria

- [ ] Multiple credentials can be configured and validated
- [ ] Automatic rotation works correctly
- [ ] Download limits are tracked and enforced
- [ ] Fallback mechanisms handle credential failures
- [ ] All tests pass with good coverage
- [ ] Documentation is clear and complete
- [ ] No breaking changes to existing functionality

## Integration Notes

- Minimal changes to existing `cli.py`
- New modules follow existing code style
- Backward compatible with current setup
- Optional state file (`.zlibrary_rotation_state`)
- Uses existing Zlibrary client implementation

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Credential leakage | Use environment variables, sanitize logs |
| State file corruption | Handle gracefully, regenerate if needed |
| API rate limits | Implement intelligent rotation and limits check |
| Backward compatibility | Support both old and new formats |
| Performance impact | Cache clients, lazy-load on demand |

## Next Steps

1. Review and approve specification
2. Begin Phase 1 implementation
3. Implement core infrastructure (CredentialManager, ClientPool)
4. Integrate with CLI
5. Comprehensive testing
6. User documentation
7. Release and monitor

---

**Status:** Ready for Implementation
**Last Updated:** 2024-10-16
**Version:** 1.0
