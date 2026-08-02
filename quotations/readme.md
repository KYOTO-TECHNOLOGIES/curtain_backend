# CurtainMaster Quotations API

This README documents the quotations API for the Curtain Master backend.

## Base URL

```text
http://localhost:8000/api/quotations/
```

## Authentication

All endpoints require a valid JWT access token.

```http
Authorization: Bearer <access_token>
```

---

## 1. List Quotations

### Endpoint
```http
GET /api/quotations/
```

### Query Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| status | string | Filter by status: `draft`, `pending`, `sent`, `accepted`, `cancelled` |
| customer | integer | Filter by customer ID |
| work_type | integer | Filter by work type ID |
| quote_type | string | Filter by quote type: `b2c`, `b2b` |
| date_from | date | Filter from issued date |
| date_to | date | Filter to issued date |
| search | string | Search by quotation ID or customer name |

### Example Response
```json
[
  {
    "id": "QT-90214",
    "customer": 1,
    "customer_name": "Mariam Al Mansouri",
    "customer_phone": "+971501234567",
    "appointment": 1,
    "appointment_id": "APT-1001",
    "status": "accepted",
    "quote_type": "b2c",
    "work_type": 1,
    "work_type_name": "Curtain&Blinds",
    "subtotal": "11857.14",
    "vat": "592.86",
    "total": "12450.00",
    "discount_percentage": "0.00",
    "discount_amount": "0.00",
    "valid_until": "2024-08-22",
    "issued_date": "2024-07-22",
    "sent_date": "2024-07-22T14:30:00Z",
    "sent_via": "email",
    "prepared_by": 1,
    "prepared_by_name": "Basheer",
    "accepted_date": "2024-07-22T15:00:00Z",
    "created_at": "2024-07-22T10:00:00Z",
    "updated_at": "2024-07-22T15:00:00Z"
  }
]
```

---

## 2. Create Quotation

### Endpoint
```http
POST /api/quotations/
```

### Request Body
```json
{
  "customer": 1,
  "appointment": 1,
  "work_type": 1,
  "status": "draft",
  "quote_type": "b2c",
  "valid_until": "2024-08-22",
  "discount_percentage": 0,
  "areas_data": [
    {
      "area_type": "Living Room",
      "display_name": "Room of Mariam",
      "sort_order": 0,
      "surfaces": [
        {
          "surface_name": "Window 01",
          "surface_type": "window_curtain_path",
          "width_cm": 240,
          "height_cm": 310,
          "opening_direction": "one_way",
          "special_requirements": "Blackout required",
          "sort_order": 0,
          "spec": {
            "fabric_type": 1,
            "model": 1,
            "catalog_item": 1,
            "fabric_code": "LX-2044",
            "unit_price_per_m2": 120.0,
            "motor_control_type": "motorized",
            "motor_type": 1,
            "motor_price_per_unit": 180.0,
            "smart_integration": true,
            "alexa_quantity": 1,
            "alexa_unit_price": 200.0,
            "pelmet_enabled": true,
            "pelmet_width_cm": 240,
            "pelmet_price_per_metre": 90.0,
            "addon_label": "Customization Charge",
            "addon_amount": 50.0
          }
        }
      ]
    }
  ]
}
```

### Example Response
```json
{
  "id": "QT-90215",
  "customer": 1,
  "appointment": 1,
  "status": "draft",
  "quote_type": "b2c",
  "work_type": 1,
  "valid_until": "2024-08-22",
  "discount_percentage": "0.00",
  "areas": [
    {
      "id": 2,
      "quotation": "QT-90215",
      "area_type": "Living Room",
      "display_name": "Room of Mariam",
      "sort_order": 0,
      "surfaces": [
        {
          "id": 2,
          "surface_name": "Window 01",
          "surface_type": "window_curtain_path",
          "width_cm": "240.00",
          "height_cm": "310.00",
          "calculated_area_m2": "7.4400",
          "opening_direction": "one_way",
          "special_requirements": "Blackout required",
          "sort_order": 0,
          "spec": {
            "id": 2,
            "fabric_type": 1,
            "fabric_type_name": "Curtains",
            "model": 1,
            "model_name": "American",
            "catalog_item": 1,
            "catalog_item_name": "Blackout",
            "fabric_code": "LX-2044",
            "unit_price_per_m2": "120.00",
            "fabric_total": "892.80",
            "motor_control_type": "motorized",
            "motor_type": 1,
            "motor_type_name": "American Battery Motor",
            "motor_price_per_unit": "180.00",
            "motor_charge_total": "1339.20",
            "manual_control_total": "0.00",
            "smart_integration": true,
            "alexa_quantity": 1,
            "alexa_unit_price": "200.00",
            "alexa_total": "200.00",
            "pelmet_enabled": true,
            "pelmet_width_cm": "240.00",
            "pelmet_price_per_metre": "90.00",
            "pelmet_total": "216.00",
            "addon_label": "Customization Charge",
            "addon_amount": "50.00",
            "line_item_total": "2698.00"
          }
        }
      ]
    }
  ]
}
```

