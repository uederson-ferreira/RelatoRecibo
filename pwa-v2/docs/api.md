# API Documentation - RelatoRecibo Backend

## Base URL

```bash
Development: http://localhost:3000/api
Production: https://api.relatorecibo.com/api
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

The JWT token is obtained from Supabase Auth after successful login/signup.

---

## Endpoints

### Authentication - Autenticação

#### `POST /auth/signup`

Register a new user.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "João Silva"
}
```

**Response:** `201 Created`

```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "João Silva"
  },
  "session": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "expires_in": 3600
  }
}
```

#### `POST /auth/login`

Login existing user.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`

```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "João Silva"
  },
  "session": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "expires_in": 3600
  }
}
```

#### `POST /auth/logout`

Logout current user.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

```json
{
  "message": "Logged out successfully"
}
```

#### `POST /auth/refresh`

Refresh access token.

**Request:**

```json
{
  "refresh_token": "refresh_token"
}
```

**Response:** `200 OK`

```json
{
  "access_token": "new_jwt_token",
  "refresh_token": "new_refresh_token",
  "expires_in": 3600
}
```

---

### Profile

#### `GET /profile`

Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "João Silva",
  "avatar_url": "https://...",
  "created_at": "2025-12-08T10:00:00Z",
  "updated_at": "2025-12-08T10:00:00Z"
}
```

#### `PUT /profile`

Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request:**

```json
{
  "full_name": "João da Silva",
  "avatar_url": "https://..."
}
```

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "João da Silva",
  "avatar_url": "https://...",
  "updated_at": "2025-12-08T11:00:00Z"
}
```

#### `GET /profile/stats`

Get user statistics.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

```json
{
  "total_reports": 15,
  "total_receipts": 87,
  "total_value": 12450.50,
  "draft_reports": 3,
  "completed_reports": 12,
  "avg_receipts_per_report": 5.8,
  "avg_value_per_receipt": 143.11
}
```

---

### Reports

#### `GET /reports`

List all reports for the authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

- `status` (optional): Filter by status (`draft`, `completed`, `archived`)
- `limit` (optional): Number of results (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)
- `sort` (optional): Sort field (default: `created_at`)
- `order` (optional): Sort order (`asc` or `desc`, default: `desc`)

**Response:** `200 OK`

```json
{
  "reports": [
    {
      "id": "uuid",
      "name": "Viagem São Paulo - Dezembro 2025",
      "description": "Despesas da viagem de negócios",
      "target_value": 5000.00,
      "total_value": 4235.50,
      "receipts_count": 12,
      "status": "draft",
      "created_at": "2025-12-01T10:00:00Z",
      "updated_at": "2025-12-08T15:30:00Z",
      "completed_at": null
    }
  ],
  "pagination": {
    "total": 15,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

#### `GET /reports/:id`

Get a specific report with summary.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "name": "Viagem São Paulo - Dezembro 2025",
  "description": "Despesas da viagem de negócios",
  "target_value": 5000.00,
  "total_value": 4235.50,
  "receipts_count": 12,
  "status": "draft",
  "progress_percentage": 84.71,
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-08T15:30:00Z",
  "completed_at": null,
  "earliest_receipt_date": "2025-12-01",
  "latest_receipt_date": "2025-12-08",
  "avg_receipt_value": 352.96,
  "min_receipt_value": 25.00,
  "max_receipt_value": 850.00
}
```

#### `POST /reports`

Create a new report.

**Headers:** `Authorization: Bearer <token>`

**Request:**

```json
{
  "name": "Viagem São Paulo - Dezembro 2025",
  "description": "Despesas da viagem de negócios",
  "target_value": 5000.00
}
```

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "name": "Viagem São Paulo - Dezembro 2025",
  "description": "Despesas da viagem de negócios",
  "target_value": 5000.00,
  "total_value": 0.00,
  "receipts_count": 0,
  "status": "draft",
  "created_at": "2025-12-08T16:00:00Z",
  "updated_at": "2025-12-08T16:00:00Z"
}
```

#### `PUT /reports/:id`

Update an existing report.

**Headers:** `Authorization: Bearer <token>`

**Request:**

```json
{
  "name": "Viagem SP - Dez/2025",
  "description": "Atualizado",
  "target_value": 5500.00,
  "status": "completed"
}
```

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "name": "Viagem SP - Dez/2025",
  "description": "Atualizado",
  "target_value": 5500.00,
  "total_value": 4235.50,
  "receipts_count": 12,
  "status": "completed",
  "updated_at": "2025-12-08T16:30:00Z",
  "completed_at": "2025-12-08T16:30:00Z"
}
```

#### `DELETE /reports/:id`

Delete a report and all associated receipts.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

#### `POST /reports/:id/duplicate`

Duplicate a report (without receipts).

**Headers:** `Authorization: Bearer <token>`

**Response:** `201 Created`

```json
{
  "id": "new_uuid",
  "name": "Viagem SP - Dez/2025 (Cópia)",
  "description": "Atualizado",
  "target_value": 5500.00,
  "total_value": 0.00,
  "receipts_count": 0,
  "status": "draft",
  "created_at": "2025-12-08T17:00:00Z"
}
```

#### `GET /reports/:id/pdf`

Generate and download PDF report.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="relatorio-{name}-{date}.pdf"`

