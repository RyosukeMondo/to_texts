# Multi-Credential Account Downloading - Requirements

## Overview
Enable the Z-Library downloader to support multiple credentials, allowing the system to perform search and download operations while rotating through different accounts to avoid rate limiting and API access throttling.

## Functional Requirements

### FR1: Multiple Credentials Management
- Support storing multiple Z-Library account credentials in `.env` file
- Support both email/password and remix token authentication methods
- Allow users to configure unlimited number of credentials
- Validate credentials on startup and track their status

### FR2: Credential Rotation Strategy
- Implement round-robin credential rotation for search operations
- Track which credential was last used for searches
- Move to next credential after each search/download operation
- Maintain state of credential index in a persistent file or database

### FR3: Search and Download Operations
- Perform search operations using the current active credential
- Download books using the current active credential
- Automatically rotate to next credential after successful operation
- Handle credential exhaustion gracefully (check download limits)

### FR4: Rate Limiting Management
- Track download limits per credential
- Check available downloads before operations
- Automatically skip credentials that have reached their limit
- Provide user feedback on remaining downloads per account

### FR5: Configuration and State Management
- Load credentials from `.env` file with a standardized format
- Store credential rotation state persistently
- Support credential validation and health checks
- Log credential usage for debugging and monitoring

## Non-Functional Requirements

### NFR1: Performance
- Credential rotation should add minimal overhead
- State management should not introduce delays

### NFR2: Reliability
- Handle credential failures gracefully
- Prevent data loss during credential rotation
- Recover from interrupted operations

### NFR3: Usability
- Clear feedback to user about which credential is being used
- Display remaining downloads per account
- Provide helpful error messages

### NFR4: Security
- Protect stored credentials appropriately
- Don't expose credentials in logs or error messages
- Validate credential format before use

## User Stories

### US1: Configure Multiple Accounts
**As a** user
**I want to** configure multiple Z-Library accounts in my `.env` file
**So that** I can distribute my download quota across different accounts

**Acceptance Criteria:**
- User can add multiple credentials with clear formatting
- System validates all credentials on startup
- User sees status of each account (active, inactive, error)

### US2: Automatic Credential Rotation
**As a** user
**I want the** system to automatically switch accounts after each search/download
**So that** I avoid hitting rate limits on a single account

**Acceptance Criteria:**
- Each operation uses a different credential
- System tracks which credential is currently active
- Rotation happens transparently without user intervention

### US3: Monitor Account Status
**As a** user
**I want to** see how many downloads are left on each account
**So that** I can understand my available quota

**Acceptance Criteria:**
- Display remaining downloads per account before operations
- Show which account is currently active
- Warn when accounts are approaching limits

### US4: Handle Rate Limiting
**As a** user
**I want the** system to handle rate limiting gracefully
**So that** operations don't fail unexpectedly

**Acceptance Criteria:**
- Skip accounts that have reached limits
- Fall back to next available account
- Provide clear error messages when all accounts are exhausted

## Dependencies
- Existing Z-Library client implementation
- Python environment with required packages
- `.env` file for credential storage

## Constraints
- Must maintain backward compatibility with single-credential setup
- Rate limiting imposed by Z-Library API
- Download limits per account

## Success Metrics
- User can configure and use multiple accounts
- Credential rotation works transparently
- No duplicate downloads or missed operations
- Clear user feedback on account status and operations