---

## 3. Get Quotation Details

### Endpoint
```http
GET /api/quotations/{id}/
```

### Example Response
```json
{
  "id": "QT-90214",
  "customer": 1,
  "customer_name": "Mariam Al Mansouri",
  "customer_phone": "+971501234567",
  "customer_email": "mariam.m@example.com",
  "appointment": 1,
  "appointment_id": "APT-1001",
  "status": "accepted",
  "quote_type": "b2c",
  "work_type": 1,
  "work_type_name": "Curtain&Blinds",
  "subtotal": "11857.14",
  "vat": "592.86",
  "total": "12450.00",
  "discount_percentage": "0.00",
  "discount_amount": "0.00",
  "valid_until": "2024-08-22",
  "issued_date": "2024-07-22",
  "sent_date": "2024-07-22T14:30:00Z",
  "sent_via": "email",
  "prepared_by": 1,
  "prepared_by_name": "Basheer",
  "prepared_by_email": "admin@example.com",
  "accepted_date": "2024-07-22T15:00:00Z",
  "created_at": "2024-07-22T10:00:00Z",
  "updated_at": "2024-07-22T15:00:00Z",
  "areas": [
    {
      "id": 1,
      "quotation": "QT-90214",
      "area_type": "Master Bedroom",
      "display_name": "Room of Mariam",
      "sort_order": 0,
      "surfaces": [
        {
          "id": 1,
          "surface_name": "Window 01",
          "surface_type": "window_curtain_path",
          "width_cm": "240.00",
          "height_cm": "310.00",
          "calculated_area_m2": "7.4400",
          "opening_direction": "one_way",
          "special_requirements": "Blackout required",
          "sort_order": 0,
          "spec": {
            "id": 1,
            "fabric_type": 1,
            "fabric_type_name": "Curtains",
            "model": 1,
            "model_name": "American",
            "catalog_item": 1,
            "catalog_item_name": "Blackout",
            "fabric_code": "LX-2044",
            "unit_price_per_m2": "120.00",
            "fabric_total": "892.80",
            "motor_control_type": "motorized",
            "motor_type": 1,
            "motor_type_name": "American Battery Motor",
            "motor_price_per_unit": "180.00",
            "motor_charge_total": "1339.20",
            "manual_control_total": "0.00",
            "smart_integration": true,
            "alexa_quantity": 1,
            "alexa_unit_price": "200.00",
            "alexa_total": "200.00",
            "pelmet_enabled": true,
            "pelmet_width_cm": "240.00",
            "pelmet_price_per_metre": "90.00",
            "pelmet_total": "216.00",
            "addon_label": "Customization Charge",
            "addon_amount": "50.00",
            "line_item_total": "2698.00"
          }
        }
      ]
    }
  ]
}
```

---

## 4. Update Quotation

### Endpoint
```http
PATCH /api/quotations/{id}/
```

### Request Body Example
```json
{
  "status": "pending",
  "discount_percentage": 10,
  "areas_data": [
    {
      "area_type": "New Room",
      "display_name": "New Room Name",
      "sort_order": 0,
      "surfaces": [
        {
          "surface_name": "New Window",
          "surface_type": "window_curtain_path",
          "width_cm": 300,
          "height_cm": 250,
          "opening_direction": "two_way",
          "sort_order": 0,
          "spec": {
            "fabric_type": 1,
            "model": 1,
            "catalog_item": 1,
            "fabric_code": "NEW-001",
            "unit_price_per_m2": 150.0,
            "motor_control_type": "manual",
            "smart_integration": false,
            "pelmet_enabled": false,
            "pelmet_price_per_metre": 0,
            "addon_amount": 0
          }
        }
      ]
    }
  ]
}
```

