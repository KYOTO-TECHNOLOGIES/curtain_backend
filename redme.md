# Customers & Appointments API

## Base URL

`http://localhost:8111/api/`

## Authentication

All API endpoints except login, refresh, and logout require authentication.

### Headers

`Authorization: Bearer <access_token>`

If cookie-based auth is enabled, the following cookies may be used:

- `access_token` - JWT access token (HTTP-only cookie)
- `refresh_token` - JWT refresh token (HTTP-only cookie)

---

## 1. Authentication Endpoints

### 1.1 Login

- Endpoint: `POST /api/auth/login/`
- Request body:

```json
{
  "email": "admin@example.com",
  "password": "adminpass123"
}
```

- Response:

```json
{
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": {
      "id": 1,
      "name": "Admin",
      "description": "Administrator role with full permissions"
    },
    "role_name": "Admin",
    "is_active": true,
    "is_staff": true,
    "is_superuser": true,
    "created_at": "2024-07-22T10:00:00Z",
    "updated_at": "2024-07-22T10:00:00Z"
  },
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 1.2 Refresh Token

- Endpoint: `POST /api/auth/refresh/`
- Request body:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

- Response:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "full_name": "Admin User"
  }
}
```

### 1.3 Logout

- Endpoint: `POST /api/auth/logout/`
- Request body:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

- Response:

```json
{
  "detail": "Logged out successfully."
}
```

### 1.4 Get Current User

- Endpoint: `GET /api/auth/me/`
- Response:

```json
{
  "id": 1,
  "email": "admin@example.com",
  "full_name": "Admin User",
  "role": {
    "id": 1,
    "name": "Admin",
    "description": "Administrator role with full permissions"
  },
  "role_name": "Admin",
  "is_active": true,
  "is_staff": true,
  "is_superuser": true
}
```

### 1.5 Change Password

- Endpoint: `POST /api/auth/change-password/`
- Request body:

```json
{
  "old_password": "oldpass123",
  "new_password": "newpass123"
}
```

- Response:

```json
{
  "detail": "Password changed successfully."
}
```

---

## 2. Customers API

### 2.1 List Customers

- Endpoint: `GET /api/customers/`
- Query parameters:
  - `search` (string): Search by first name, last name, phone, or email.

Example:

```http
GET /api/customers/?search=John
```

Response:

```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+971501234567",
    "email": "john.doe@example.com",
    "address_line_1": "123 Main St",
    "address_line_2": "Apt 4B",
    "city": "Dubai",
    "state": "Dubai",
    "postal_code": "12345",
    "country": "UAE",
    "company_name": "",
    "notes": "Test customer",
    "created_by": 1,
    "created_at": "2024-07-22T10:00:00Z",
    "updated_at": "2024-07-22T10:00:00Z"
  }
]
```

### 2.2 Create Customer

- Endpoint: `POST /api/customers/`
- Request body:

```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+9715087654321",
  "email": "jane.smith@example.com",
  "address_line_1": "456 Park Ave",
  "address_line_2": "Suite 100",
  "city": "Abu Dhabi",
  "state": "Abu Dhabi",
  "postal_code": "54321",
  "country": "UAE",
  "company_name": "Smith Interiors",
  "notes": "Preferred client"
}
```

- Response (201 Created):

```json
{
  "id": 2,
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "phone": "+9715087654321",
  "email": "jane.smith@example.com",
  "address_line_1": "456 Park Ave",
  "address_line_2": "Suite 100",
  "city": "Abu Dhabi",
  "state": "Abu Dhabi",
  "postal_code": "54321",
  "country": "UAE",
  "company_name": "Smith Interiors",
  "notes": "Preferred client",
  "created_by": 1,
  "created_at": "2024-07-22T10:05:00Z",
  "updated_at": "2024-07-22T10:05:00Z"
}
```

- Error response (duplicate phone/email):

```json
{
  "phone": ["A customer with this phone already exists."]
}
```

### 2.3 Get Customer

- Endpoint: `GET /api/customers/{id}/`

