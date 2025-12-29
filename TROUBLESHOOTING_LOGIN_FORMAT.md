# Troubleshooting: Login Request Format

## Problem

Getting validation error when trying to login:
```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR",
  "message": "identifier is required",
  "details": {
    "errors": [{
      "field": "identifier",
      "error_code": "MISSING_IDENTIFIER",
      "message": "identifier is required",
      "path": "body.identifier"
    }]
  }
}
```

## Root Cause

The auth-service login endpoint expects a **different request format** than what you're sending.

**Wrong format:**
```json
{
  "username": "alex.w",
  "password": "Ax9!kP3#Lm2Q"
}
```

**Correct format:**
```json
{
  "login_type": "username",
  "identifier": "alex.w",
  "password": "Ax9!kP3#Lm2Q"
}
```

## Solution

### Correct Request Format

The auth-service uses a flexible login system that supports multiple login methods:

```bash
# Login with username
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login_type": "username",
    "identifier": "alex.w",
    "password": "Ax9!kP3#Lm2Q"
  }'

# Login with email
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login_type": "email",
    "identifier": "alex.w@example.com",
    "password": "Ax9!kP3#Lm2Q"
  }'

# Login with phone
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login_type": "phone",
    "identifier": "+1234567890",
    "password": "Ax9!kP3#Lm2Q"
  }'
```

### Request Fields

| Field | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `login_type` | string | No (default: "username") | Login method type | `"username"`, `"email"`, `"phone"` |
| `identifier` | string | **Yes** | Username, email, or phone number | Any string |
| `password` | string | **Yes** | User password | Any string (min length: 1) |

### Examples

#### Example 1: Username Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login_type": "username",
    "identifier": "alex.w",
    "password": "Ax9!kP3#Lm2Q"
  }'
```

#### Example 2: Email Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login_type": "email",
    "identifier": "alex.w@example.com",
    "password": "Ax9!kP3#Lm2Q"
  }'
```

#### Example 3: Phone Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login_type": "phone",
    "identifier": "+1234567890",
    "password": "Ax9!kP3#Lm2Q"
  }'
```

#### Example 4: Default (Username)
```bash
# login_type is optional, defaults to "username"
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "alex.w",
    "password": "Ax9!kP3#Lm2Q"
  }'
```

## Expected Response

### Success Response (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_expires_in": 604800
}
```

### Error Responses

#### User Not Found (404)
```json
{
  "status": "error",
  "error_code": "USER_NOT_FOUND",
  "message": "User with identifier 'alex.w' not found"
}
```

#### Invalid Password (400)
```json
{
  "status": "error",
  "error_code": "INVALID_PASSWORD",
  "message": "Invalid password"
}
```

#### User Inactive (403)
```json
{
  "status": "error",
  "error_code": "USER_INACTIVE",
  "message": "User account is inactive"
}
```

## Quick Reference

### Correct Command
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login_type": "username", "identifier": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

### Wrong Command (Don't Use)
```bash
# ❌ Wrong - uses "username" instead of "identifier"
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

## Testing

### Test Direct Connection
```bash
# Test directly to auth-service (bypass gateway)
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login_type": "username",
    "identifier": "alex.w",
    "password": "Ax9!kP3#Lm2Q"
  }'
```

### Test Through Gateway
```bash
# Test through gateway
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login_type": "username",
    "identifier": "alex.w",
    "password": "Ax9!kP3#Lm2Q"
  }'
```

## API Documentation

For complete API documentation, see:
- `API_DOCUMENTATION.md` in auth-service
- OpenAPI schema: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Summary

**Key Points:**
- ✅ Use `identifier` (not `username`)
- ✅ Include `login_type` (optional, defaults to "username")
- ✅ Use `password` field

**Correct Format:**
```json
{
  "login_type": "username",
  "identifier": "alex.w",
  "password": "Ax9!kP3#Lm2Q"
}
```