### Example Response
```json
{
  "id": "QT-90214",
  "status": "pending",
  "discount_percentage": "10.00",
  "areas": [
    {
      "id": 3,
      "quotation": "QT-90214",
      "area_type": "New Room",
      "display_name": "New Room Name",
      "sort_order": 0,
      "surfaces": [
        {
          "id": 3,
          "surface_name": "New Window",
          "surface_type": "window_curtain_path",
          "width_cm": "300.00",
          "height_cm": "250.00",
          "calculated_area_m2": "7.5000",
          "opening_direction": "two_way",
          "special_requirements": "",
          "sort_order": 0,
          "spec": {
            "id": 3,
            "fabric_type": 1,
            "fabric_type_name": "Curtains",
            "model": 1,
            "model_name": "American",
            "catalog_item": 1,
            "catalog_item_name": "Blackout",
            "fabric_code": "NEW-001",
            "unit_price_per_m2": "150.00",
            "fabric_total": "1125.00",
            "motor_control_type": "manual",
            "motor_type": null,
            "motor_type_name": null,
            "motor_price_per_unit": "0.00",
            "motor_charge_total": "0.00",
            "manual_control_total": "0.00",
            "smart_integration": false,
            "alexa_quantity": 0,
            "alexa_unit_price": "0.00",
            "alexa_total": "0.00",
            "pelmet_enabled": false,
            "pelmet_width_cm": "0.00",
            "pelmet_price_per_metre": "0.00",
            "pelmet_total": "0.00",
            "addon_label": "",
            "addon_amount": "0.00",
            "line_item_total": "1125.00"
          }
        }
      ]
    }
  ]
}
```

---

## 5. Update Quotation Status

### Endpoint
```http
PATCH /api/quotations/{id}/status/
```

### Request Body
```json
{
  "status": "sent",
  "sent_via": "email"
}
```

### Status Flow
```text
draft → pending → sent → accepted
                  ↘ cancelled
```

### Example Response
```json
{
  "id": "QT-90214",
  "status": "sent",
  "sent_date": "2024-07-22T14:30:00Z",
  "sent_via": "email",
  "updated_at": "2024-07-22T14:30:00Z"
}
```

---

## 6. Send Quotation

### Endpoint
```http
PATCH /api/quotations/{id}/send/
```

### Request Body
```json
{
  "sent_via": "whatsapp"
}
```

### Example Response
```json
{
  "id": "QT-90214",
  "status": "sent",
  "sent_via": "whatsapp",
  "sent_date": "2024-07-22T14:30:00Z"
}
```

---

## 7. Accept Quotation

### Endpoint
```http
PATCH /api/quotations/{id}/accept/
```

### Request Body
```json
{}
```

Response
json
{
  "id": "QT-90214",
  "status": "accepted",
  "accepted_date": "2024-07-22T15:00:00Z"
}
8. Cancel Quotation
Endpoint: PATCH /api/quotations/{id}/cancel/

Request Body
json
{
  "cancellation_reason": "Client changed mind"
}
Response
json
{
  "id": "QT-90214",
  "status": "cancelled"
}
9. Duplicate Quotation
Endpoint: POST /api/quotations/{id}/duplicate/

Request Body (Optional)
json
{
  "customer": 2,
  "status": "draft"
}
Response
json
{
  "id": "QT-90215",
  "customer": 2,
  "status": "draft",
  "work_type": 1,
  "quote_type": "b2c",
  "valid_until": "2024-08-22",
  "areas": [
    {
      "id": 4,
      "quotation": "QT-90215",
      "area_type": "Master Bedroom",
      "display_name": "Room of Test",
      "sort_order": 0,
      "surfaces": [
        {
          "id": 4,
          "area": 4,
          "area_name": "Room of Test",
          "surface_name": "Window 01",
          "surface_type": "window_curtain_path",
          "width_cm": "240.00",
          "height_cm": "310.00",
          "calculated_area_m2": "7.4400",
          "opening_direction": "one_way",
          "special_requirements": "",
          "sort_order": 0,
          "spec": {
            "id": 4,
            "surface": 4,
            "fabric_type": 1,
            "fabric_type_name": "Curtains",
            "model": 1,
            "model_name": "American",
            "catalog_item": 1,
            "catalog_item_name": "Blackout",
            "fabric_code": "TEST-001",
            "unit_price_per_m2": "120.00",
            "fabric_total": "892.80",
            "motor_control_type": "motorized",
            "motor_type": 1,
            "motor_type_name": "American Battery Motor",
            "motor_price_per_unit": "180.00",
            "motor_charge_total": "1339.20",
            "manual_control_total": "0.00",
            "smart_integration": true,
            "alexa_quantity": 1,
            "alexa_unit_price": "200.00",
            "alexa_total": "200.00",
            "pelmet_enabled": true,
            "pelmet_width_cm": "240.00",
            "pelmet_price_per_metre": "90.00",
            "pelmet_total": "216.00",
            "addon_label": "Customization",
            "addon_amount": "50.00",
            "line_item_total": "2698.00"
          }
        }
      ]
    }
  ]
}
10. Get Quotation Statistics
Endpoint: GET /api/quotations/stats/

