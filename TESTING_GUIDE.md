# Testing Guide - Frontend & Backend Integration

This guide shows you how to verify that your React frontend and Flask backend are properly connected.

---

## ✅ Pre-Test Checklist

- [ ] Backend running on `http://localhost:5000`
- [ ] Frontend running on `http://localhost:3000`
- [ ] Both show no errors in console
- [ ] Browser has no CORS errors

---

## 🧪 Test 1: Health Check (Verify Backend is Running)

### Via Browser
```
GET http://localhost:5000/api/health
```

1. Open new browser tab
2. Navigate to: `http://localhost:5000/api/health`
3. Should see JSON response

Expected Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-16T10:30:45.123456",
  "version": "1.0.0"
}
```

### Via Terminal (cURL)
```bash
curl http://localhost:5000/api/health
```

**Status**: ✅ PASS if you see JSON response

---

## 🧪 Test 2: Login (Authentication)

### Via Frontend
1. Open `http://localhost:3000`
2. Should be redirected to `/login`
3. Enter credentials:
   - Email: `user@alumni.edu`
   - Password: `user123`
4. Click "Sign In"

Expected Result:
- ✅ Redirected to Dashboard
- ✅ Token saved in localStorage (check DevTools → Application → localStorage)
- ✅ No CORS errors in console

### Via cURL
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@alumni.edu","password":"user123"}'
```

Expected Response:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "email": "user@alumni.edu",
    "name": "Regular User",
    "role": "user"
  }
}
```

**Status**: ✅ PASS if you get a token and user info

---

## 🧪 Test 3: View Protected Endpoint (JWT Authorization)

### Prerequisites
- You must have a valid JWT token from Test 2
- Save the token: `TOKEN="eyJ0eXAi..."`

### Via cURL
```bash
# Replace with token from Test 2
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X GET http://localhost:5000/api/alumni/ALUM001 \
  -H "Authorization: Bearer $TOKEN"
```

Expected Response:
```json
{
  "alumni_id": "ALUM001",
  "name": "Alumni User ALUM001",
  "email": "ALUM001@alumni.edu",
  "graduation_year": 2015,
  "department": "Computer Science",
  "engagement_level": "high",
  "donation_score": 0.75,
  "last_engagement": "2026-02-16T10:00:00.000000",
  "total_donations": 5000.0,
  "donation_count": 3
}
```

### Via Frontend
1. Login (Test 2)
2. Click on any alumni in the search/list
3. Should see profile details

**Status**: ✅ PASS if you see alumni data

---

## 🧪 Test 4: Record Engagement (POST Request)

### Via Frontend
1. Navigate to "Record Engagement"
2. Fill form:
   - Alumni ID: `ALUM001`
   - Event Type: `attendance`
   - Description: `Attended networking event`
3. Click "Record Engagement"
4. Should see success message

### Via cURL
```bash
TOKEN="eyJ0eXAi..."

curl -X POST http://localhost:5000/api/alumni/engagement \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alumni_id": "ALUM001",
    "event_type": "attendance",
    "description": "Attended networking event",
    "date": "2026-02-16"
  }'
```

Expected Response:
```json
{
  "message": "Engagement recorded successfully",
  "alumni_id": "ALUM001",
  "event_type": "attendance",
  "timestamp": "2026-02-16T10:35:12.654321"
}
```

**Status**: ✅ PASS if engagement is recorded with timestamp

---

## 🧪 Test 5: Record Donation (POST Request)

### Via Frontend
1. Navigate to "Record Donation"
2. Fill form:
   - Alumni ID: `ALUM002`
   - Amount: `500`
   - Fund Type: `scholarship`
3. Click "Record Donation"
4. Should see success message

### Via cURL
```bash
TOKEN="eyJ0eXAi..."

curl -X POST http://localhost:5000/api/alumni/donation \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alumni_id": "ALUM002",
    "amount": 500,
    "fund_type": "scholarship",
    "date": "2026-02-16"
  }'
```

Expected Response:
```json
{
  "message": "Donation recorded successfully",
  "alumni_id": "ALUM002",
  "amount": 500,
  "reference_id": "DONATE-ALUM002-1708074912",
  "timestamp": "2026-02-16T10:35:12.654321"
}
```

