"""
Full Frontend API Documentation
Alumni ML Pipeline React Application

This document outlines all API endpoints used by the frontend.
"""

# Authentication Endpoints

## POST /auth/login
Record an alumni engagement event
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```
- **Response (200):**
  ```json
  {
    "token": "jwt-token",
    "user": {
      "id": "user123",
      "name": "John Doe",
      "email": "john@example.com",
      "permissions": ["read:alumni", "write:engagement"]
    }
  }
  ```

## POST /auth/logout
Logout current user
- **Response (200):** Empty

## POST /auth/refresh
Refresh authentication token
- **Response (200):**
  ```json
  {
    "token": "new-jwt-token"
  }
  ```

---

# Alumni Endpoints

## GET /alumni/{alumniId}
Get alumni profile and donation score
- **Path Parameters:**
  - `alumniId` (string, required): Alumni identifier
- **Response (200):**
  ```json
  {
    "alumni_id": "ALUM001",
    "name": "John Doe",
    "email": "john@alumni.edu",
    "graduation_year": 2012,
    "department": "Computer Science",
    "current_role": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "donation_score": 0.85,
    "engagement_level": "high",
    "total_donations": 15000,
    "last_engagement": "2026-02-16",
    "donation_history": [...],
    "engagement_events": [...],
    "predicted_score": 0.89
  }
  ```

## POST /alumni/engagement
Record an alumni engagement event
- **Request Body:**
  ```json
  {
    "alumni_id": "ALUM001",
    "event_type": "attendance|newsletter|login|feedback|volunteer",
    "event_date": "2026-02-16",
    "details": "Optional details"
  }
  ```
- **Response (200):**
  ```json
  {
    "message": "Engagement recorded",
    "alumni_id": "ALUM001",
    "event_id": "EVT-12345"
  }
  ```

## POST /alumni/donation
Record a donation from an alumni
- **Request Body:**
  ```json
  {
    "alumni_id": "ALUM001",
    "amount": 5000.00,
    "fund_type": "general|scholarship|infrastructure|research",
    "donation_date": "2026-02-16",
    "payment_method": "card|bank|check|cryptocurrency",
    "notes": "Optional notes"
  }
  ```
- **Response (200):**
  ```json
  {
    "message": "Donation recorded",
    "alumni_id": "ALUM001",
    "reference_id": "DONATE-ALUM001-123456",
    "amount": 5000.00
  }
  ```

## POST /alumni/forecast
Generate donation forecast for a segment
- **Request Body:**
  ```json
  {
    "segment": "recent_grads|early_career|mid_career|executives",
    "fund_type": "general|scholarship|infrastructure",
    "month": 6
  }
  ```
- **Response (200):**
  ```json
  {
    "segment": "mid_career",
    "predicted_donors": 150,
    "projected_amount": 500000,
    "confidence": 0.87,
    "average_donation": 3333.33,
    "trend": [
      {
        "month": "Jul",
        "donors": 45,
        "amount": 25000
      },
      ...
    ],
    "recommendations": [
      "Target high-engagement alumni first"
    ]
  }
  ```

## GET /alumni/insights
Get GenAI insights about alumni data
- **Query Parameters:**
  - `question` (string, required): Question about alumni data
- **Response (200):**
  ```json
  {
    "question": "Which segment donates most?",
    "answer": "Based on our analysis...",
    "confidence": 0.92,
    "recommendations": [
      "Target this segment with premium events"
    ]
  }
  ```

## GET /alumni/search
Search for alumni
- **Query Parameters:**
  - `q` (string, required): Search query (name, email, ID)
  - `limit` (number, optional): Max results, default 20
- **Response (200):**
  ```json
  {
    "results": [
      {
        "alumni_id": "ALUM001",
        "name": "John Doe",
        "email": "john@alumni.edu",
        "donation_score": 0.85
      }
    ],
    "total": 1
  }
  ```

---

# Error Responses

## 400 Bad Request
```json
{
  "error": "Invalid request format",
  "details": "Field 'amount' is required"
}
```

## 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

## 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

## 404 Not Found
```json
{
  "error": "Alumni not found"
}
```

## 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Please try again later"
}
```

---

# Authentication

All authenticated endpoints require:
```
Authorization: Bearer <jwt-token>
```

The token is automatically:
1. Retrieved from localStorage after login
2. Added to all API requests
3. Refreshed on 401 responses
4. Cleared on logout

---

# Rate Limiting

- **Limit:** 100 requests per minute per user
- **Response Header:** `X-RateLimit-Remaining`
- **Error (429):**
  ```json
  {
    "error": "Rate limit exceeded",
    "retry_after": 60
  }
  ```

---

# Pagination

Endpoints returning lists support pagination:
- **Query Parameters:**
  - `page` (number, default 1): Page number
  - `limit` (number, default 20): Items per page
  - `sort` (string, default name): Sort field
  - `order` (asc|desc, default asc): Sort order

---

# Filtering & Sorting

### Alumni Filtering
```
GET /alumni?department=CS&graduation_year=2012&engagement_level=high
```

### Sorting Example
```
GET /alumni?sort=donation_score&order=desc&limit=50
```

---

# Webhook Events (Optional)

When implemented, the backend may send webhooks:

### donation.created
```json
{
  "event": "donation.created",
  "data": {
    "donation_id": "DON-123",
    "alumni_id": "ALUM001",
    "amount": 5000.00
  }
}
```

### engagement.recorded
```json
{
  "event": "engagement.recorded",
  "data": {
    "alumni_id": "ALUM001",
    "event_type": "attendance",
    "timestamp": "2026-02-16T10:30:00Z"
  }
}
```
