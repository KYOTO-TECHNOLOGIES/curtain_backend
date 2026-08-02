# Curtain Master API README

This project is a Django + DRF + JWT CRM backend.

Base URL examples below assume:

```text
http://localhost:8000/api/
```

## Auth Overview

- JWT access token is accepted from:
  - `Authorization: Bearer <token>`
  - `access_token` cookie
- Refresh token is accepted from:
  - request body field `refresh`
  - `refresh_token` cookie
- Login stores both JWT tokens in `HttpOnly` cookies
- Logout clears both cookies and blacklists the refresh token when present

## Default Admin User

Created during the first migration:

```text
email: admin@kyotosoftware.com
password: Abcd@123
```

## Auth Endpoints

### 1. Login

**Endpoint**

```text
POST /api/auth/login/
```

**Request**

```json
{
  "email": "admin@kyotosoftware.com",
  "password": "Abcd@123"
}
```

**Success Response**

```json
{
  "user": {
    "id": 1,
    "email": "admin@kyotosoftware.com",
    "full_name": "Curtain Master Admin",
    "role": {
      "id": 1,
      "name": "Administrator",
      "description": "Default system administrator role.",
      "is_active": true,
      "permissions": [],
      "created_at": "2026-07-18T10:30:00Z",
      "updated_at": "2026-07-18T10:30:00Z"
    },
    "is_active": true,
    "is_staff": true,
    "created_at": "2026-07-18T10:30:00Z",
    "updated_at": "2026-07-18T10:30:00Z"
  },
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

**Error Response**

```json
{
  "detail": "Invalid email or password."
}
```

### 2. Refresh Token

**Endpoint**

```text
POST /api/auth/refresh/
```

**Request**

```json
{
  "refresh": "<jwt_refresh_token>"
}
```

You can also call this without body if the `refresh_token` cookie exists.

**Success Response**

```json
{
  "access": "<new_jwt_access_token>",
  "refresh": "<same_jwt_refresh_token>",
  "user": {
    "id": 1,
    "email": "admin@kyotosoftware.com",
    "full_name": "Curtain Master Admin",
    "role": {
      "id": 1,
      "name": "Administrator",
      "description": "Default system administrator role.",
      "is_active": true,
      "permissions": [],
      "created_at": "2026-07-18T10:30:00Z",
      "updated_at": "2026-07-18T10:30:00Z"
    },
    "is_active": true,
    "is_staff": true,
    "created_at": "2026-07-18T10:30:00Z",
    "updated_at": "2026-07-18T10:30:00Z"
  }
}
```

**Missing Refresh Response**

```json
{
  "detail": "Refresh token is required."
}
```

**Invalid Refresh Response**

```json
{
  "detail": "Invalid or expired refresh token."
}
```

### 3. Logout

**Endpoint**

```text
POST /api/auth/logout/
```

**Request**

```json
{
  "refresh": "<jwt_refresh_token>"
}
```

You can also call this using only the `refresh_token` cookie.

**Success Response**

```json
{
  "detail": "Logged out successfully."
}
```

### 4. Current Logged-In User

**Endpoint**

```text
GET /api/auth/me/
```

**Headers**

```text
Authorization: Bearer <jwt_access_token>
```

**Success Response**

```json
{
  "id": 1,
  "email": "admin@kyotosoftware.com",
  "full_name": "Curtain Master Admin",
  "role": {
    "id": 1,
    "name": "Administrator",
    "description": "Default system administrator role.",
    "is_active": true,
    "permissions": [],
    "created_at": "2026-07-18T10:30:00Z",
    "updated_at": "2026-07-18T10:30:00Z"
  },
  "is_active": true,
  "is_staff": true,
  "created_at": "2026-07-18T10:30:00Z",
  "updated_at": "2026-07-18T10:30:00Z"
}
```

## User APIs

Users can be created only by admin.

### 5. List Users

**Endpoint**

```text
GET /api/users/
```

**Auth**

- Admin only

**Response**

```json
[
  {
    "id": 1,
    "email": "admin@kyotosoftware.com",
    "full_name": "Curtain Master Admin",
    "role": {
      "id": 1,
      "name": "Administrator",
      "description": "Default system administrator role.",
      "is_active": true,
      "permissions": [],
      "created_at": "2026-07-18T10:30:00Z",
      "updated_at": "2026-07-18T10:30:00Z"
    },
    "is_active": true,
    "is_staff": true,
    "created_at": "2026-07-18T10:30:00Z",
    "updated_at": "2026-07-18T10:30:00Z"
  }
]
```

### 6. Create User

**Endpoint**

```text
POST /api/users/
```

**Auth**

- Admin only

**Request**

```json
{
  "email": "manager@curtainmaster.com",
  "full_name": "Sales Manager",
  "password": "StrongPass123",
  "role_id": 1
}
```

**Success Response**

```json
{
  "id": 2,
  "email": "manager@curtainmaster.com",
  "full_name": "Sales Manager",
  "role": {
    "id": 1,
    "name": "Administrator",
    "description": "Default system administrator role.",
    "is_active": true,
    "permissions": [],
    "created_at": "2026-07-18T10:30:00Z",
    "updated_at": "2026-07-18T10:30:00Z"
  },
  "is_active": true,
  "is_staff": false,
  "created_at": "2026-07-18T10:45:00Z",
  "updated_at": "2026-07-18T10:45:00Z"
}
```

### 7. Get Single User

**Endpoint**

```text
GET /api/users/{id}/
```

**Auth**

- Admin can view any user
- Normal user can view only their own record

**Success Response**

```json
{
  "id": 2,
  "email": "manager@curtainmaster.com",
  "full_name": "Sales Manager",
  "role": {
    "id": 1,
    "name": "Administrator",
    "description": "Default system administrator role.",
    "is_active": true,
    "permissions": [],
    "created_at": "2026-07-18T10:30:00Z",
    "updated_at": "2026-07-18T10:30:00Z"
  },
  "is_active": true,
  "is_staff": false,
  "created_at": "2026-07-18T10:45:00Z",
  "updated_at": "2026-07-18T10:45:00Z"
}
```

### 8. Update User

**Endpoint**

```text
PATCH /api/users/{id}/
```

**Request**

```json
{
  "full_name": "Updated Sales Manager",
  "role_id": 1,
  "is_active": true
}
```

**Success Response**

```json
{
  "id": 2,
  "email": "manager@curtainmaster.com",
  "full_name": "Updated Sales Manager",
  "role": {
    "id": 1,
    "name": "Administrator",
    "description": "Default system administrator role.",
    "is_active": true,
    "permissions": [],
    "created_at": "2026-07-18T10:30:00Z",
    "updated_at": "2026-07-18T10:30:00Z"
  },
  "is_active": true,
  "is_staff": false,
  "created_at": "2026-07-18T10:45:00Z",
  "updated_at": "2026-07-18T10:50:00Z"
}
```

### 9. Delete User

**Endpoint**

```text
DELETE /api/users/{id}/
```

**Success Response**

```text
204 No Content
```

## Role APIs

### 10. List Roles

**Endpoint**

```text
GET /api/roles/
```

**Auth**

- Admin only

**Response**

```json
[
  {
    "id": 1,
    "name": "Administrator",
    "description": "Default system administrator role.",
    "is_active": true,
    "permissions": [],
    "created_at": "2026-07-18T10:30:00Z",
    "updated_at": "2026-07-18T10:30:00Z"
  }
]
```

### 11. Create Role

**Endpoint**

```text
POST /api/roles/
```

**Request**

```json
{
  "name": "Sales",
  "description": "Sales team role",
  "permission_ids": [1, 2]
}
```

**Success Response**

```json
{
  "id": 2,
  "name": "Sales",
  "description": "Sales team role",
  "is_active": true,
  "permissions": [
    {
      "id": 1,
      "name": "manage_customers",
      "description": "Can manage customers",
      "is_active": true,
      "created_at": "2026-07-18T11:00:00Z",
      "updated_at": "2026-07-18T11:00:00Z"
    },
    {
      "id": 2,
      "name": "view_reports",
      "description": "Can view reports",
      "is_active": true,
      "created_at": "2026-07-18T11:00:00Z",
      "updated_at": "2026-07-18T11:00:00Z"
    }
  ],
  "created_at": "2026-07-18T11:05:00Z",
  "updated_at": "2026-07-18T11:05:00Z"
}
```

### 12. Get Role

**Endpoint**

```text
GET /api/roles/{id}/
```

**Success Response**

```json
{
  "id": 2,
  "name": "Sales",
  "description": "Sales team role",
  "is_active": true,
  "permissions": [
    {
      "id": 1,
      "name": "manage_customers",
      "description": "Can manage customers",
      "is_active": true,
      "created_at": "2026-07-18T11:00:00Z",
      "updated_at": "2026-07-18T11:00:00Z"
    }
  ],
  "created_at": "2026-07-18T11:05:00Z",
  "updated_at": "2026-07-18T11:05:00Z"
}
```

### 13. Update Role

**Endpoint**

```text
PATCH /api/roles/{id}/
```

**Request**

```json
{
  "description": "Updated sales role",
  "permission_ids": [1]
}
```

**Success Response**

```json
{
  "id": 2,
  "name": "Sales",
  "description": "Updated sales role",
  "is_active": true,
  "permissions": [
    {
      "id": 1,
      "name": "manage_customers",
      "description": "Can manage customers",
      "is_active": true,
      "created_at": "2026-07-18T11:00:00Z",
      "updated_at": "2026-07-18T11:00:00Z"
    }
  ],
  "created_at": "2026-07-18T11:05:00Z",
  "updated_at": "2026-07-18T11:10:00Z"
}
```

### 14. Delete Role

**Endpoint**

```text
DELETE /api/roles/{id}/
```

**Success Response**

```text
204 No Content
```

## Permission APIs

### 15. List Permissions

**Endpoint**

```text
GET /api/permissions/
```

**Response**

```json
[
  {
    "id": 1,
    "name": "manage_customers",
    "description": "Can manage customers",
    "is_active": true,
    "created_at": "2026-07-18T11:00:00Z",
    "updated_at": "2026-07-18T11:00:00Z"
  }
]
```

### 16. Create Permission

**Endpoint**

```text
POST /api/permissions/
```

**Request**

```json
{
  "name": "manage_customers",
  "description": "Can manage customers"
}
```

**Success Response**

```json
{
  "id": 1,
  "name": "manage_customers",
  "description": "Can manage customers",
  "is_active": true,
  "created_at": "2026-07-18T11:00:00Z",
  "updated_at": "2026-07-18T11:00:00Z"
}
```

### 17. Get Permission

**Endpoint**

```text
GET /api/permissions/{id}/
```

**Success Response**

```json
{
  "id": 1,
  "name": "manage_customers",
  "description": "Can manage customers",
  "is_active": true,
  "created_at": "2026-07-18T11:00:00Z",
  "updated_at": "2026-07-18T11:00:00Z"
}
```

### 18. Update Permission

**Endpoint**

```text
PATCH /api/permissions/{id}/
```

**Request**

```json
{
  "description": "Updated permission description"
}
```

**Success Response**

```json
{
  "id": 1,
  "name": "manage_customers",
  "description": "Updated permission description",
  "is_active": true,
  "created_at": "2026-07-18T11:00:00Z",
  "updated_at": "2026-07-18T11:10:00Z"
}
```

### 19. Delete Permission

**Endpoint**

```text
DELETE /api/permissions/{id}/
```

**Success Response**

```text
204 No Content
```

## Customer APIs

Customers do not have login access. They are only CRM records.

### 20. List Customers

**Endpoint**

```text
GET /api/customers/
```

**Auth**

- Admin only

**Response**

```json
[
  {
    "id": 1,
    "first_name": "Ali",
    "last_name": "Khan",
    "full_name": "Ali Khan",
    "email": "ali@example.com",
    "phone_number": "+971500000000",
    "company_name": "Ali Curtains",
    "address_line_1": "Office 10",
    "address_line_2": "",
    "city": "Dubai",
    "state": "Dubai",
    "postal_code": "00000",
    "country": "UAE",
    "notes": "High priority customer",
    "is_active": true,
    "created_at": "2026-07-18T11:15:00Z",
    "updated_at": "2026-07-18T11:15:00Z"
  }
]
```

### 21. Create Customer

**Endpoint**

```text
POST /api/customers/
```

**Request**

```json
{
  "first_name": "Ali",
  "last_name": "Khan",
  "email": "ali@example.com",
  "phone_number": "+971500000000",
  "company_name": "Ali Curtains",
  "address_line_1": "Office 10",
  "address_line_2": "",
  "city": "Dubai",
  "state": "Dubai",
  "postal_code": "00000",
  "country": "UAE",
  "notes": "High priority customer",
  "is_active": true
}
```

**Success Response**

```json
{
  "id": 1,
  "first_name": "Ali",
  "last_name": "Khan",
  "full_name": "Ali Khan",
  "email": "ali@example.com",
  "phone_number": "+971500000000",
  "company_name": "Ali Curtains",
  "address_line_1": "Office 10",
  "address_line_2": "",
  "city": "Dubai",
  "state": "Dubai",
  "postal_code": "00000",
  "country": "UAE",
  "notes": "High priority customer",
  "is_active": true,
  "created_at": "2026-07-18T11:15:00Z",
  "updated_at": "2026-07-18T11:15:00Z"
}
```

### 22. Get Customer

**Endpoint**

```text
GET /api/customers/{id}/
```

**Success Response**

```json
{
  "id": 1,
  "first_name": "Ali",
  "last_name": "Khan",
  "full_name": "Ali Khan",
  "email": "ali@example.com",
  "phone_number": "+971500000000",
  "company_name": "Ali Curtains",
  "address_line_1": "Office 10",
  "address_line_2": "",
  "city": "Dubai",
  "state": "Dubai",
  "postal_code": "00000",
  "country": "UAE",
  "notes": "High priority customer",
  "is_active": true,
  "created_at": "2026-07-18T11:15:00Z",
  "updated_at": "2026-07-18T11:15:00Z"
}
```

### 23. Update Customer

**Endpoint**

```text
PATCH /api/customers/{id}/
```

**Request**

```json
{
  "phone_number": "+971511111111",
  "notes": "Updated note"
}
```

**Success Response**

```json
{
  "id": 1,
  "first_name": "Ali",
  "last_name": "Khan",
  "full_name": "Ali Khan",
  "email": "ali@example.com",
  "phone_number": "+971511111111",
  "company_name": "Ali Curtains",
  "address_line_1": "Office 10",
  "address_line_2": "",
  "city": "Dubai",
  "state": "Dubai",
  "postal_code": "00000",
  "country": "UAE",
  "notes": "Updated note",
  "is_active": true,
  "created_at": "2026-07-18T11:15:00Z",
  "updated_at": "2026-07-18T11:20:00Z"
}
```

### 24. Delete Customer

**Endpoint**

```text
DELETE /api/customers/{id}/
```

**Success Response**

```text
204 No Content
```

## Common Status Codes

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

## Notes

- There is no public user registration endpoint.
- User creation is admin-only.
- Customers are CRM records only and cannot log in.
- Role and permission assignment currently exists at the data level; custom per-endpoint role-permission enforcement can be added later.