**Status**: ✅ PASS if donation is recorded with reference ID

---

## 🧪 Test 6: Get Engagement History (GET Request)

### Via cURL
```bash
TOKEN="eyJ0eXAi..."

curl -X GET http://localhost:5000/api/alumni/engagement/ALUM001 \
  -H "Authorization: Bearer $TOKEN"
```

Expected Response:
```json
{
  "alumni_id": "ALUM001",
  "total_events": 1,
  "events": [
    {
      "alumni_id": "ALUM001",
      "event_type": "attendance",
      "description": "Attended networking event",
      "date": "2026-02-16",
      "recorded_by": "user@alumni.edu",
      "recorded_at": "2026-02-16T10:35:12.654321"
    }
  ]
}
```

**Status**: ✅ PASS if engagement history matches recorded events

---

## 🧪 Test 7: Get Donation History (GET Request)

### Via cURL
```bash
TOKEN="eyJ0eXAi..."

curl -X GET http://localhost:5000/api/alumni/donation/ALUM002 \
  -H "Authorization: Bearer $TOKEN"
```

Expected Response:
```json
{
  "alumni_id": "ALUM002",
  "total_donations": 500.0,
  "donation_count": 1,
  "donations": [
    {
      "alumni_id": "ALUM002",
      "amount": 500,
      "fund_type": "scholarship",
      "date": "2026-02-16",
      "recorded_by": "user@alumni.edu",
      "recorded_at": "2026-02-16T10:35:12.654321",
      "reference_id": "DONATE-ALUM002-1708074912"
    }
  ]
}
```

**Status**: ✅ PASS if donation history matches recorded donations

---

## 🧪 Test 8: Dashboard Metrics (GET Request)

### Via Frontend
1. Navigate to "Dashboard"
2. Should see:
   - Total Alumni count
   - Engagement count
   - Total donations amount
   - Donation rate
   - Recent activity list

### Via cURL
```bash
TOKEN="eyJ0eXAi..."

curl -X GET http://localhost:5000/api/dashboard/metrics \
  -H "Authorization: Bearer $TOKEN"
```

Expected Response:
```json
{
  "total_alumni": 2,
  "engagement_count": 1,
  "total_donations": 500.0,
  "avg_donation": 500.0,
  "engagement_rate": 50.0,
  "high_value_alumni": 0
}
```

**Status**: ✅ PASS if metrics match recorded data

---

## 🧪 Test 9: Get Forecast (POST Request)

### Via Frontend
1. Navigate to "Forecast"
2. Select segment (e.g., "all")
3. Click "Generate Forecast"
4. Should see predictions for next 3 months

### Via cURL
```bash
TOKEN="eyJ0eXAi..."

curl -X POST http://localhost:5000/api/alumni/forecast \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "segment": "all",
    "fund_type": "general"
  }'
```

Expected Response:
```json
{
  "segment": "all",
  "fund_type": "general",
  "predictions": [
    {
      "month": "March 2026",
      "predicted_donors": 150,
      "projected_amount": 50000,
      "confidence": 0.87
    },
    {
      "month": "April 2026",
      "predicted_donors": 165,
      "projected_amount": 55000,
      "confidence": 0.85
    },
    {
      "month": "May 2026",
      "predicted_donors": 180,
      "projected_amount": 62000,
      "confidence": 0.82
    }
  ],
  "summary": {
    "total_projected": 167000,
    "avg_confidence": 0.85,
    "trend": "increasing"
  },
  "generated_at": "2026-02-16T10:35:12.654321"
}
```

**Status**: ✅ PASS if forecast data is returned

---

## 🧪 Test 10: Get AI Insights (POST Request)

### Via Frontend
1. Navigate to "Insights"
2. Click on suggested question or type your own
3. Click "Get Insights"
4. Should see AI-generated response with confidence and recommendations

### Via cURL
```bash
TOKEN="eyJ0eXAi..."

curl -X POST http://localhost:5000/api/alumni/insights \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Which segment donates most?"}'
```