Example:

```http
GET /api/customers/1/
```

Response:

```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone": "+971501234567",
  "email": "john.doe@example.com",
  "address_line_1": "123 Main St",
  "address_line_2": "Apt 4B",
  "city": "Dubai",
  "state": "Dubai",
  "postal_code": "12345",
  "country": "UAE",
  "company_name": "",
  "notes": "Test customer",
  "created_by": 1,
  "created_at": "2024-07-22T10:00:00Z",
  "updated_at": "2024-07-22T10:00:00Z"
}
```

### 2.4 Update Customer

- Endpoint: `PUT /api/customers/{id}/` (full update)
- Endpoint: `PATCH /api/customers/{id}/` (partial update)

Example PATCH request:

```json
{
  "first_name": "Jonathan",
  "phone": "+9715098765432"
}
```

Example response:

```json
{
  "id": 1,
  "first_name": "Jonathan",
  "last_name": "Doe",
  "full_name": "Jonathan Doe",
  "phone": "+9715098765432",
  "email": "john.doe@example.com",
  "address_line_1": "123 Main St",
  "address_line_2": "Apt 4B",
  "city": "Dubai",
  "state": "Dubai",
  "postal_code": "12345",
  "country": "UAE",
  "company_name": "",
  "notes": "Test customer",
  "created_by": 1,
  "created_at": "2024-07-22T10:00:00Z",
  "updated_at": "2024-07-22T10:10:00Z"
}
```

### 2.5 Delete Customer

- Endpoint: `DELETE /api/customers/{id}/`
- Response: `204 No Content`

### 2.6 Lookup Customer

- Endpoint: `GET /api/customers/lookup/`
- Query parameters:
  - `phone` (string)
  - `email` (string)

Examples:

```http
GET /api/customers/lookup/?phone=+971501234567
GET /api/customers/lookup/?email=john.doe@example.com
```

Response (found):

```json
{
  "found": true,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+971501234567",
    "email": "john.doe@example.com"
  }
}
```

Response (not found):

```json
{
  "found": false,
  "message": "Customer not found."
}
```

### 2.7 Create or Get Customer

- Endpoint: `POST /api/customers/create-or-get/`
- Request body includes at least one of `phone` or `email`.

Example request:

```json
{
  "first_name": "Sara",
  "last_name": "Ali",
  "phone": "+971501112233",
  "email": "sara.ali@example.com"
}
```

Response if customer exists:

```json
{
  "created": false,
  "customer": {
    "id": 5,
    "first_name": "Sara",
    "last_name": "Ali",
    "full_name": "Sara Ali",
    "phone": "+971501112233",
    "email": "sara.ali@example.com",
    "address_line_1": "",
    "address_line_2": "",
    "city": "",
    "state": "",
    "postal_code": "",
    "country": "",
    "company_name": "",
    "notes": "",
    "created_by": 1,
    "created_at": "2024-07-22T10:15:00Z",
    "updated_at": "2024-07-22T10:15:00Z"
  }
}
```

Response if created:

```json
{
  "created": true,
  "customer": {
    "id": 6,
    "first_name": "Sara",
    "last_name": "Ali",
    "full_name": "Sara Ali",
    "phone": "+971501112233",
    "email": "sara.ali@example.com",
    "address_line_1": "",
    "address_line_2": "",
    "city": "",
    "state": "",
    "postal_code": "",
    "country": "",
    "company_name": "",
    "notes": "",
    "created_by": 1,
    "created_at": "2024-07-22T10:16:00Z",
    "updated_at": "2024-07-22T10:16:00Z"
  }
}
```

---

## 3. Appointments API

### 3.1 List Appointments

- Endpoint: `GET /api/appointments/`
- Query parameters:
  - `status` (string)
  - `assigned_to` (integer)
  - `date_from` (YYYY-MM-DD)
  - `date_to` (YYYY-MM-DD)
  - `customer` (integer customer ID)

Example:

```http
GET /api/appointments/?status=pending&customer=1
```

Response:

