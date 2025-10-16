# Requirements Document

## Introduction

The Multi-Credential Account Downloading feature enables the Z-Library downloader to support multiple credentials, allowing the system to perform search and download operations while rotating through different accounts to avoid rate limiting and API access throttling. This feature addresses the critical limitation of single-account usage that leads to rapid quota exhaustion and operational interruptions.

## Alignment with Product Vision

This feature enhances the reliability and scalability of the Z-Library downloader by:
- Enabling power users to maximize their download capacity across multiple accounts
- Reducing operational friction by automating credential management
- Improving system resilience through automatic failover between accounts
- Supporting production-grade usage patterns for batch downloading workflows

## Requirements

### Requirement 1: Multiple Credentials Management

**User Story:** As a power user, I want to configure multiple Z-Library accounts in my `.env` file, so that I can distribute my download quota across different accounts

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL load all configured credentials from the `.env` file
2. WHEN credentials are loaded THEN the system SHALL support both email/password and remix token authentication methods
3. WHEN credentials are loaded THEN the system SHALL validate each credential by authenticating with the Z-Library API
4. WHEN validation completes THEN the system SHALL display the status of each credential (valid, invalid, exhausted)
5. IF any credential is invalid THEN the system SHALL provide clear error messages indicating which credential failed and why

### Requirement 2: Credential Rotation Strategy

**User Story:** As a user, I want the system to automatically switch accounts after each search/download, so that I avoid hitting rate limits on a single account

#### Acceptance Criteria

1. WHEN an operation completes THEN the system SHALL implement round-robin credential rotation
2. WHEN rotating THEN the system SHALL track which credential was last used
3. WHEN rotating THEN the system SHALL move to the next credential after each search/download operation
4. WHEN the application restarts THEN the system SHALL persist rotation state and resume from the last position
5. WHEN a credential fails THEN the system SHALL skip to the next available credential automatically

### Requirement 3: Search and Download Operations

**User Story:** As a user, I want seamless search and download operations using the active credential, so that I can perform my tasks without manual intervention

#### Acceptance Criteria

1. WHEN a search is initiated THEN the system SHALL perform the search using the current active credential
2. WHEN a download is initiated THEN the system SHALL perform the download using the current active credential
3. WHEN an operation succeeds THEN the system SHALL automatically rotate to the next credential
4. WHEN a credential fails during operation THEN the system SHALL handle the failure gracefully and retry with the next credential
5. WHEN all credentials fail THEN the system SHALL provide a clear error message to the user

### Requirement 4: Rate Limiting Management

**User Story:** As a user, I want to see how many downloads are left on each account, so that I can understand my available quota

#### Acceptance Criteria

1. WHEN credentials are validated THEN the system SHALL fetch and track download limits per credential
2. WHEN an operation is about to execute THEN the system SHALL check available downloads before proceeding
3. WHEN a credential reaches its limit THEN the system SHALL automatically skip credentials that have reached their limit
4. WHEN operations are performed THEN the system SHALL provide user feedback on remaining downloads per account
5. WHEN accounts are approaching limits THEN the system SHALL warn the user
6. WHEN an account is exhausted THEN the system SHALL provide clear indication and skip to the next account

### Requirement 5: Configuration and State Management

**User Story:** As a user, I want persistent credential state management, so that my rotation status is maintained across application restarts

#### Acceptance Criteria

1. WHEN the application starts THEN the system SHALL load credentials from the `.env` file with standard format
2. WHEN rotation occurs THEN the system SHALL store credential rotation state persistently in a state file
3. WHEN credentials are used THEN the system SHALL support credential validation and health checks
4. IF configuration issues exist THEN the system SHALL provide clear error messages for configuration issues
5. WHEN state is persisted THEN the system SHALL ensure the state file is human-readable (JSON format)

## Non-Functional Requirements

### Code Architecture and Modularity
- **Single Responsibility Principle**: Each module (Credential, CredentialManager, ClientPool, RotationState) should have a single, well-defined purpose
- **Modular Design**: Components should be isolated and reusable, with clear separation between credential management, client pooling, and state persistence
- **Dependency Management**: Minimize interdependencies between modules - ClientPool depends on CredentialManager, but both are independent of CLI
- **Clear Interfaces**: Define clean contracts between components (Credential data model, CredentialManager API, ClientPool API)

### Performance
- Credential rotation SHALL add <100ms overhead per operation
- Client caching SHALL avoid repeated authentication
- State file I/O SHALL be optimized to minimize disk access
- Credential validation on startup SHALL complete within 5 seconds for up to 10 accounts

### Security
- Credentials SHALL NOT be exposed in logs or error messages
- State file SHALL have restricted permissions (chmod 600 on Unix systems)
- Input validation SHALL be applied on all credential data
- Passwords SHALL be handled securely and never printed to console

### Reliability
- System SHALL handle credential failures without data loss
- System SHALL recover from interrupted operations
- System SHALL validate state file integrity before loading
- System SHALL maintain backward compatibility with single-credential setup

### Usability
- Users SHALL receive clear feedback on which credential is active
- Display remaining downloads per account at appropriate times
- Provide helpful error messages for common configuration issues
- Configuration format SHALL be intuitive and well-documented
