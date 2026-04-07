# Setup Guide

## Prerequisites

### Required Software
- **Python**: 3.8 or higher
- **Node.js**: 20.x or higher
- **npm**: 10.x or higher
- **Git**: Latest version

### Required Accounts
- **Alibaba Cloud Account** with access to:
  - DashScope API (for Qwen models and ASR)
  - OSS (Object Storage Service)

---

## Initial Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd pic-talk
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

Or use a virtual environment (recommended):
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Environment Variables
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your credentials:
```env
# DashScope API Configuration
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# OSS Configuration
OSS_ACCESS_KEY_ID=your_oss_access_key_id
OSS_ACCESS_KEY_SECRET=your_oss_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# Database Configuration (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./pic_talk.db

# Application Configuration
ENVIRONMENT=development
DEBUG=true
```

#### Initialize Database
```bash
python -c "from db.init_db import init_database; init_database()"
```

Or run the initialization script if available:
```bash
python db/init_db.py
```

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend
npm install
```

#### Configure Frontend (if needed)
Create `.env.local` for frontend environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running the Application

### Development Mode

#### Start Backend Server
```bash
cd backend
uvicorn main:app --reload
```

The backend will be available at: `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

#### Start Frontend Development Server
```bash
cd frontend
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### Production Mode

#### Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
npm start
```

---

## Verification

### Test Backend
1. Visit `http://localhost:8000` - should return `{"status": "ok"}`
2. Visit `http://localhost:8000/docs` - should show API documentation
3. Test task generation:
```bash
curl http://localhost:8000/api/image/generate
```

### Test Frontend
1. Visit `http://localhost:3000`
2. Should see the application interface
3. Check browser console for any errors

---

## Common Issues

### Backend Issues

#### Import Errors
**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: 
```bash
pip install -r requirements.txt
```

#### Database Errors
**Problem**: `sqlite3.OperationalError: no such table`

**Solution**: Initialize the database:
```bash
python db/init_db.py
```

#### API Key Errors
**Problem**: `Authentication failed` or `Invalid API key`

**Solution**: 
- Verify your DashScope API key in `.env`
- Ensure the key has proper permissions
- Check if the key is active in Alibaba Cloud console

#### OSS Upload Errors
**Problem**: `Access denied` or `Bucket not found`

**Solution**:
- Verify OSS credentials in `.env`
- Check bucket name and endpoint
- Ensure bucket has proper permissions

### Frontend Issues

#### Port Already in Use
**Problem**: `Port 3000 is already in use`

**Solution**:
```bash
# Use a different port
PORT=3001 npm run dev
```

#### CORS Errors
**Problem**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
- Ensure backend is running
- Check CORS configuration in `backend/main.py`
- Verify frontend URL matches allowed origins

#### Build Errors
**Problem**: TypeScript or build errors

**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit Python files
   - Server auto-reloads with `--reload` flag
   - Test endpoints via Swagger UI or curl

2. **Frontend Changes**:
   - Edit React/TypeScript files
   - Hot reload is automatic
   - Check browser console for errors

### Adding Dependencies

**Backend**:
```bash
pip install <package-name>
pip freeze > requirements.txt
```

**Frontend**:
```bash
npm install <package-name>
```

### Database Migrations

Currently using SQLite with simple schema. For schema changes:
1. Update table definitions in `db/` folder
2. Drop and recreate database (development only):
```bash
rm pic_talk.db
python db/init_db.py
```

For production, implement proper migrations using Alembic.

---

## Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

Or run specific test file:
```bash
python test.py
```

### Frontend Tests
```bash
cd frontend
npm run test
```

---

## Deployment Considerations

### Environment Variables
- Never commit `.env` files
- Use environment-specific configurations
- Set `ENVIRONMENT=production` in production

### Database
- Migrate from SQLite to PostgreSQL for production
- Set up proper backup strategy
- Use connection pooling

### Security
- Enable HTTPS
- Restrict CORS to production domains
- Implement rate limiting
- Add authentication/authorization
- Secure API keys using secrets management

### Performance
- Enable caching for API responses
- Optimize image sizes
- Use CDN for static assets
- Monitor API usage and costs

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Alibaba Cloud DashScope](https://dashscope.aliyun.com/)
- [Alibaba Cloud OSS](https://www.alibabacloud.com/product/oss)

---

## Getting Help

If you encounter issues:
1. Check this guide's Common Issues section
2. Review error messages carefully
3. Check application logs
4. Verify all environment variables are set correctly
5. Ensure all services (DashScope, OSS) are accessible