```json
[
  {
    "id": 1,
    "customer": 1,
    "customer_name": "John Doe",
    "customer_phone": "+971501234567",
    "title": "Window installation",
    "description": "Install curtain tracks and blinds.",
    "appointment_date": "2026-07-22",
    "appointment_time": "09:00:00",
    "end_time": "11:00:00",
    "job_type": "installation",
    "status": "scheduled",
    "assigned_to": 3,
    "assigned_to_name": "Sales Rep",
    "assigned_to_username": "sales@example.com",
    "location_full_address": "123 Main St, Dubai",
    "created_at": "2026-07-20T14:00:00Z",
    "updated_at": "2026-07-20T14:00:00Z"
  }
]
```

### 3.2 Create Appointment

- Endpoint: `POST /api/appointments/`
- Required fields are determined by the serializer.
- Customer may be created by passing `customer_first_name`, `customer_last_name`, `customer_phone`, and/or `customer_email`.

Example request with existing customer:

```json
{
  "customer": 1,
  "title": "Window installation",
  "description": "Install curtain tracks and blinds.",
  "appointment_date": "2026-07-22",
  "appointment_time": "09:00:00",
  "end_time": "11:00:00",
  "job_type": "installation",
  "status": "scheduled",
  "assigned_to": 3,
  "location_building": "Tower A",
  "location_unit": "402",
  "location_full_address": "123 Main St, Dubai",
  "location_coordinates": {"lat": 25.2048, "lng": 55.2708},
  "location_instructions": "Use rear entrance"
}
```

Example request creating a new customer:

```json
{
  "customer_first_name": "Ahmed",
  "customer_last_name": "Mohammed",
  "customer_phone": "+9715098765432",
  "customer_email": "ahmed@example.com",
  "customer_address": "Business Bay",
  "customer_city": "Dubai",
  "customer_source": "website",
  "title": "Curtain repair",
  "description": "Repair curtain motor",
  "appointment_date": "2026-07-22",
  "appointment_time": "13:00:00",
  "end_time": "14:00:00",
  "job_type": "repair",
  "status": "pending",
  "assigned_to": 4,
  "location_building": "Building 5",
  "location_unit": "12",
  "location_full_address": "Business Bay, Dubai",
  "location_coordinates": {"lat": 25.1950, "lng": 55.2760},
  "location_instructions": "Call on arrival"
}
```

- Response (201 Created):

```json
{
  "id": 10,
  "customer": 2,
  "title": "Curtain repair",
  "description": "Repair curtain motor",
  "appointment_date": "2026-07-22",
  "appointment_time": "13:00:00",
  "end_time": "14:00:00",
  "job_type": "repair",
  "status": "pending",
  "assigned_to": 4,
  "location": 5,
  "created_at": "2026-07-20T15:00:00Z",
  "updated_at": "2026-07-20T15:00:00Z"
}
```

### 3.3 Get Appointment

- Endpoint: `GET /api/appointments/{id}/`

Example response:

```json
{
  "id": 10,
  "customer": {
    "id": 2,
    "first_name": "Ahmed",
    "last_name": "Mohammed",
    "full_name": "Ahmed Mohammed",
    "phone": "+9715098765432",
    "email": "ahmed@example.com",
    "address_line_1": "Business Bay",
    "address_line_2": "",
    "city": "Dubai",
    "state": "",
    "postal_code": "",
    "country": "UAE",
    "company_name": "",
    "notes": "",
    "created_by": 1,
    "created_at": "2026-07-20T15:00:00Z",
    "updated_at": "2026-07-20T15:00:00Z"
  },
  "title": "Curtain repair",
  "description": "Repair curtain motor",
  "appointment_date": "2026-07-22",
  "appointment_time": "13:00:00",
  "end_time": "14:00:00",
  "job_type": "repair",
  "status": "pending",
  "assigned_to": 4,
  "assigned_to_name": "Sales Rep",
  "assigned_to_username": "sales@example.com",
  "created_by": 1,
  "created_by_name": "Admin User",
  "created_by_username": "admin@example.com",
  "created_at": "2026-07-20T15:00:00Z",
  "updated_at": "2026-07-20T15:00:00Z",
  "cancellation_reason": "",
  "cancelled_at": null,
  "cancelled_by": null,
  "cancelled_by_name": null,
  "location": {
    "id": 5,
    "building_name": "Building 5",
    "unit_number": "12",
    "full_address": "Business Bay, Dubai",
    "coordinates": {"lat": 25.1950, "lng": 55.2760},
    "additional_instructions": "Call on arrival",
    "location_status": "not_set"
  }
}
```