Response
json
{
  "total": 24,
  "by_status": {
    "draft": 3,
    "pending": 5,
    "sent": 8,
    "accepted": 6,
    "cancelled": 2
  },
  "total_value": "1245000.00",
  "accepted_value": "892000.00",
  "pending_value": "235000.00",
  "this_month": 12
}
11. Delete Quotation (Soft Delete)
Endpoint: DELETE /api/quotations/{id}/

This performs a soft delete - sets status to "cancelled".

Response
json
{
  "message": "Quotation QT-90214 has been cancelled.",
  "quotation": {
    "id": "QT-90214",
    "status": "cancelled"
  }
}
Status Codes
Status Code	Description
200	Success (GET, PATCH, DELETE)
201	Created (POST)
400	Bad Request (Validation error)
401	Unauthorized (Authentication required)
403	Forbidden (Permission denied)
404	Not Found
Error Responses
Validation Error (400)
json
{
  "discount_percentage": ["Discount cannot exceed 100%."]
}
Authentication Error (401)
json
{
  "detail": "Authentication credentials were not provided."
}
Permission Error (403)
json
{
  "error": "You don't have permission to perform this action."
}
Not Found (404)
json
{
  "detail": "Not found."
}
Field Descriptions
Quotation Fields
Field	Type	Description
id	string	Auto-generated ID (e.g., QT-90214)
customer	integer	Customer ID
appointment	integer	Appointment ID
status	string	draft, pending, sent, accepted, cancelled
quote_type	string	b2c (Retail), b2b (Business)
work_type	integer	Work type ID from catalog
subtotal	decimal	Total before VAT and discount
vat	decimal	VAT amount (5%)
total	decimal	Grand total
discount_percentage	decimal	Discount percentage (0-100)
discount_amount	decimal	Discount amount
valid_until	date	Quotation validity date
issued_date	date	Date issued
sent_date	datetime	When sent to customer
sent_via	string	email, whatsapp, sms
prepared_by	integer	User ID who prepared the quote
accepted_date	datetime	When accepted by customer
Area Fields
Field	Type	Description
area_type	string	Room type (e.g., "Living Room")
display_name	string	Display name for the area
sort_order	integer	Order in the quotation
Surface Fields
Field	Type	Description
surface_name	string	Name of the surface
surface_type	string	window_curtain_path, wall_to_wall_track, bay_window, sliding_door
width_cm	decimal	Width in centimeters
height_cm	decimal	Height in centimeters
calculated_area_m2	decimal	Auto-calculated area in m²
opening_direction	string	one_way, two_way
special_requirements	text	Special instructions
Surface Spec Fields
Field	Type	Description
fabric_type	integer	Fabric type ID from catalog
model	integer	Model ID from catalog
catalog_item	integer	Catalog item ID
fabric_code	string	Custom fabric code
unit_price_per_m2	decimal	Price per square metre
fabric_total	decimal	Auto-calculated fabric total
motor_control_type	string	manual, motorized
motor_type	integer	Motor type ID from catalog
motor_price_per_unit	decimal	Motor price per unit
motor_charge_total	decimal	Auto-calculated motor charge
manual_control_total	decimal	Manual control charge
smart_integration	boolean	With Alexa integration
alexa_quantity	integer	Number of Alexa units
alexa_unit_price	decimal	Price per Alexa unit
alexa_total	decimal	Auto-calculated Alexa total
pelmet_enabled	boolean	Pelmet included
pelmet_width_cm	decimal	Pelmet width in cm
pelmet_price_per_metre	decimal	Price per metre
pelmet_total	decimal	Auto-calculated pelmet total
addon_label	string	Label for custom add-on
addon_amount	decimal	Custom add-on amount
line_item_total	decimal	Auto-calculated total for this spec
Quick Reference - cURL Examples
Create Quotation
bash
curl -X POST http://localhost:8000/api/quotations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer": 1,
    "appointment": 1,
    "work_type": 1,
    "status": "draft",
    "quote_type": "b2c",
    "valid_until": "2024-08-22",
    "discount_percentage": 0,
    "areas_data": []
  }'
List Quotations
bash
curl -X GET "http://localhost:8000/api/quotations/?status=draft&search=Mariam" \
  -H "Authorization: Bearer YOUR_TOKEN"
Update Status
bash
curl -X PATCH http://localhost:8000/api/quotations/QT-90214/status/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "sent", "sent_via": "email"}'
Duplicate Quotation
bash
curl -X POST http://localhost:8000/api/quotations/QT-90214/duplicate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer": 2}'
Get Statistics
bash
curl -X GET http://localhost:8000/api/quotations/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
Test Credentials
json
{
  "admin": {
    "email": "admin@example.com",
    "password": "adminpass123"
  },
  "salesman": {
    "email": "salesman@example.com",
    "password": "salesmanpass123"
  }
}
