# CurtainMaster Orders API

This document describes the Orders, Invoices, and Payments API endpoints for the Curtain Master backend.

## Base URL

```text
http://localhost:8000/api/
```

## Authentication

All API endpoints require authentication using a JWT token.

```http
Authorization: Bearer <access_token>
```

---

## 1. Orders API

### 1.1 List Orders

**Endpoint**
```http
GET /api/orders/
```

**Query Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| status | string | Filter by order status |
| customer | integer | Filter by customer ID |
| quotation | string | Filter by quotation ID |
| search | string | Search by ID or customer |

**Example Response**
```json
[
  {
    "id": 1,
    "quotation": "QT-90214",
    "quotation_id": "QT-90214",
    "customer": 1,
    "customer_name": "Mariam Al Mansouri",
    "customer_phone": "+971501234567",
    "order_status": "pending_production",
    "estimated_production_days": 21,
    "invoice": "INV-2041",
    "invoice_id": "INV-2041",
    "invoice_status": "sent",
    "created_at": "2024-07-22T10:00:00Z",
    "updated_at": "2024-07-22T10:00:00Z"
  }
]
```

### 1.2 Create Order

**Endpoint**
```http
POST /api/orders/
```

**Request Body**
```json
{
  "quotation": "QT-90214",
  "customer": 1,
  "order_status": "pending_production",
  "estimated_production_days": 21
}
```

**Validation Rules**
- Quotation must be in accepted status
- Only one order per quotation
- Customer must exist

**Example Response**
```json
{
  "id": 2,
  "quotation": "QT-90215",
  "customer": 1,
  "order_status": "pending_production",
  "estimated_production_days": 21,
  "created_at": "2024-07-22T10:00:00Z",
  "updated_at": "2024-07-22T10:00:00Z"
}
```

### 1.3 Get Order Details

**Endpoint**
```http
GET /api/orders/{id}/
```

**Example Response**
```json
{
  "id": 1,
  "quotation": "QT-90214",
  "quotation_id": "QT-90214",
  "customer": 1,
  "customer_name": "Mariam Al Mansouri",
  "customer_phone": "+971501234567",
  "order_status": "pending_production",
  "estimated_production_days": 21,
  "invoice": "INV-2041",
  "invoice_id": "INV-2041",
  "invoice_status": "sent",
  "created_at": "2024-07-22T10:00:00Z",
  "updated_at": "2024-07-22T10:00:00Z"
}
```

### 1.4 Update Order Status

**Endpoint**
```http
PATCH /api/orders/{id}/status/
```

**Request Body**
```json
{
  "order_status": "in_production"
}
```

**Status Flow**
```text
pending_production → in_production → shipped → installed → closed
```

**Example Response**
```json
{
  "id": 1,
  "order_status": "in_production",
  "updated_at": "2024-07-22T10:30:00Z"
}
```

### 1.5 Generate Invoice from Order

**Endpoint**
```http
POST /api/orders/{id}/generate-invoice/
```

**Request Body**
```json
{}
```

**Example Response**
```json
{
  "id": "INV-2042",
  "order": 1,
  "customer": 1,
  "status": "draft",
  "total_amount": "12450.00",
  "amount_paid": "0.00",
  "balance_due": "12450.00",
  "due_date": "2024-08-05",
  "issued_date": "2024-07-22",
  "payment_terms": "Full payment on invoice",
  "payment_url": "",
  "sent_date": null,
  "sent_via": "",
  "quotation_id": "QT-90214",
  "payments": []
}
```

### 1.6 Order Statistics

**Endpoint**
```http
GET /api/orders/stats/
```

**Example Response**
```json
{
  "total": 24,
  "by_status": {
    "pending_production": 8,
    "in_production": 6,
    "shipped": 4,
    "installed": 4,
    "closed": 2
  },
  "pending_production": 8,
  "in_production": 6,
  "shipped": 4,
  "installed": 4,
  "closed": 2
}
```

### 1.7 Delete Order (Soft Delete)

**Endpoint**
```http
DELETE /api/orders/{id}/
```

**Validation**
- Cannot delete closed orders
- Cannot delete orders with payments

**Example Response**
```json
{
  "message": "Order 1 has been cancelled.",
  "order": {
    "id": 1,
    "order_status": "cancelled"
  }
}
```

---

## 2. Invoices API

### 2.1 List Invoices

**Endpoint**
```http
GET /api/invoices/
```

**Query Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| status | string | Filter by status |
| customer | integer | Filter by customer ID |
| date_from | date | Filter from issued date |
| date_to | date | Filter to issued date |
| search | string | Search by ID or customer |

