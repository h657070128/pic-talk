# pic-talk

AI-Powered English Speaking Practice Platform. Users view AI-generated images and practice describing them in English, receiving real-time AI feedback.

## Architecture

- **Backend**: FastAPI (Python), MySQL, SQLAlchemy
- **Frontend**: Next.js 16 (React 19, TypeScript, Tailwind CSS 4)
- **AI Services**: Alibaba Cloud (Qwen text/image generation, DashScope ASR)

## Features

- **Image Practice**: View AI-generated images and practice English descriptions
- **Speech Recognition**: Record audio, transcribe via ASR, evaluate with AI
- **User Management**: Registration, login, JWT authentication
- **Subscription System**: Three tiers (Monthly/Quarterly/Yearly) with free tier limits
- **Pricing Page**: Public pricing page with plan comparison
- **User Dashboard**: Practice history, subscription status

## Start Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
python -m db.seed     # Create tables and seed subscription plans
uvicorn main:app --reload
```

## Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Auth
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user profile

### Subscription
- `GET /api/subscription/plans` - List plans (public)
- `GET /api/subscription/my` - Get user's subscription
- `POST /api/subscription/create-order` - Create payment order

### Practice
- `GET /api/image/get_random_task` - Get random practice task
- `GET /api/image/generate` - Generate new AI task (subscription required)
- `POST /api/user-practice/evaluate` - Submit practice for evaluation

### User
- `PUT /api/user/profile` - Update profile
- `GET /api/user/practice-history` - Get practice history

## Environment Variables

See `backend/.env.example` for all required configuration.