### 3.4 Update Appointment

- Endpoint: `PUT /api/appointments/{id}/` (full update)
- Endpoint: `PATCH /api/appointments/{id}/` (partial update)

Request body can include any appointment fields and optional customer/location creation fields.

Example PATCH request:

```json
{
  "title": "Curtain motor replacement",
  "status": "scheduled",
  "location_full_address": "Mall area, Dubai"
}
```

- Response:

```json
{
  "id": 10,
  "customer": 2,
  "title": "Curtain motor replacement",
  "description": "Repair curtain motor",
  "appointment_date": "2026-07-22",
  "appointment_time": "13:00:00",
  "end_time": "14:00:00",
  "job_type": "repair",
  "status": "scheduled",
  "assigned_to": 4,
  "location": 5,
  "created_at": "2026-07-20T15:00:00Z",
  "updated_at": "2026-07-20T15:10:00Z"
}
```

### 3.5 Cancel/Delete Appointment

- Endpoint: `DELETE /api/appointments/{id}/`
- Response:

```json
{
  "message": "Appointment 10 has been cancelled.",
  "appointment": {
    "id": 10,
    "customer": {
      "id": 2,
      "first_name": "Ahmed",
      "last_name": "Mohammed",
      "full_name": "Ahmed Mohammed",
      "phone": "+9715098765432",
      "email": "ahmed@example.com",
      "address_line_1": "Business Bay",
      "address_line_2": "",
      "city": "Dubai",
      "state": "",
      "postal_code": "",
      "country": "UAE",
      "company_name": "",
      "notes": "",
      "created_by": 1,
      "created_at": "2026-07-20T15:00:00Z",
      "updated_at": "2026-07-20T15:10:00Z"
    },
    "title": "Curtain motor replacement",
    "description": "Repair curtain motor",
    "appointment_date": "2026-07-22",
    "appointment_time": "13:00:00",
    "end_time": "14:00:00",
    "job_type": "repair",
    "status": "cancelled",
    "assigned_to": 4,
    "assigned_to_name": "Sales Rep",
    "assigned_to_username": "sales@example.com",
    "created_by": 1,
    "created_by_name": "Admin User",
    "created_by_username": "admin@example.com",
    "created_at": "2026-07-20T15:00:00Z",
    "updated_at": "2026-07-20T15:15:00Z",
    "cancellation_reason": "Deleted by user",
    "cancelled_at": "2026-07-20T15:15:00Z",
    "cancelled_by": 1,
    "cancelled_by_name": "Admin User",
    "location": {
      "id": 5,
      "building_name": "Building 5",
      "unit_number": "12",
      "full_address": "Business Bay, Dubai",
      "coordinates": {"lat": 25.1950, "lng": 55.2760},
      "additional_instructions": "Call on arrival",
      "location_status": "not_set"
    }
  }
}
```

### 3.6 Update Appointment Status

- Endpoint: `PATCH /api/appointments/{id}/status/`
- Request body:

```json
{
  "status": "cancelled",
  "cancellation_reason": "Customer requested cancellation"
}
```

- Response:

```json
{
  "id": 10,
  "customer": {
    "id": 2,
    "first_name": "Ahmed",
    "last_name": "Mohammed",
    "full_name": "Ahmed Mohammed",
    "phone": "+9715098765432",
    "email": "ahmed@example.com"
  },
  "title": "Curtain motor replacement",
  "description": "Repair curtain motor",
  "appointment_date": "2026-07-22",
  "appointment_time": "13:00:00",
  "end_time": "14:00:00",
  "job_type": "repair",
  "status": "cancelled",
  "assigned_to": 4,
  "assigned_to_name": "Sales Rep",
  "assigned_to_username": "sales@example.com",
  "created_by": 1,
  "created_by_name": "Admin User",
  "created_by_username": "admin@example.com",
  "created_at": "2026-07-20T15:00:00Z",
  "updated_at": "2026-07-20T15:15:00Z",
  "cancellation_reason": "Customer requested cancellation",
  "cancelled_at": "2026-07-20T15:15:00Z",
  "cancelled_by": 1,
  "cancelled_by_name": "Admin User",
  "location": {
    "id": 5,
    "building_name": "Building 5",
    "unit_number": "12",
    "full_address": "Business Bay, Dubai",
    "coordinates": {"lat": 25.1950, "lng": 55.2760},
    "additional_instructions": "Call on arrival",
    "location_status": "not_set"
  }
}
```

### 3.7 Assign Salesman

- Endpoint: `PATCH /api/appointments/{id}/assign/`
- Request body:

```json
{
  "assigned_to": 4
}
```

- Response:

```json
{
  "id": 10,
  "customer": {
    "id": 2,
    "first_name": "Ahmed",
    "last_name": "Mohammed",
    "full_name": "Ahmed Mohammed",
    "phone": "+9715098765432",
    "email": "ahmed@example.com"
  },
  "title": "Curtain motor replacement",
  "description": "Repair curtain motor",
  "appointment_date": "2026-07-22",
  "appointment_time": "13:00:00",
  "end_time": "14:00:00",
  "job_type": "repair",
  "status": "cancelled",
  "assigned_to": 4,
  "assigned_to_name": "Sales Rep",
  "assigned_to_username": "sales@example.com",
  "created_by": 1,
  "created_by_name": "Admin User",
  "created_by_username": "admin@example.com",
  "created_at": "2026-07-20T15:00:00Z",
  "updated_at": "2026-07-20T15:15:00Z",
  "cancellation_reason": "Deleted by user",
  "cancelled_at": "2026-07-20T15:15:00Z",
  "cancelled_by": 1,
  "cancelled_by_name": "Admin User",
  "location": {
    "id": 5,
    "building_name": "Building 5",
    "unit_number": "12",
    "full_address": "Business Bay, Dubai",
    "coordinates": {"lat": 25.1950, "lng": 55.2760},
    "additional_instructions": "Call on arrival",
    "location_status": "not_set"
  }
}
```

### 3.8 My Appointments

- Endpoint: `GET /api/appointments/my/`
- Returns appointments assigned to the current user.

### 3.9 Appointment Stats

- Endpoint: `GET /api/appointments/stats/`
- Response:

```json
{
  "total": 5,
  "by_status": {
    "scheduled": 2,
    "pending": 1,
    "cancelled": 1,
    "rescheduled": 1
  },
  "today": 1,
  "upcoming": 3
}
```

### 3.10 Reschedule Appointment

- Endpoint: `POST /api/appointments/{id}/reschedule/`
- Request body:

```json
{
  "appointment_date": "2026-07-25",
  "appointment_time": "15:00:00",
  "end_time": "16:00:00"
}
```

- Response: updated appointment detail object.

---

## 4. Notes

- Customer phone and email are unique within the system.
- Appointments can be filtered by `status`, `assigned_to`, `date_from`, `date_to`, and `customer`.
- Appointment deletion marks the record as cancelled rather than permanently removing it.
- Use `create-or-get` to avoid duplicate customers when a phone or email already exists.


This endpoint either creates a new customer or returns an existing one based on phone/email.

Request Body:

json
{
  "phone": "+971501234567",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "address_line_1": "123 Main St",
  "city": "Dubai",
  "country": "UAE"
}
Response (Existing):

json
{
  "created": false,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+971501234567",
    "email": "john.doe@example.com"
  }
}
Response (New):