**Example Response**
```json
[
  {
    "id": "INV-2041",
    "order": 1,
    "order_id": 1,
    "customer": 1,
    "customer_name": "Mariam Al Mansouri",
    "customer_phone": "+971501234567",
    "customer_email": "mariam.m@example.com",
    "status": "sent",
    "status_display": "Sent",
    "total_amount": "12450.00",
    "amount_paid": "0.00",
    "balance_due": "12450.00",
    "due_date": "2024-08-05",
    "issued_date": "2024-07-22",
    "payment_terms": "Full payment on invoice",
    "payment_url": "",
    "sent_date": null,
    "sent_via": "",
    "quotation_id": "QT-90214",
    "payments": [],
    "created_at": "2024-07-22T10:00:00Z",
    "updated_at": "2024-07-22T10:00:00Z"
  }
]
```

### 2.2 Create Invoice

**Endpoint**
```http
POST /api/invoices/
```

**Request Body**
```json
{
  "order": 1,
  "customer": 1,
  "total_amount": 12450.0,
  "due_date": "2024-08-05",
  "payment_terms": "50% advance, balance on installation",
  "payment_url": "https://pay.curtainmaster.ae/i/INV-2041"
}
```

**Example Response**
```json
{
  "id": "INV-2041",
  "order": 1,
  "customer": 1,
  "status": "draft",
  "total_amount": "12450.00",
  "amount_paid": "0.00",
  "balance_due": "12450.00",
  "due_date": "2024-08-05",
  "issued_date": "2024-07-22",
  "payment_terms": "50% advance, balance on installation",
  "payment_url": "https://pay.curtainmaster.ae/i/INV-2041",
  "payments": []
}
```

### 2.3 Get Invoice Details

**Endpoint**
```http
GET /api/invoices/{id}/
```

**Response**
Full invoice details with payments.

### 2.4 Update Invoice Status

**Endpoint**
```http
PATCH /api/invoices/{id}/status/
```

**Request Body**
```json
{
  "status": "paid",
  "sent_via": "email"
}
```

**Status Values**
- `draft`
- `sent`
- `overdue`
- `paid`
- `partially_paid`

**Example Response**
```json
{
  "id": "INV-2041",
  "status": "paid",
  "amount_paid": "12450.00",
  "balance_due": "0.00"
}
```

### 2.5 Send Invoice

**Endpoint**
```http
PATCH /api/invoices/{id}/send/
```

**Request Body**
```json
{
  "sent_via": "whatsapp"
}
```

**Example Response**
```json
{
  "id": "INV-2041",
  "status": "sent",
  "sent_via": "whatsapp",
  "sent_date": "2024-07-22T10:30:00Z"
}
```

### 2.6 Add Payment to Invoice

**Endpoint**
```http
POST /api/invoices/{id}/add-payment/
```

**Request Body**
```json
{
  "amount": 6225.0,
  "method": "bank_transfer",
  "reference": "BNK-44821",
  "payment_date": "2024-07-22",
  "notes": "50% advance payment"
}
```

**Payment Methods**
- `cash`
- `card`
- `bank_transfer`
- `cheque`

**Example Response**
```json
{
  "id": "INV-2041",
  "status": "partially_paid",
  "amount_paid": "6225.00",
  "balance_due": "6225.00",
  "payments": [
    {
      "id": 1,
      "amount": "6225.00",
      "method": "bank_transfer",
      "reference": "BNK-44821",
      "payment_date": "2024-07-22",
      "notes": "50% advance payment",
      "created_by_name": "Basheer"
    }
  ]
}
```

### 2.7 Invoice Statistics

**Endpoint**
```http
GET /api/invoices/stats/
```

**Example Response**
```json
{
  "total": 24,
  "by_status": {
    "draft": 3,
    "sent": 8,
    "overdue": 2,
    "paid": 9,
    "partially_paid": 2
  },
  "total_amount": "1245000.00",
  "total_paid": "892000.00",
  "total_due": "353000.00",
  "overdue": 2
}
```

### 2.8 Delete Invoice (Soft Delete)

**Endpoint**
```http
DELETE /api/invoices/{id}/
```

**Validation**
- Cannot delete invoices with payments
- Cannot delete paid invoices

**Example Response**
```json
{
  "message": "Invoice INV-2041 has been cancelled.",
  "invoice": {
    "id": "INV-2041",
    "status": "cancelled"
  }
}
```

---

## 3. Payments API

### 3.1 List Payments

**Endpoint**
```http
GET /api/payments/
```

**Query Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| invoice | string | Filter by invoice ID |
| method | string | Filter by payment method |
| date_from | date | Filter from payment date |
| date_to | date | Filter to payment date |

Response:

json
[
  {
    "id": 1,
    "invoice": "INV-2041",
    "invoice_number": "INV-2041",
    "amount": "6225.00",
    "method": "bank_transfer",
    "reference": "BNK-44821",
    "payment_date": "2024-07-22",
    "notes": "50% advance payment",
    "created_by": 1,
    "created_by_name": "Basheer",
    "created_at": "2024-07-22T10:00:00Z"
  }
]
3.2 Create Payment
Endpoint: POST /api/payments/

Request Body:

json
{
  "invoice": "INV-2041",
  "amount": 6225.00,
  "method": "bank_transfer",
  "reference": "BNK-44821",
  "payment_date": "2024-07-22",
  "notes": "50% advance payment"
}
Response (201 Created):

json
{
  "id": 2,
  "invoice": "INV-2041",
  "invoice_number": "INV-2041",
  "amount": "6225.00",
  "method": "bank_transfer",
  "reference": "BNK-44821",
  "payment_date": "2024-07-22",
  "notes": "50% advance payment",
  "created_by": 1,
  "created_by_name": "Basheer",
  "created_at": "2024-07-22T10:05:00Z"
}
3.3 Delete Payment
Endpoint: DELETE /api/payments/{id}/

Response:

json
{
  "message": "Payment deleted successfully.",
  "invoice": {
    "id": "INV-2041",
    "status": "sent",
    "amount_paid": "0.00",
    "balance_due": "12450.00"
  }
}
4. Error Responses
Validation Error (400)
json
{
  "quotation": ["An order already exists for this quotation."]
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
5. Field Descriptions
Order Fields
Field	Type	Description
id	integer	Auto-generated ID
quotation	string	Quotation ID
quotation_id	string	Quotation ID (readable)
customer	integer	Customer ID
customer_name	string	Customer full name
customer_phone	string	Customer phone number
order_status	string	pending_production, in_production, shipped, installed, closed, cancelled
estimated_production_days	integer	Estimated days for production
invoice	string	Invoice ID (if exists)
invoice_status	string	Invoice status
Invoice Fields
Field	Type	Description
id	string	Auto-generated ID (e.g., INV-2041)
order	integer	Order ID
customer	integer	Customer ID
status	string	draft, sent, overdue, paid, partially_paid
total_amount	decimal	Total invoice amount
amount_paid	decimal	Total paid amount
balance_due	decimal	Remaining balance
due_date	date	Payment due date
issued_date	date	Invoice issue date
payment_terms	string	Payment terms description
payment_url	string	Payment gateway link
sent_date	datetime	When invoice was sent
sent_via	string	email, whatsapp
Payment Fields
Field	Type	Description
id	integer	Auto-generated ID
invoice	string	Invoice ID
amount	decimal	Payment amount
method	string	cash, card, bank_transfer, cheque
reference	string	Bank reference, cheque number, etc.
payment_date	date	Payment date
notes	string	Additional notes
6. Workflow Summary
text
Quotation (accepted) 
    ↓
Order (pending_production) 
    ↓
Invoice (generated) → Invoice (sent) → Payment (received) → Invoice (paid)
    ↓
Order → in_production → shipped → installed → closed
Status Values
Order Status:

pending_production - Order created, awaiting production

in_production - In production

shipped - Shipped to customer

installed - Installed at customer site

closed - Order completed

cancelled - Order cancelled (soft delete)

Invoice Status:

draft - Invoice created but not sent

sent - Invoice sent to customer

overdue - Payment overdue

partially_paid - Partial payment received

paid - Fully paid

7. cURL Examples
Create Order
bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quotation": "QT-90214",
    "customer": 1,
    "order_status": "pending_production"
  }'
Generate Invoice
bash
curl -X POST http://localhost:8000/api/orders/1/generate-invoice/ \
  -H "Authorization: Bearer YOUR_TOKEN"
Add Payment to Invoice
bash
curl -X POST http://localhost:8000/api/invoices/INV-2041/add-payment/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 6225.00,
    "method": "bank_transfer",
    "reference": "BNK-44821",
    "payment_date": "2024-07-22"
  }'
Update Invoice Status
bash
curl -X PATCH http://localhost:8000/api/invoices/INV-2041/status/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "paid"}'
Update Order Status
bash
curl -X PATCH http://localhost:8000/api/orders/1/status/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_status": "in_production"}'
Get Statistics
bash
curl -X GET http://localhost:8000/api/orders/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
8. Test Credentials
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
9. Changelog

| Version | Date       | Changes                                |
|---------|------------|----------------------------------------|
| 1.0.0   | 2024-07-22 | Initial API release                    |

**Features Included:**
- ✅ Order management
- ✅ Invoice management
- ✅ Payment management
- ✅ Full CRUD operations
- ✅ Statistics endpoints

---

## Support

For issues or questions, contact the development team at support@curtainmaster.ae

**Last Updated:** 2024-07-22
