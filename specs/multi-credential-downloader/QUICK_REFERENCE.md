# Multi-Credential Downloader - Quick Reference

## What Is This Spec About?

Enable the Z-Library downloader to use **multiple accounts automatically**, rotating through them to avoid hitting rate limits and download quotas on a single account.

## The Problem

Currently:
- Only 1 Z-Library account can be configured
- Limited downloads per day/account
- Risk of hitting API rate limits
- No way to distribute load across accounts

## The Solution

Users will:
1. Configure multiple credentials in `.env` file
2. System automatically switches accounts after each search/download
3. Tracks remaining downloads per account
4. Skips accounts that have reached their limits
5. Provides clear feedback on which account is active

## Quick Config Example

```env
# Multiple accounts
ZLIBRARY_ACCOUNT_1_EMAIL=account1@example.com
ZLIBRARY_ACCOUNT_1_PASSWORD=pass1

ZLIBRARY_ACCOUNT_2_EMAIL=account2@example.com
ZLIBRARY_ACCOUNT_2_PASSWORD=pass2

ZLIBRARY_ACCOUNT_3_USERID=123456
ZLIBRARY_ACCOUNT_3_USERKEY=remix_token
```

## How It Works

```
Search with Account 1 ➜ Rotate ➜ Search with Account 2 ➜ Rotate ➜ Search with Account 3 ➜ Rotate...
```

## Key Components

| Component | Purpose |
|-----------|---------|
| **CredentialManager** | Load and manage all credentials |
| **ClientPool** | Keep Z-Library clients ready for each account |
| **RotationState** | Remember which account was used last |
| **Updated CLI** | Show account status and integrate rotation |

## What Gets Built

### New Files
- `credential.py` - Credential model
- `credential_manager.py` - Credential management
- `client_pool.py` - Client pool
- `rotation_state.py` - State persistence

### Modified Files
- `cli.py` - Add rotation logic
- `__init__.py` - Export new classes
- `README.md` - Update docs

### Documentation
- `.env.example` - Example config
- `multi-credential-guide.md` - User guide

## Implementation Timeline

| Phase | Tasks | Time |
|-------|-------|------|
| 1. Infrastructure | Core classes | 8-10h |
| 2. Integration | CLI updates | 4-6h |
| 3. Features | Limits & fallback | 4-6h |
| 4. Testing | Test suite | 6-8h |
| 5. Docs & Polish | Documentation | 7-10h |
| **Total** | **12 tasks** | **29-40h** |

## Features Included

✅ Support multiple credentials (email/password or remix tokens)
✅ Automatic rotation with persistent state
✅ Download limit tracking per account
✅ Graceful fallback when account exhausted
✅ Clear status display on startup
✅ Backward compatible with single account
✅ Comprehensive test coverage
✅ Full documentation

## Before Implementation Checklist

- [ ] Review requirements.md
- [ ] Review design.md
- [ ] Review tasks.md
- [ ] Understand the architecture
- [ ] Plan development phases
- [ ] Set up test infrastructure
- [ ] Prepare CI/CD if needed

## Usage Flow (After Implementation)

1. **Setup:** Add multiple credentials to `.env`
2. **Start:** Run app, see all accounts' status
3. **Search:** System uses Account 1
4. **Download:** System rotates to Account 2
5. **Search Again:** System uses Account 3
6. **Repeat:** Cycle continues, skipping exhausted accounts

## Success Metrics

- Users can configure and use multiple accounts
- Rotation works transparently
- No duplicate downloads
- Clear feedback on account status
- All existing features still work
- Tests have good coverage

## Questions?

Refer to:
- **What needs building?** → `tasks.md`
- **How does it work?** → `design.md`
- **What are the rules?** → `requirements.md`
- **How to set it up?** → `multi-credential-guide.md` (to be written)

---

**Spec Status:** ✅ Complete and Ready for Implementation
**Created:** 2024-10-16
