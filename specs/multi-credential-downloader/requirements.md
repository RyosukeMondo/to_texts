# Multi-Credential Account Downloading - Requirements

## Overview
Enable the Z-Library downloader to support multiple credentials, allowing the system to perform search and download operations while rotating through different accounts to avoid rate limiting and API access throttling.

## Problem Statement
Currently, users can only configure a single Z-Library account credential. This creates the following issues:
- Limited downloads per day (hitting account limits quickly)
- Risk of API rate limiting if multiple searches/downloads are performed
- No way to distribute load across multiple accounts
- Users need manual workarounds to manage multiple accounts

## Solution
Implement automatic credential rotation that allows users to:
1. Configure multiple Z-Library credentials in `.env`
2. Have the system automatically switch between accounts after each operation
3. Track download limits and skip exhausted accounts
4. Receive clear feedback on account status and remaining quotas

## Functional Requirements

### FR1: Multiple Credentials Management
- System shall support storing multiple Z-Library account credentials
- System shall support both email/password and remix token authentication methods
- System shall validate all credentials on startup
- System shall display status of each credential (valid, invalid, exhausted)

### FR2: Credential Rotation Strategy
- System shall implement round-robin credential rotation
- System shall track which credential was last used
- System shall move to next credential after each search/download operation
- System shall persist rotation state between application restarts

### FR3: Search and Download Operations
- System shall perform search using current active credential
- System shall perform downloads using current active credential
- System shall automatically rotate to next credential after successful operation
- System shall handle credential failures gracefully

### FR4: Rate Limiting Management
- System shall fetch and track download limits per credential
- System shall check available downloads before operations
- System shall automatically skip credentials that have reached their limit
- System shall provide user feedback on remaining downloads per account

### FR5: Configuration and State Management
- System shall load credentials from `.env` file with standard format
- System shall store credential rotation state persistently
- System shall support credential validation and health checks
- System shall provide clear error messages for configuration issues

## Non-Functional Requirements

### NFR1: Performance
- Credential rotation shall add <100ms overhead per operation
- Client caching shall avoid repeated authentication
- State file I/O shall be optimized

### NFR2: Reliability
- System shall handle credential failures without data loss
- System shall recover from interrupted operations
- System shall validate state file integrity

### NFR3: Usability
- Users shall receive clear feedback on which credential is active
- Display remaining downloads per account
- Provide helpful error messages for common issues

### NFR4: Security
- Credentials shall not be exposed in logs or error messages
- State file shall have restricted permissions
- Input validation on all credential data

## User Stories

### US1: Configure Multiple Accounts
**As a** power user
**I want to** configure multiple Z-Library accounts in my `.env` file
**So that** I can distribute my download quota across different accounts

**Acceptance Criteria:**
- [ ] User can add multiple credentials with clear formatting
- [ ] System validates all credentials on startup
- [ ] User sees status of each account (valid, invalid, error)
- [ ] Clear error messages if credentials are invalid

### US2: Automatic Credential Rotation
**As a** user
**I want the** system to automatically switch accounts after each search/download
**So that** I avoid hitting rate limits on a single account

**Acceptance Criteria:**
- [ ] Each operation uses a different credential
- [ ] System rotates transparently without user intervention
- [ ] Rotation state persists between restarts
- [ ] User can see which account was used

### US3: Monitor Account Status
**As a** user
**I want to** see how many downloads are left on each account
**So that** I can understand my available quota

**Acceptance Criteria:**
- [ ] Display remaining downloads per account before operations
- [ ] Show which account is currently active
- [ ] Warn when accounts are approaching limits
- [ ] Clear indication when account is exhausted

### US4: Handle Rate Limiting
**As a** user
**I want the** system to handle rate limiting gracefully
**So that** operations don't fail unexpectedly

**Acceptance Criteria:**
- [ ] Skip accounts that have reached limits
- [ ] Fall back to next available account automatically
- [ ] Clear error messages when all accounts exhausted
- [ ] Log credential rotation for debugging

## Dependencies
- Existing Z-Library client implementation (zlibrary_downloader/client.py)
- Python 3.8+
- python-dotenv library
- Existing CLI structure

## Constraints
- Must maintain backward compatibility with single-credential setup
- Rate limiting imposed by Z-Library API (download limits per account)
- State file must be human-readable (JSON format)

## Success Metrics
- Users can configure and use 3+ accounts simultaneously
- Credential rotation works transparently across 50+ operations
- No duplicate downloads or missed operations
- >80% test coverage for new functionality
- Clear user feedback on account status and operations