---

### Receipts

#### `GET /reports/:reportId/receipts`

List all receipts for a specific report.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

- `limit` (optional): Number of results (default: 50, max: 200)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`

```json
{
  "receipts": [
    {
      "id": "uuid",
      "report_id": "uuid",
      "value": 450.00,
      "date": "2025-12-05",
      "description": "Hotel - 2 diárias",
      "notes": "Check-in 03/12, Check-out 05/12",
      "image_url": "https://supabase.co/storage/.../image.jpg",
      "thumbnail_url": "https://supabase.co/storage/.../thumb.jpg",
      "ocr_text": "Total R$ 450,00...",
      "ocr_confidence": 92.5,
      "ocr_status": "processed",
      "created_at": "2025-12-05T20:30:00Z",
      "updated_at": "2025-12-05T20:30:00Z"
    }
  ],
  "pagination": {
    "total": 12,
    "limit": 50,
    "offset": 0
  }
}
```

#### `GET /receipts/:id`

Get a specific receipt.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "report_id": "uuid",
  "value": 450.00,
  "date": "2025-12-05",
  "description": "Hotel - 2 diárias",
  "notes": "Check-in 03/12, Check-out 05/12",
  "image_url": "https://...",
  "ocr_text": "...",
  "ocr_confidence": 92.5,
  "created_at": "2025-12-05T20:30:00Z"
}
```

#### `POST /reports/:reportId/receipts`

Upload a new receipt with OCR processing.

**Headers:**

- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request (multipart/form-data):**

```bash
file: [image file] (required)
value: "450.00" (optional - will be extracted by OCR if not provided)
date: "2025-12-05" (optional - defaults to today)
description: "Hotel - 2 diárias" (optional)
notes: "Check-in 03/12" (optional)
```

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "report_id": "uuid",
  "value": 450.00,
  "date": "2025-12-05",
  "description": "Hotel - 2 diárias",
  "notes": "Check-in 03/12, Check-out 05/12",
  "image_url": "https://...",
  "ocr_text": "Hotel XYZ\nTotal: R$ 450,00\n...",
  "ocr_confidence": 92.5,
  "ocr_status": "processed",
  "created_at": "2025-12-05T20:30:00Z"
}
```

#### `PUT /receipts/:id`

Update a receipt.

**Headers:** `Authorization: Bearer <token>`

**Request:**

```json
{
  "value": 475.00,
  "description": "Hotel - 2 diárias (atualizado)",
  "notes": "Incluído café da manhã"
}
```

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "value": 475.00,
  "description": "Hotel - 2 diárias (atualizado)",
  "notes": "Incluído café da manhã",
  "updated_at": "2025-12-08T18:00:00Z"
}
```

#### `DELETE /receipts/:id`

Delete a receipt.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

#### `POST /receipts/bulk-delete`

Delete multiple receipts at once.

**Headers:** `Authorization: Bearer <token>`

**Request:**

```json
{
  "receipt_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:** `200 OK`

```json
{
  "deleted_count": 3
}
```

---

### Search

#### `GET /search/reports`

Full-text search for reports.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

- `q` (required): Search query
- `status` (optional): Filter by status
- `limit` (optional): Number of results (default: 20)
- `offset` (optional): Pagination offset

**Response:** `200 OK`

```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Viagem São Paulo",
      "description": "...",
      "total_value": 4235.50,
      "status": "completed",
      "rank": 0.85
    }
  ],
  "total": 5
}
```

---

## Error Responses

### Error Format

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {} // Optional additional details
  }
}
```

### HTTP Status Codes

- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate email)
- `413 Payload Too Large` - File upload too large (max 5MB)
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Common Error Codes

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "fields": {
        "email": "Invalid email format",
        "password": "Password must be at least 8 characters"
      }
    }
  }
}
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Report not found"
  }
}
```

```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds 5MB limit"
  }
}
```

```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Only JPEG, PNG, and WebP images are allowed"
  }
}
```

---

## Rate Limiting

- **Authentication endpoints:** 5 requests per minute per IP
- **Upload endpoints:** 10 requests per minute per user
- **Other endpoints:** 100 requests per minute per user

Rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702234567
```

---

## File Upload Constraints

- **Max file size:** 5MB
- **Allowed formats:** JPEG, JPG, PNG, WebP
- **Recommended resolution:** 1920x1080 or lower
- **Compression:** Images are automatically optimized server-side

---

## Webhooks (Future Feature)

Coming in Phase 2:

- `receipt.created`
- `receipt.ocr.completed`
- `report.completed`

---

## SDK Example (Frontend)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Example: Upload receipt
const uploadReceipt = async (reportId: string, file: File, data: any) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('value', data.value);
  formData.append('description', data.description);

  const response = await api.post(
    `/reports/${reportId}/receipts`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );

  return response.data;
};
```
