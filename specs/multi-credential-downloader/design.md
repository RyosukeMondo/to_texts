# Multi-Credential Account Downloading - Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Interface                        │
│              (cli.py - updated)                          │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│              Credential Manager                          │
│          (credential_manager.py - new)                   │
│  - Load & validate credentials                           │
│  - Maintain credential state                             │
│  - Rotation logic                                        │
└─────────────────────────────────────────────────────────┘
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ Credential  │  │ Credential   │  │ Credential   │
│ Account 1   │  │ Account 2    │  │ Account N    │
└─────────────┘  └──────────────┘  └──────────────┘
      │                  │                  │
      └──────────────────┼──────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│               Z-Library Client Pool                      │
│          (client_pool.py - new)                          │
│  - Manage Zlibrary instances                             │
│  - Provide client for current credential                 │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│              Zlibrary API Client                         │
│              (client.py - existing)                      │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Credential Manager (`credential_manager.py`)

**Responsibilities:**
- Load credentials from `.env` file
- Validate credential format and authenticity
- Maintain credential state (active, inactive, exhausted)
- Track rotation index
- Monitor download limits

**Key Classes:**
```python
class Credential:
    - identifier: str (email or userid)
    - email: Optional[str]
    - password: Optional[str]
    - remix_userid: Optional[str]
    - remix_userkey: Optional[str]
    - status: CredentialStatus (enum)
    - last_used: datetime
    - downloads_left: int

class CredentialManager:
    - credentials: List[Credential]
    - current_index: int
    - state_file: str

    Methods:
    - load_credentials() -> List[Credential]
    - validate_credential(credential) -> bool
    - get_current_credential() -> Credential
    - rotate_credential() -> Credential
    - update_download_limit(credential, limit)
    - get_available_credentials() -> List[Credential]
    - save_state()
    - load_state()
```

### 2. Client Pool (`client_pool.py`)

**Responsibilities:**
- Maintain a pool of Zlibrary client instances
- Provide current client based on credential rotation
- Cache clients to avoid repeated logins
- Handle client authentication failures

**Key Classes:**
```python
class ZlibraryClientPool:
    - clients: Dict[str, Zlibrary]
    - credential_manager: CredentialManager

    Methods:
    - get_current_client() -> Zlibrary
    - rotate_to_next_client() -> Zlibrary
    - validate_all_clients() -> Dict[str, bool]
    - refresh_client(credential) -> Zlibrary
    - get_client_status() -> Dict[str, ClientStatus]
```

### 3. Enhanced CLI (`cli.py` - updated)

**Changes:**
- Initialize CredentialManager on startup
- Display credential status and available downloads
- Show which account is currently active
- Provide new commands for credential management
- Automatically rotate credentials after operations

## Credential Format in `.env`

```env
# Single credential (backward compatible)
ZLIBRARY_EMAIL=user@example.com
ZLIBRARY_PASSWORD=password123

# Multiple credentials (new format)
# Format: ZLIBRARY_ACCOUNT_<N>_EMAIL and ZLIBRARY_ACCOUNT_<N>_PASSWORD
# Or: ZLIBRARY_ACCOUNT_<N>_USERID and ZLIBRARY_ACCOUNT_<N>_USERKEY

# Account 1 - Email/Password
ZLIBRARY_ACCOUNT_1_EMAIL=user1@example.com
ZLIBRARY_ACCOUNT_1_PASSWORD=password1

# Account 2 - Email/Password
ZLIBRARY_ACCOUNT_2_EMAIL=user2@example.com
ZLIBRARY_ACCOUNT_2_PASSWORD=password2

# Account 3 - Remix Tokens (recommended)
ZLIBRARY_ACCOUNT_3_USERID=123456
ZLIBRARY_ACCOUNT_3_USERKEY=token_key_here

# Rotation state file location (optional)
ZLIBRARY_ROTATION_STATE_FILE=.zlibrary_rotation_state
```

## State Management

### State File Format (`~/.zlibrary_rotation_state`)
```json
{
    "current_index": 1,
    "last_rotation": "2024-10-16T12:30:45Z",
    "credentials_status": {
        "user1@example.com": {
            "last_used": "2024-10-16T12:30:45Z",
            "downloads_left": 8,
            "status": "active"
        },
        "user2@example.com": {
            "last_used": "2024-10-16T12:15:30Z",
            "downloads_left": 0,
            "status": "exhausted"
        }
    }
}
```

## Workflow Diagrams

### Search and Download Workflow
```
User Request (Search/Download)
    │
    ├─> Get current credential
    │
    ├─> Check credential status
    │   ├─> Active? Continue
    │   ├─> Exhausted? Rotate to next
    │   └─> Error? Skip and rotate
    │
    ├─> Get client from pool
    │
    ├─> Execute operation (search/download)
    │   ├─> Success? Update state
    │   └─> Fail? Log and rotate
    │
    └─> Rotate to next credential
        └─> Save state
```

### Startup Validation Workflow
```
Application Start
    │
    ├─> Load credentials from .env
    │
    ├─> Validate each credential
    │   ├─> Valid? Mark as active
    │   └─> Invalid? Mark as error
    │
    ├─> Load previous rotation state (if exists)
    │
    ├─> Display credential summary to user
    │
    └─> Ready for operations
```

## Error Handling Strategy

### Credential Validation Errors
- Log validation errors with credential identifier (not password)
- Mark credential as invalid
- Continue with next credential
- Warn user if no valid credentials found

### Download Limit Exceeded
- Check remaining downloads before operation
- Skip to next credential if limit reached
- Inform user about account exhaustion

### API Errors During Operation
- Retry with current credential (up to 2 attempts)
- On persistent failure, rotate to next credential
- Log error details for debugging

## Data Flow

### Operation Sequence
1. **User initiates search/download**
2. CredentialManager returns current credential
3. ClientPool gets or creates Zlibrary client for credential
4. Operation executes (search or download)
5. Update credential state (downloads_left)
6. Rotate to next credential
7. Save rotation state to file

## Backward Compatibility

- Support existing single credential format (ZLIBRARY_EMAIL + ZLIBRARY_PASSWORD)
- Auto-detect format (single vs. multiple credentials)
- No breaking changes to existing CLI interface
- Optional: Migrate to multi-credential format if user chooses

## Performance Considerations

- Cache Zlibrary clients to avoid repeated logins
- Lazy-load client credentials on first use
- Persist rotation state to minimize startup overhead
- Implement credential health checks periodically

## Security Considerations

- Never log or expose credentials in output
- Sanitize error messages that might contain credentials
- Secure state file permissions (user-readable only)
- Validate and sanitize credential format
- Use environment variables (via .env) for credential storage

## Testing Strategy

### Unit Tests
- Credential validation
- Rotation logic
- State persistence

### Integration Tests
- Multi-credential authentication
- Search and download with multiple accounts
- Credential rotation across operations
- Download limit handling

### E2E Tests
- Full workflow with multiple accounts
- Fallback mechanisms
- Error handling and recovery
