# Authentication Setup Guide

## 🎯 **Local Development Authentication**

I've set up a **local Cognito mock** for development that simulates AWS Cognito behavior without requiring AWS services.

## 🔧 **What's Implemented**

### **1. Local Cognito Mock (`auth/local_cognito.py`)**
- JWT token generation and validation
- User management with roles/groups
- Password authentication (accepts any password for dev users)
- Mock user database with default users

### **2. Authentication Middleware (`auth/__init__.py`)**
- JWT token extraction from Authorization header
- User authentication dependencies
- Role-based access control (RBAC)
- Optional authentication for public endpoints

### **3. Authentication Endpoints (`auth/routes.py`)**
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/users` - Create new user (admin only)
- `GET /api/v1/auth/users` - List all users (admin only)
- `GET /api/v1/auth/dev-users` - Get dev users for testing

## 👥 **Default Development Users**

| Username | Email | Password | Groups |
|----------|-------|----------|--------|
| admin | admin@aquifer.local | any | admin, user |
| user | user@aquifer.local | any | user |
| analyst | analyst@aquifer.local | any | analyst, user |

## 🚀 **How to Use**

### **1. Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "any"}'
```

### **2. Use Token for Protected Endpoints**
```bash
TOKEN="your_jwt_token_here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

### **3. Test Different User Roles**
```bash
# Login as analyst
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst", "password": "any"}'
```

## 🔒 **Role-Based Access Control**

### **Available Roles:**
- **admin**: Full access to all endpoints
- **analyst**: Access to analysis and data endpoints
- **user**: Basic user access

### **Usage in Endpoints:**
```python
from auth import require_admin, require_analyst, require_user

@app.get("/admin-only")
async def admin_endpoint(current_user = Depends(require_admin)):
    return {"message": "Admin only"}

@app.get("/analyst-endpoint") 
async def analyst_endpoint(current_user = Depends(require_analyst)):
    return {"message": "Analyst access"}
```

## 🔄 **Migration to AWS Cognito**

When ready for production, you can easily switch to real AWS Cognito:

### **1. Update Environment Variables**
```bash
export AWS_COGNITO_USER_POOL_ID="your-pool-id"
export AWS_COGNITO_CLIENT_ID="your-client-id"
export AWS_REGION="your-region"
```

### **2. Replace Mock with Real Cognito**
- Replace `local_cognito.py` with AWS Cognito SDK calls
- Update JWT validation to use Cognito's public keys
- Keep the same API interface

### **3. Benefits of This Approach**
- ✅ **Same API** for local and production
- ✅ **Easy testing** with mock users
- ✅ **No AWS costs** during development
- ✅ **Offline development** capability
- ✅ **Consistent behavior** across environments

## 📝 **Next Steps**

1. **Protect your API endpoints** by adding authentication dependencies
2. **Test different user roles** with the provided dev users
3. **Add user management** features as needed
4. **Plan AWS Cognito migration** for production

## 🛠 **Development Commands**

```bash
# Start server
cd backend && ./venv/bin/python main.py

# Test authentication
curl http://localhost:8000/api/v1/auth/dev-users

# Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "any"}'
```

This setup gives you **production-ready authentication** for local development while maintaining **easy migration** to AWS Cognito when needed!