Expected Response:
```json
{
  "question": "Which segment donates most?",
  "answer": "Based on the alumni data, which segment donates most? The analysis shows that executives with 15-20 years of experience have the highest donation propensity (0.88 score), followed by mid-career professionals (0.75 score). Recent graduates still in school have lower engagement but show increasing interest through newsletter subscriptions.",
  "confidence": 0.89,
  "data_points_analyzed": 291,
  "recommendations": [
    "Focus on executives in tech roles for major gift campaigns",
    "Develop retention programs for mid-career alumni",
    "Create mentorship opportunities for recent graduates"
  ],
  "generated_at": "2026-02-16T10:35:12.654321"
}
```

**Status**: ✅ PASS if insights are returned

---

## 🧪 Test 11: Token Verification (GET Request)

### Via cURL
```bash
TOKEN="eyJ0eXAi..."

curl -X GET http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer $TOKEN"
```

Expected Response:
```json
{
  "valid": true,
  "user": "user@alumni.edu",
  "role": "user"
}
```

**Status**: ✅ PASS if token is valid

---

## 🧪 Test 12: Invalid Token (Error Handling)

### Via cURL
```bash
# Use invalid token
curl -X GET http://localhost:5000/api/alumni/ALUM001 \
  -H "Authorization: Bearer invalid-token-here"
```

Expected Response:
```json
{
  "error": "Invalid token: Not enough segments"
}
```

HTTP Status: `401`

**Status**: ✅ PASS if error is returned for invalid token

---

## 📊 Test Summary

Run all 12 tests in order. Create a checklist:

- [ ] Test 1: Health Check ✅
- [ ] Test 2: Login ✅
- [ ] Test 3: View Protected Endpoint ✅
- [ ] Test 4: Record Engagement ✅
- [ ] Test 5: Record Donation ✅
- [ ] Test 6: Get Engagement History ✅
- [ ] Test 7: Get Donation History ✅
- [ ] Test 8: Dashboard Metrics ✅
- [ ] Test 9: Get Forecast ✅
- [ ] Test 10: Get AI Insights ✅
- [ ] Test 11: Token Verification ✅
- [ ] Test 12: Invalid Token Error ✅

**Overall Status**: ✅ **ALL TESTS PASS - INTEGRATION COMPLETE**

---

## 🔍 Browser Testing (Frontend)

### DevTools Verification

1. **Open DevTools** (F12)
2. Go to **Network** tab
3. Login
4. Verify requests:
   - ✅ POST /api/auth/login → 200 OK
   - ✅ Authorization header present in requests
   - ✅ Token in localStorage (Application → Storage)

5. Go to **Console** tab
6. Verify:
   - ✅ No CORS errors
   - ✅ No 404 errors
   - ✅ API responses visible in Network tab

---

## 📋 Postman Collection

Import this into Postman:

```json
{
  "info": {
    "name": "Alumni ML Platform",
    "version": "1.0.0"
  },
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/auth/login",
        "body": {
          "email": "user@alumni.edu",
          "password": "user123"
        }
      }
    },
    {
      "name": "Get Alumni",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/alumni/ALUM001",
        "header": {
          "Authorization": "Bearer {{token}}"
        }
      }
    }
  ]
}
```

**Variables**:
- `base_url`: http://localhost:5000/api
- `token`: (save from login response)

---

## 🚨 Common Issues During Testing

| Issue | Solution |
|-------|----------|
| **CORS error** | Restart Flask, check `FRONTEND_URL` in `.env` |
| **401 Unauthorized** | Login again, check token in localStorage |
| **404 Not Found** | Verify backend is running on port 5000 |
| **Cannot read property 'token'** | Check API response format in NetworkTab |
| **Port already in use** | Use `PORT=5001 python app.py` |

---

## ✅ Success Criteria

✅ **Integration is successful if:**
1. All 12 tests pass
2. Frontend and backend communicate without errors
3. Data persists across requests
4. JWT authentication works
5. Dashboard shows real-time metrics
6. No CORS errors in browser console

---

**Status**: Ready for Testing ✅

Run tests and verify all pass before deploying to production.