json
{
  "created": true,
  "customer": {
    "id": 3,
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+971501234567",
    "email": "john.doe@example.com"
  }
}
3. Appointments API
3.1 List Appointments
Endpoint: GET /api/appointments/

Query Parameters:

Parameter	Type	Description
status	string	Filter by status
assigned_to	integer	Filter by assigned user ID
date_from	date	Filter appointments from this date
date_to	date	Filter appointments up to this date
customer	integer	Filter by customer ID
Status Values:

pending

scheduled

in_progress

completed

cancelled

rescheduled

Job Types:

measurement

installation

consultation

repair

Examples:

text
GET /api/appointments/?status=scheduled
GET /api/appointments/?assigned_to=2
GET /api/appointments/?date_from=2024-07-01&date_to=2024-07-31
Response:

json
[
  {
    "id": "APT-1001",
    "customer": 1,
    "customer_name": "Fatima Al Hashimi",
    "customer_phone": "+971501234567",
    "title": "Window Measurement",
    "description": "Client needs measurements for blackout curtains",
    "appointment_date": "2024-07-25",
    "appointment_time": "09:30:00",
    "end_time": "10:30:00",
    "job_type": "measurement",
    "status": "scheduled",
    "assigned_to": 2,
    "assigned_to_name": "James Doe",
    "assigned_to_username": "salesman@example.com",
    "location_full_address": "Al Marsa St, Dubai Marina",
    "created_at": "2024-07-22T10:00:00Z",
    "updated_at": "2024-07-22T10:00:00Z"
  }
]
3.2 Create Appointment
Endpoint: POST /api/appointments/

This endpoint automatically handles customer creation/lookup.

Request Body:

json
{
  "customer_first_name": "Ahmed",
  "customer_last_name": "Mohammed",
  "customer_phone": "+9715098765432",
  "customer_email": "ahmed.m@example.com",
  "customer_address": "Business Bay",
  "customer_city": "Dubai",
  "customer_source": "website",
  
  "title": "Installation Consultation",
  "description": "Client needs consultation for new curtains",
  "appointment_date": "2024-07-26",
  "appointment_time": "14:00:00",
  "end_time": "15:00:00",
  "job_type": "consultation",
  "status": "pending",
  "assigned_to": 2,
  
  "location_building": "Business Bay Tower",
  "location_unit": "Office 1001",
  "location_full_address": "Business Bay, Dubai",
  "location_coordinates": {"lat": 25.1900, "lng": 55.2700},
  "location_instructions": "Parking available in basement"
}
Response (201 Created):

json
{
  "id": "APT-1002",
  "customer": {
    "id": 2,
    "first_name": "Ahmed",
    "last_name": "Mohammed",
    "full_name": "Ahmed Mohammed",
    "phone": "+9715098765432",
    "email": "ahmed.m@example.com",
    "address_line_1": "Business Bay",
    "city": "Dubai",
    "country": "UAE"
  },
  "title": "Installation Consultation",
  "description": "Client needs consultation for new curtains",
  "appointment_date": "2024-07-26",
  "appointment_time": "14:00:00",
  "end_time": "15:00:00",
  "job_type": "consultation",
  "status": "pending",
  "assigned_to": 2,
  "assigned_to_name": "James Doe",
  "assigned_to_username": "salesman@example.com",
  "created_by": 1,
  "created_by_name": "Admin User",
  "created_by_username": "admin@example.com",
  "created_at": "2024-07-22T10:05:00Z",
  "updated_at": "2024-07-22T10:05:00Z",
  "cancellation_reason": "",
  "cancelled_at": null,
  "cancelled_by": null,
  "cancelled_by_name": null,
  "location": {
    "id": 1,
    "building_name": "Business Bay Tower",
    "unit_number": "Office 1001",
    "full_address": "Business Bay, Dubai",
    "coordinates": {"lat": 25.1900, "lng": 55.2700},
    "additional_instructions": "Parking available in basement",
    "location_status": "not_set"
  }
}
Creating with Existing Customer:

json
{
  "customer_phone": "+971501234567",
  "customer_first_name": "Fatima",
  "customer_last_name": "Al Hashimi",
  "title": "Follow-up Measurement",
  "appointment_date": "2024-07-27",
  "appointment_time": "11:00:00",
  "job_type": "measurement",
  "location_full_address": "Al Marsa St, Dubai Marina"
}
3.3 Get Appointment Details
Endpoint: GET /api/appointments/{id}/

Example:

text
GET /api/appointments/APT-1001/
Response:

json
{
  "id": "APT-1001",
  "customer": {
    "id": 1,
    "first_name": "Fatima",
    "last_name": "Al Hashimi",
    "full_name": "Fatima Al Hashimi",
    "phone": "+971501234567",
    "email": "fatima.h@example.com",
    "address_line_1": "Al Marsa St",
    "city": "Dubai",
    "country": "UAE"
  },
  "title": "Window Measurement",
  "description": "Client needs measurements for blackout curtains",
  "appointment_date": "2024-07-25",
  "appointment_time": "09:30:00",
  "end_time": "10:30:00",
  "job_type": "measurement",
  "status": "scheduled",
  "assigned_to": 2,
  "assigned_to_name": "James Doe",
  "assigned_to_username": "salesman@example.com",
  "created_by": 1,
  "created_by_name": "Admin User",
  "created_by_username": "admin@example.com",
  "created_at": "2024-07-22T10:00:00Z",
  "updated_at": "2024-07-22T10:00:00Z",
  "cancellation_reason": "",
  "cancelled_at": null,
  "cancelled_by": null,
  "cancelled_by_name": null,
  "location": {
    "id": 1,
    "building_name": "Marina Heights",
    "unit_number": "Flat 1204",
    "full_address": "Al Marsa St, Dubai Marina",
    "coordinates": {"lat": 25.0805, "lng": 55.1403},
    "additional_instructions": "",
    "location_status": "not_set"
  }
}
3.4 Update Appointment
Endpoint: PATCH /api/appointments/{id}/

Request Body:

json
{
  "title": "Updated Measurement",
  "description": "Updated description",
  "job_type": "installation",
  "appointment_date": "2024-07-28",
  "appointment_time": "15:00:00",
  "end_time": "16:00:00",
  "location_building": "New Building",
  "location_unit": "New Unit",
  "location_full_address": "New Address"
}
Response: Updated appointment details (same structure as GET)

3.5 Update Appointment Status
Endpoint: PATCH /api/appointments/{id}/status/

Request Body:

json
{
  "status": "in_progress"
}
Or for cancellation:

json
{
  "status": "cancelled",
  "cancellation_reason": "Client requested reschedule"
}
Status Flow:

text
pending → scheduled → in_progress → completed
                     ↘ cancelled
                     ↘ rescheduled
Response: Updated appointment details

3.6 Assign Salesman
Endpoint: PATCH /api/appointments/{id}/assign/

Request Body:

json
{
  "assigned_to": 3
}
Response: Updated appointment details

3.7 Reschedule Appointment
Endpoint: POST /api/appointments/{id}/reschedule/

Request Body:

json
{
  "appointment_date": "2024-07-30",
  "appointment_time": "10:00:00",
  "end_time": "11:00:00"
}
Response: Updated appointment details with status set to "rescheduled"

3.8 Get My Appointments (For Salesmen)
Endpoint: GET /api/appointments/my/

Query Parameters:

Parameter	Type	Description
status	string	Filter by status
Example:

text
GET /api/appointments/my/?status=in_progress
Response:

json
[
  {
    "id": "APT-1001",
    "customer": 1,
    "customer_name": "Fatima Al Hashimi",
    "customer_phone": "+971501234567",
    "title": "Window Measurement",
    "appointment_date": "2024-07-25",
    "appointment_time": "09:30:00",
    "job_type": "measurement",
    "status": "in_progress",
    "location_full_address": "Al Marsa St, Dubai Marina"
  }
]
3.9 Get Appointment Statistics
Endpoint: GET /api/appointments/stats/

Response:

json
{
  "total": 24,
  "by_status": {
    "scheduled": 18,
    "in_progress": 3,
    "completed": 2,
    "cancelled": 1
  },
  "today": 5,
  "upcoming": 21
}
3.10 Delete/Cancel Appointment
Endpoint: DELETE /api/appointments/{id}/

This performs a soft delete - the appointment status is set to "cancelled".

Response:

json
{
  "message": "Appointment APT-1001 has been cancelled.",
  "appointment": {
    "id": "APT-1001",
    "status": "cancelled",
    "cancellation_reason": "Deleted by user",
    // ... rest of appointment data
  }
}
4. Error Responses
4.1 Validation Error (400 Bad Request)
json
{
  "end_time": ["End time must be after start time."]
}
4.2 Authentication Error (401 Unauthorized)
json
{
  "detail": "Authentication credentials were not provided."
}
4.3 Permission Error (403 Forbidden)
json
{
  "error": "You can only update status for appointments assigned to you."
}
4.4 Not Found (404 Not Found)
json
{
  "detail": "Not found."
}
5. Status Codes Summary
Status Code	Description
200	Success (GET, PUT, PATCH)
201	Created (POST)
204	No Content (DELETE)
400	Bad Request (Validation error)
401	Unauthorized (Authentication required)
403	Forbidden (Permission denied)
404	Not Found
409	Conflict (Duplicate customer)
6. User Roles & Permissions
Role	Permissions
Admin	Full access to all endpoints
Salesman	Can view/update appointments assigned to them, view customers
Receptionist	Can create appointments, view customers
Accountant	Can view financial data
Production Manager	Can manage production
7. Test Credentials
json
{
  "admin": {
    "email": "admin@example.com",
    "password": "adminpass123"
  },
  "salesman": {
    "email": "salesman@example.com",
    "password": "salesmanpass123"
  },
  "receptionist": {
    "email": "receptionist@example.com",
    "password": "receptionpass123"
  }
}
8. Quick Reference - curl Examples
Login
bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "adminpass123"}'
List Customers
bash
curl -X GET http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer YOUR_TOKEN"
Create Appointment
bash
curl -X POST http://localhost:8000/api/appointments/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_first_name": "Test",
    "customer_last_name": "User",
    "customer_phone": "+971501234568",
    "title": "Test Appointment",
    "appointment_date": "2024-07-25",
    "appointment_time": "10:00:00",
    "job_type": "measurement",
    "location_full_address": "Test Address"
  }'
Update Status
bash
curl -X PATCH http://localhost:8000/api/appointments/APT-1001/status/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
Get My Appointments
bash
curl -X GET http://localhost:8000/api/appointments/my/ \
  -H "Authorization: Bearer YOUR_TOKEN"
9. Frontend Integration Tips
9.1 Managing Tokens
Store tokens securely (preferably in HTTP-only cookies). If using localStorage:

javascript
// Store tokens
localStorage.setItem('access_token', response.access);
localStorage.setItem('refresh_token', response.refresh);

// Use in requests
const token = localStorage.getItem('access_token');
fetch('/api/customers/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
9.2 Error Handling
javascript
try {
  const response = await fetch('/api/appointments/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 401) {
    // Token expired - refresh or redirect to login
    await refreshToken();
  } else if (response.status === 403) {
    // Permission denied
    showError('You don\'t have permission to perform this action');
  } else if (response.status === 400) {
    const errors = await response.json();
    // Handle validation errors
    Object.keys(errors).forEach(field => {
      showFieldError(field, errors[field][0]);
    });
  }
} catch (error) {
  console.error('API Error:', error);
}
9.3 Auto-refresh Token
javascript
async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  const response = await fetch('/api/auth/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data.access;
  } else {
    // Redirect to login
    window.location.href = '/login';
  }
}
10. Changelog
Version	Date	Changes
1.0.0	2024-07-22	Initial API release
Customers CRUD with duplicate prevention
Appointments with status management
Location support for appointments
Role-based permissions
For questions or support, contact the development team.