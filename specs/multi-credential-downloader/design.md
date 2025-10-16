# Multi-Credential Account Downloading - Design

## Architecture Overview

```
┌──────────────────────────────────────────────┐
│         CLI Interface (cli.py)               │
│    Entry point for all operations            │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│     Credential Manager (NEW)                 │
│  • Load credentials from .env                │
│  • Validate credentials                      │
│  • Track rotation state                      │
│  • Manage credential lifecycle               │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│      Client Pool (NEW)                       │
│  • Cache Zlibrary client instances           │
│  • Manage credential rotation                │
│  • Provide current client                    │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│   Zlibrary API Client (existing)             │
│  • Search & download operations              │
│  • API interaction                           │
└──────────────────────┬───────────────────────┘
                       │
                  Z-Library API
```

## Core Components

### 1. Credential Data Model
**File:** `zlibrary_downloader/credential.py`

```python
class CredentialStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    EXHAUSTED = "exhausted"

class Credential:
    identifier: str          # Email or user ID (for identification)
    email: Optional[str]     # For email/password auth
    password: Optional[str]
    remix_userid: Optional[str]  # For remix token auth
    remix_userkey: Optional[str]
    status: CredentialStatus
    downloads_left: int
    last_used: datetime
    last_validated: datetime
```

### 2. Credential Manager
**File:** `zlibrary_downloader/credential_manager.py`

```python
class CredentialManager:
    credentials: List[Credential]
    current_index: int
    state_file: str

    Methods:
    - load_credentials() -> List[Credential]
        # Load from .env, support multiple formats
    - validate_credential(cred) -> bool
        # Check if credential works
    - get_current() -> Credential
        # Return currently active credential
    - rotate() -> Credential
        # Move to next valid credential
    - update_downloads_left(cred, limit)
        # Update remaining downloads
    - get_available() -> List[Credential]
        # Get non-exhausted credentials
    - save_state() -> None
        # Persist state to file
    - load_state() -> None
        # Load state from file
```

### 3. Client Pool
**File:** `zlibrary_downloader/client_pool.py`

```python
class ZlibraryClientPool:
    clients: Dict[str, Zlibrary]
    credential_manager: CredentialManager

    Methods:
    - get_current_client() -> Zlibrary
        # Get client for current credential
    - rotate_client() -> Zlibrary
        # Rotate and get next client
    - validate_all() -> Dict[str, bool]
        # Test all credentials
    - refresh_client(credential)
        # Create new client for credential
```

## Credential Format in .env

### Single Credential (Backward Compatible)
```env
ZLIBRARY_EMAIL=user@example.com
ZLIBRARY_PASSWORD=password123
```

### Multiple Credentials (New)
```env
# Account 1 - Email/Password
ZLIBRARY_ACCOUNT_1_EMAIL=user1@example.com
ZLIBRARY_ACCOUNT_1_PASSWORD=password1

# Account 2 - Email/Password
ZLIBRARY_ACCOUNT_2_EMAIL=user2@example.com
ZLIBRARY_ACCOUNT_2_PASSWORD=password2

# Account 3 - Remix Tokens (Recommended)
ZLIBRARY_ACCOUNT_3_USERID=123456789
ZLIBRARY_ACCOUNT_3_USERKEY=remix_token_key_here

# Optional: State file location
ZLIBRARY_ROTATION_STATE_FILE=.zlibrary_rotation_state
```

## State Persistence

### State File Format (.zlibrary_rotation_state)
```json
{
    "current_index": 1,
    "last_rotation": "2024-10-16T12:30:45Z",
    "credentials_status": {
        "user1@example.com": {
            "last_used": "2024-10-16T12:30:45Z",
            "downloads_left": 8,
            "status": "valid"
        },
        "user2@example.com": {
            "last_used": "2024-10-16T12:15:30Z",
            "downloads_left": 0,
            "status": "exhausted"
        }
    }
}
```

## Workflow: Search and Download

```
User initiates search/download
    │
    ├─> Get current credential
    │   (from CredentialManager)
    │
    ├─> Check credential status
    │   ├─ Valid? Continue
    │   ├─ Exhausted? Rotate
    │   └─ Invalid? Rotate & retry
    │
    ├─> Get Zlibrary client
    │   (from ClientPool cache)
    │
    ├─> Execute operation
    │   (search or download)
    │
    ├─> On success:
    │   ├─ Update download count
    │   └─ Rotate to next credential
    │
    ├─> On failure:
    │   ├─ Log error
    │   ├─ Retry with next credential
    │   └─ If all fail, error to user
    │
    └─> Save state
        (persist rotation index)
```

## Workflow: Startup Validation

```
Application starts
    │
    ├─> Load credentials from .env
    │   (support both old and new format)
    │
    ├─> Create Credential objects
    │
    ├─> Load previous state (if exists)
    │
    ├─> Validate each credential
    │   ├─ Create test Zlibrary client
    │   ├─ Call getProfile() to test
    │   ├─ Set status (valid/invalid)
    │   └─ Fetch download limits
    │
    ├─> Initialize ClientPool
    │   (with validated credentials)
    │
    ├─> Display summary to user
    │   (account count, available downloads)
    │
    └─> Ready for operations
```

## Error Handling

### Credential Validation Errors
- Log validation error with identifier (not password)
- Mark credential as INVALID
- Continue with next credential
- Warn user if no valid credentials

### Download Limit Exceeded
- Check remaining before operation
- Skip to next if limit reached
- Inform user about exhaustion
- Continue with next available

### API Errors During Operation
- Retry up to 2 times with current credential
- On persistent failure, rotate and retry with next
- If all credentials fail, return error to user
- Log all attempts for debugging

## Data Flow: Credential Rotation

```
Operation Complete
    │
    ├─> CredentialManager.rotate()
    │   ├─ Increment current_index
    │   ├─ Skip exhausted credentials
    │   └─ Wrap around if at end
    │
    ├─> Update state
    │   ├─ Save new index
    │   └─ Update timestamp
    │
    └─> ClientPool updates
        (internal index synced)
```

## Integration with Existing Code

### Changes to cli.py
- Update `load_credentials()` to use CredentialManager
- Update `initialize_zlibrary()` to use ClientPool
- Add rotation after search_books()
- Add rotation after download_book()
- Display credential status on startup

### New Environment Detection
- Check for `ZLIBRARY_ACCOUNT_1_*` variables first
- Fall back to `ZLIBRARY_EMAIL` + `ZLIBRARY_PASSWORD` if multi not found
- Support both formats transparently

## Backward Compatibility

- Single credential format still works unchanged
- Auto-detect format (single vs multi)
- No breaking changes to CLI interface
- Existing scripts/tools continue to work

## Security Considerations

- Never log credentials (username yes, password no)
- Sanitize error messages (no credential info)
- State file permissions: user-readable only (chmod 600)
- Validate all credential inputs
- No credential exposure in output

## Performance Considerations

- Cache Zlibrary clients to avoid repeated logins
- Lazy-load credentials on first use
- Persist state to minimize startup overhead
- Async validation optional for large credential sets

## Testing Strategy

### Unit Tests
- Credential loading and validation
- Rotation logic and state transitions
- State file save/load

### Integration Tests
- Multi-credential authentication
- Search with rotation
- Download with rotation
- Fallback mechanisms

### End-to-End Tests
- Full workflow with 2-3 accounts
- Credential exhaustion scenarios
- Error recovery

### Performance Tests
- Rotation overhead per operation
- State file I/O performance
