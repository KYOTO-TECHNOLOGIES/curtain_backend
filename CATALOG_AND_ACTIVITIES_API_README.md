# Catalog and Activities API Reference

This document describes the REST API endpoints for the catalog and activities apps in the Curtain Master project.

## Base URLs

- Catalog API: `/api/catalog/`
- Activities API: `/api/activities/`

## Authentication

- Catalog endpoints use `IsAuthenticatedOrReadOnly`.
  - `GET` requests are allowed without authentication.
  - `POST`, `PUT`, `PATCH`, and `DELETE` require an authenticated user.
- Activities endpoints are read-only (`GET` only) and use `IsAuthenticatedOrReadOnly`.

---

## 1) Catalog API

### 1.1 Work Types

Base path: `/api/catalog/work-types/`

#### List work types
- Method: `GET`
- Description: Returns all work types.

Example request
```http
GET /api/catalog/work-types/
```

Example response
```json
[
  {
    "id": 1,
    "name": "Roller",
    "pricing_unit": "m2",
    "features": {
      "motor": true,
      "charges": true,
      "images": true
    }
  }
]
```

#### Create a work type
- Method: `POST`
- Required fields: `name`

Example request body
```json
{
  "name": "Roman",
  "pricing_unit": "m2",
  "features": {
    "motor": false,
    "charges": true
  }
}
```

Example response
```json
{
  "id": 2,
  "name": "Roman",
  "pricing_unit": "m2",
  "features": {
    "motor": false,
    "charges": true
  }
}
```

### 1.2 Fabric Types

Base path: `/api/catalog/fabric-types/`

#### List fabric types
- Method: `GET`

Example response
```json
[
  {
    "id": 1,
    "work_type": 1,
    "work_type_name": "Roller",
    "name": "Blackout"
  }
]
```

### 1.3 Models

Base path: `/api/catalog/models/`

#### List models
- Method: `GET`

Example response
```json
[
  {
    "id": 1,
    "fabric_type": 1,
    "fabric_type_name": "Blackout",
    "name": "Classic"
  }
]
```

### 1.4 Catalog Items

Base path: `/api/catalog/items/`

#### List catalog items
- Method: `GET`

Example response
```json
[
  {
    "id": 1,
    "model": 1,
    "model_name": "Classic",
    "name": "Premium Shade",
    "price_per_unit": "150.00",
    "image": null
  }
]
```

#### Create a catalog item
- Method: `POST`
- Required fields: `model`, `name`, `price_per_unit`

Example request body
```json
{
  "model": 1,
  "name": "Premium Shade",
  "price_per_unit": "150.00"
}
```

### 1.5 Motor Types

Base path: `/api/catalog/motors/`

#### List motor types
- Method: `GET`

Example response
```json
[
  {
    "id": 1,
    "name": "Tubular",
    "price_per_m2": "120.00"
  }
]
```

### 1.6 Charge Templates

Base path: `/api/catalog/charges/`

#### List charge templates
- Method: `GET`

Example response
```json
[
  {
    "id": 1,
    "name": "Manual Control",
    "price": "50.00",
    "unit": "flat"
  }
]
```

---

## 2) Activities API

### 2.1 Activity Logs

Base path: `/api/activities/activity-logs/`

#### List activity logs
- Method: `GET`
- Description: Returns recent activity log entries.

Example request
```http
GET /api/activities/activity-logs/
```

Example response
```json
[
  {
    "id": 1,
    "action": "created",
    "details": {
      "source": "test"
    },
    "content_type": 16,
    "object_id": 3,
    "target_type": "worktype",
    "target_id": 3,
    "user": 1,
    "user_email": "activity@example.com",
    "created_at": "2026-07-27T10:00:00Z"
  }
]
```

#### Filter by target model
- Method: `GET`
- Query parameter: `content_type`

Example request
```http
GET /api/activities/activity-logs/?content_type=worktype
```

---

## 3) Common Response Notes

- Successful `GET` requests return `200 OK`.
- Successful `POST`/`PUT`/`PATCH` requests return `200 OK` or `201 Created` depending on the action.
- Invalid input returns `400 Bad Request`.
- Unauthorized write requests return `401 Unauthorized` or `403 Forbidden`.

---

## 4) Example Curl Commands

### Catalog list
```bash
curl http://localhost:8000/api/catalog/work-types/
```

### Create catalog item
```bash
curl -X POST http://localhost:8000/api/catalog/items/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"model": 1, "name": "Premium Shade", "price_per_unit": "150.00"}'
```

### Activities list
```bash
curl http://localhost:8000/api/activities/activity-logs/
```
