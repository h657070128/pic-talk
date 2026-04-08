# Pricing Page & User Management Implementation Plan

> **Project:** pic-talk — AI-Powered English Speaking Practice Platform
> **Date:** 2026-04-08
> **Status:** Draft

---

## Table of Contents

1. [Background & Current State](#1-background--current-state)
2. [Feature Goals](#2-feature-goals)
3. [Subscription Tier Design](#3-subscription-tier-design)
4. [Backend Implementation Plan](#4-backend-implementation-plan)
   - 4.1 [Database Schema Changes](#41-database-schema-changes)
   - 4.2 [Authentication System](#42-authentication-system)
   - 4.3 [Subscription & Payment APIs](#43-subscription--payment-apis)
   - 4.4 [Access Control Middleware](#44-access-control-middleware)
   - 4.5 [New Dependencies](#45-new-dependencies)
5. [Frontend Implementation Plan](#5-frontend-implementation-plan)
   - 5.1 [New Pages & Routing](#51-new-pages--routing)
   - 5.2 [Pricing Page Design](#52-pricing-page-design)
   - 5.3 [Auth Pages & Flow](#53-auth-pages--flow)
   - 5.4 [User Dashboard](#54-user-dashboard)
   - 5.5 [Global State & Auth Context](#55-global-state--auth-context)
   - 5.6 [New Dependencies](#56-new-dependencies)
6. [API Endpoint Reference](#6-api-endpoint-reference)
7. [Payment Integration](#7-payment-integration)
8. [Migration Strategy](#8-migration-strategy)
9. [Implementation Phases](#9-implementation-phases)
10. [Security Considerations](#10-security-considerations)
11. [Open Questions](#11-open-questions)

---

## 1. Background & Current State

**pic-talk** is an AI-powered English speaking practice platform. Users view AI-generated images and practice describing them in English. The system uses Alibaba Cloud services (Qwen for text/image generation, DashScope ASR for speech recognition, OSS for storage) with a **FastAPI** backend (Python, MySQL, SQLAlchemy) and a **Next.js 16** frontend (React 19, TypeScript, Tailwind CSS 4).

### What exists today

| Area | Status |
|---|---|
| Image task generation & random retrieval | Done |
| Audio recording, ASR transcription, AI evaluation | Done |
| Database: `image_practice_task`, `user_practice_record` tables | Done |
| User authentication / registration / login | **Not implemented** |
| User table | **Not implemented** |
| Subscription / payment | **Not implemented** |
| Frontend routing (multi-page) | **Not implemented** — single `page.tsx` only |

Key observation: the `user_practice_record` table already has a `user_id: BigInteger (nullable)` column, so the data model was designed with future user tracking in mind.

---

## 2. Feature Goals

1. **User Management** — Registration, login, profile; track every user and link their practice records.
2. **Subscription System** — Three paid tiers with time-based billing; free tier with limited daily usage.
3. **Pricing Page** — A public-facing page showing subscription plans, benefits, and a checkout flow.
4. **Access Control** — Enforce subscription limits on core features (task generation, practice evaluation).

---

## 3. Subscription Tier Design

### 3.1 Plans

| Plan | Price | Period | Price/Month Equivalent |
|---|---|---|---|
| Monthly | **CNY 6** | 1 month | CNY 6 |
| Quarterly | **CNY 12** | 3 months | CNY 4 |
| Yearly | **CNY 39** | 12 months | CNY 3.25 |

### 3.2 Feature Matrix

| Feature | Free (unsubscribed) | Subscribed (any tier) |
|---|---|---|
| View / practice existing tasks | 3 times/day | Unlimited |
| Generate new AI tasks | Not available | Unlimited |
| View practice history | Last 3 records | Full history |
| AI evaluation feedback | Basic (summary only) | Full (scores + detailed feedback) |
| Difficulty selection | Beginner only | All levels |

> The exact quotas above are suggestions; they can be tuned before launch.

### 3.3 Data Representation

Each plan is stored in a `subscription_plan` reference table. A user's active subscription is stored in `user_subscription` with start/end timestamps so the system can determine if a subscription is currently active.

---

## 4. Backend Implementation Plan

### 4.1 Database Schema Changes

#### New Table: `user`

```sql
CREATE TABLE `user` (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    nickname        VARCHAR(64)  DEFAULT NULL,
    avatar_url      VARCHAR(512) DEFAULT NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

SQLAlchemy model (`backend/db/user.py`):

```python
class User(Base):
    __tablename__ = "user"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    email       = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname    = Column(String(64), nullable=True)
    avatar_url  = Column(String(512), nullable=True)
    is_active   = Column(Boolean, nullable=False, default=True)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

#### New Table: `subscription_plan`

A reference/config table storing plan metadata. Seeded on deployment.

```sql
CREATE TABLE subscription_plan (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(32)  NOT NULL UNIQUE,   -- 'monthly', 'quarterly', 'yearly'
    display_name    VARCHAR(64)  NOT NULL,           -- '月度会员', '季度会员', '年度会员'
    price_cents     INT          NOT NULL,           -- price in CNY fen (分): 600, 1200, 3900
    duration_days   INT          NOT NULL,           -- 30, 90, 365
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Seed data:

| name | display_name | price_cents | duration_days |
|---|---|---|---|
| monthly | 月度会员 | 600 | 30 |
| quarterly | 季度会员 | 1200 | 90 |
| yearly | 年度会员 | 3900 | 365 |

SQLAlchemy model (`backend/db/subscription_plan.py`):

```python
class SubscriptionPlan(Base):
    __tablename__ = "subscription_plan"

    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    name          = Column(String(32), nullable=False, unique=True)
    display_name  = Column(String(64), nullable=False)
    price_cents   = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    is_active     = Column(Boolean, nullable=False, default=True)
    created_at    = Column(DateTime, server_default=func.now())
```

#### New Table: `user_subscription`

Tracks each subscription purchase/period for a user.

```sql
CREATE TABLE user_subscription (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT       NOT NULL,
    plan_id         BIGINT       NOT NULL,
    status          VARCHAR(32)  NOT NULL DEFAULT 'active',  -- 'active', 'expired', 'cancelled'
    start_date      DATETIME     NOT NULL,
    end_date        DATETIME     NOT NULL,
    payment_id      VARCHAR(128) DEFAULT NULL,               -- external payment reference
    amount_paid     INT          NOT NULL,                   -- actual amount paid in fen
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES `user`(id),
    FOREIGN KEY (plan_id) REFERENCES subscription_plan(id),
    INDEX idx_user_status (user_id, status)
);
```

SQLAlchemy model (`backend/db/user_subscription.py`):

```python
class UserSubscription(Base):
    __tablename__ = "user_subscription"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id     = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    plan_id     = Column(BigInteger, ForeignKey("subscription_plan.id"), nullable=False)
    status      = Column(String(32), nullable=False, default="active")
    start_date  = Column(DateTime, nullable=False)
    end_date    = Column(DateTime, nullable=False)
    payment_id  = Column(String(128), nullable=True)
    amount_paid = Column(Integer, nullable=False)
    created_at  = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlan")
```

#### New Table: `payment_record`

Immutable log of all payment transactions.

```sql
CREATE TABLE payment_record (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id             BIGINT       NOT NULL,
    subscription_id     BIGINT       DEFAULT NULL,
    payment_provider    VARCHAR(32)  NOT NULL,        -- 'wechat', 'alipay'
    provider_order_id   VARCHAR(128) DEFAULT NULL,    -- ID from payment provider
    amount_cents        INT          NOT NULL,
    status              VARCHAR(32)  NOT NULL DEFAULT 'pending',  -- 'pending', 'success', 'failed', 'refunded'
    paid_at             DATETIME     DEFAULT NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES `user`(id),
    FOREIGN KEY (subscription_id) REFERENCES user_subscription(id)
);
```

#### Existing Table Changes

**`user_practice_record`** — no schema change needed. The existing `user_id` column (nullable BigInteger) will now be populated with actual user IDs from the new `user` table. A foreign key constraint can optionally be added:

```sql
ALTER TABLE user_practice_record
    ADD CONSTRAINT fk_practice_user FOREIGN KEY (user_id) REFERENCES `user`(id);
```

### 4.2 Authentication System

Use **JWT (JSON Web Tokens)** for stateless authentication, consistent with the existing FastAPI ecosystem.

#### New Files

| File | Purpose |
|---|---|
| `backend/api/auth_controller.py` | Registration & login endpoints |
| `backend/api/user_controller.py` | User profile endpoints |
| `backend/services/auth_service.py` | Password hashing, JWT creation/verification |
| `backend/services/user_service.py` | User CRUD operations |
| `backend/services/user_repository.py` | User DB queries |
| `backend/middleware/auth_middleware.py` | JWT verification dependency |

#### Authentication Flow

```
Registration:
  POST /api/auth/register  { email, password, nickname? }
      → validate email uniqueness
      → hash password (bcrypt)
      → insert into `user` table
      → return JWT access_token + refresh_token

Login:
  POST /api/auth/login  { email, password }
      → verify credentials
      → return JWT access_token + refresh_token

Token Refresh:
  POST /api/auth/refresh  { refresh_token }
      → verify refresh_token
      → return new access_token

Protected Requests:
  Authorization: Bearer <access_token>
      → FastAPI Depends(get_current_user) extracts user from token
```

#### JWT Structure

```python
# Access token payload
{
    "sub": user_id,       # subject
    "email": "...",
    "exp": ...,           # expiry — 30 minutes
    "type": "access"
}

# Refresh token payload
{
    "sub": user_id,
    "exp": ...,           # expiry — 7 days
    "type": "refresh"
}
```

#### Auth Dependency

```python
# backend/middleware/auth_middleware.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Decode JWT and return user info. Raises 401 if invalid."""
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> dict | None:
    """Same as above but returns None for unauthenticated requests (public endpoints)."""
    if not credentials:
        return None
    return get_current_user(credentials)
```

### 4.3 Subscription & Payment APIs

#### New Files

| File | Purpose |
|---|---|
| `backend/api/subscription_controller.py` | Subscription & payment endpoints |
| `backend/services/subscription_service.py` | Subscription business logic |
| `backend/services/subscription_repository.py` | Subscription DB queries |
| `backend/services/payment_service.py` | Payment provider integration |

#### Subscription Service Logic

```python
# backend/services/subscription_service.py

class SubscriptionService:

    def get_plans(self) -> list[dict]:
        """Return all active subscription plans."""

    def get_user_subscription(self, user_id: int) -> dict | None:
        """Return user's current active subscription, or None."""

    def is_user_subscribed(self, user_id: int) -> bool:
        """Check if user has an active (non-expired) subscription."""

    def create_subscription(self, user_id: int, plan_id: int, payment_id: str) -> dict:
        """
        Called after successful payment.
        - If user has an existing active subscription, extend end_date.
        - Otherwise create a new subscription record.
        """

    def expire_subscriptions(self):
        """Batch job: mark subscriptions past end_date as 'expired'."""
```

### 4.4 Access Control Middleware

A FastAPI dependency that checks the current user's subscription status and enforces quotas for free-tier users.

```python
# backend/middleware/subscription_guard.py

from fastapi import Depends, HTTPException
from middleware.auth_middleware import get_current_user
from services.subscription_service import SubscriptionService

def require_subscription(user: dict = Depends(get_current_user)):
    """Raise 403 if user does not have an active subscription."""
    svc = SubscriptionService()
    if not svc.is_user_subscribed(user["sub"]):
        raise HTTPException(status_code=403, detail="Active subscription required")
    return user

def check_daily_quota(user: dict = Depends(get_current_user)):
    """
    For free-tier users: check if daily practice count < 3.
    Subscribed users pass through unconditionally.
    """
    svc = SubscriptionService()
    if svc.is_user_subscribed(user["sub"]):
        return user

    # Count today's practice records for this user
    today_count = get_today_practice_count(user["sub"])
    if today_count >= 3:
        raise HTTPException(
            status_code=429,
            detail="Daily free limit reached. Subscribe to continue."
        )
    return user
```

#### Applying Guards to Existing Endpoints

| Endpoint | Current Auth | New Auth |
|---|---|---|
| `GET /api/image/generate` | None | `require_subscription` |
| `GET /api/image/get_random_task` | None | `check_daily_quota` |
| `POST /api/user-practice/evaluate` | None | `check_daily_quota` |
| `GET /api/auth/*` | — | Public |
| `GET /api/subscription/plans` | — | Public |
| `POST /api/subscription/create-order` | — | `get_current_user` |

### 4.5 New Dependencies

Add to `backend/requirements.txt`:

```
PyJWT>=2.8.0           # JWT encoding/decoding
bcrypt>=4.0.0          # Password hashing
```

### 4.6 New Environment Variables

Add to `backend/.env.example`:

```env
# JWT
JWT_SECRET_KEY=
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Payment (WeChat Pay example)
WECHAT_PAY_APP_ID=
WECHAT_PAY_MCH_ID=
WECHAT_PAY_API_KEY=
WECHAT_PAY_NOTIFY_URL=
```

---

## 5. Frontend Implementation Plan

### 5.1 New Pages & Routing

Leverage Next.js App Router. New directory structure under `frontend/app/`:

```
frontend/app/
├── layout.tsx                    # Update: add Navbar, AuthProvider
├── page.tsx                      # Home / Practice page (existing, update to require auth)
├── pricing/
│   └── page.tsx                  # Pricing page (public)
├── login/
│   └── page.tsx                  # Login page
├── register/
│   └── page.tsx                  # Registration page
├── dashboard/
│   └── page.tsx                  # User dashboard (subscription status, practice history)
├── payment/
│   ├── page.tsx                  # Payment processing page
│   └── callback/
│       └── page.tsx              # Payment result callback
└── components/
    ├── Navbar.tsx                # Global navigation bar
    ├── AuthProvider.tsx          # React context for auth state
    ├── PricingCard.tsx           # Reusable pricing tier card
    ├── ProtectedRoute.tsx        # HOC/wrapper that redirects unauthenticated users
    └── SubscriptionBadge.tsx     # Shows current subscription status
```

### 5.2 Pricing Page Design

**Route:** `/pricing` (public — no auth required)

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Navbar  [ Home | Pricing | Login / Dashboard ]                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│              选择适合你的学习计划                                   │
│         Choose the plan that fits your learning journey          │
│                                                                 │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   月度会员    │  │    季度会员      │  │    年度会员       │     │
│  │   Monthly    │  │   Quarterly     │  │    Yearly        │     │
│  │             │  │   ★ POPULAR     │  │   ★ BEST VALUE   │     │
│  │   ¥6/月     │  │   ¥12/季        │  │   ¥39/年         │     │
│  │   ¥6/mo     │  │   ¥4/mo         │  │   ¥3.25/mo       │     │
│  │             │  │                 │  │                   │     │
│  │ ✓ Unlimited │  │ ✓ Unlimited     │  │ ✓ Unlimited      │     │
│  │   practice  │  │   practice      │  │   practice       │     │
│  │ ✓ All       │  │ ✓ All           │  │ ✓ All            │     │
│  │   levels    │  │   levels        │  │   levels         │     │
│  │ ✓ Full AI   │  │ ✓ Full AI       │  │ ✓ Full AI        │     │
│  │   feedback  │  │   feedback      │  │   feedback       │     │
│  │ ✓ Generate  │  │ ✓ Generate      │  │ ✓ Generate       │     │
│  │   tasks     │  │   tasks         │  │   tasks          │     │
│  │ ✓ Full      │  │ ✓ Full          │  │ ✓ Full           │     │
│  │   history   │  │   history       │  │   history        │     │
│  │             │  │                 │  │                   │     │
│  │ [ 立即订阅 ] │  │ [ 立即订阅 ]    │  │ [ 立即订阅 ]      │     │
│  │ [ Subscribe]│  │ [ Subscribe ]   │  │ [ Subscribe ]     │     │
│  └─────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  免费用户 Free Tier                                      │    │
│  │  • 每日 3 次练习  3 practices/day                         │    │
│  │  • 仅初级难度    Beginner only                           │    │
│  │  • 基础反馈      Basic feedback                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  FAQ / 常见问题                                                  │
│  ─────────────                                                  │
│  Q: 可以随时取消吗？                                              │
│  A: 订阅期内均可使用，到期后自动停止，无自动续费。                     │
│                                                                 │
│  Q: 支持哪些支付方式？                                            │
│  A: 微信支付、支付宝。                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### PricingCard Component

```tsx
// frontend/app/components/PricingCard.tsx

interface PricingCardProps {
  planName: string;         // "monthly" | "quarterly" | "yearly"
  displayName: string;      // "月度会员"
  price: number;            // 6, 12, 39
  period: string;           // "月", "季", "年"
  perMonth: string;         // "¥6/月", "¥4/月", "¥3.25/月"
  badge?: string;           // "热门", "最划算"
  features: string[];
  onSubscribe: () => void;
  isCurrentPlan?: boolean;
}
```

### 5.3 Auth Pages & Flow

#### Login Page (`/login`)

- Email + password form
- "记住我" checkbox (persist refresh token)
- Link to `/register`
- Link to password reset (future)
- On success: store tokens, redirect to previous page or `/`

#### Register Page (`/register`)

- Email + password + confirm password + optional nickname
- On success: auto-login, redirect to `/`
- Link to `/login`

### 5.4 User Dashboard

**Route:** `/dashboard` (requires auth)

Content:
- **Subscription status** — current plan, expiry date, or "Free Tier"
- **Quick subscribe** button if unsubscribed
- **Practice history** — paginated list of past practice records with scores
- **Account settings** — change nickname, avatar (future: change password)

### 5.5 Global State & Auth Context

```tsx
// frontend/app/components/AuthProvider.tsx

interface AuthState {
  user: { id: number; email: string; nickname?: string } | null;
  subscription: { plan: string; endDate: string } | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, nickname?: string) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
}
```

Token storage strategy:
- **Access token**: in-memory (React state) — short-lived (30 min)
- **Refresh token**: `httpOnly` cookie preferred; fallback to `localStorage` for MVP simplicity

### 5.6 New Dependencies

```bash
npm install js-cookie        # Cookie management for tokens (if using cookie approach)
```

No external state management library needed — React Context + `useState`/`useEffect` is sufficient for this scale.

---

## 6. API Endpoint Reference

### Auth Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | Public | Register new user |
| `POST` | `/api/auth/login` | Public | Login, return tokens |
| `POST` | `/api/auth/refresh` | Public (with refresh token) | Refresh access token |
| `GET` | `/api/auth/me` | Bearer | Get current user profile |

#### `POST /api/auth/register`

```json
// Request
{ "email": "user@example.com", "password": "securepass", "nickname": "Tom" }

// Response 201
{
  "user": { "id": 1, "email": "user@example.com", "nickname": "Tom" },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

#### `POST /api/auth/login`

```json
// Request
{ "email": "user@example.com", "password": "securepass" }

// Response 200
{
  "user": { "id": 1, "email": "user@example.com", "nickname": "Tom" },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

#### `GET /api/auth/me`

```json
// Response 200
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "Tom",
  "subscription": {
    "plan_name": "quarterly",
    "display_name": "季度会员",
    "status": "active",
    "end_date": "2026-07-08T00:00:00"
  }
}
```

### Subscription Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/subscription/plans` | Public | List all active plans |
| `GET` | `/api/subscription/my` | Bearer | Get user's current subscription |
| `POST` | `/api/subscription/create-order` | Bearer | Initiate a payment order |
| `POST` | `/api/subscription/payment-callback` | Webhook (provider signature) | Payment provider async notification |

#### `GET /api/subscription/plans`

```json
// Response 200
{
  "plans": [
    {
      "id": 1,
      "name": "monthly",
      "display_name": "月度会员",
      "price_cents": 600,
      "duration_days": 30,
      "price_display": "¥6",
      "per_month_display": "¥6/月"
    },
    {
      "id": 2,
      "name": "quarterly",
      "display_name": "季度会员",
      "price_cents": 1200,
      "duration_days": 90,
      "price_display": "¥12",
      "per_month_display": "¥4/月"
    },
    {
      "id": 3,
      "name": "yearly",
      "display_name": "年度会员",
      "price_cents": 3900,
      "duration_days": 365,
      "price_display": "¥39",
      "per_month_display": "¥3.25/月"
    }
  ]
}
```

#### `POST /api/subscription/create-order`

```json
// Request
{ "plan_id": 2, "payment_method": "wechat" }

// Response 200
{
  "order_id": "ORD202604080001",
  "payment_url": "weixin://wxpay/bizpayurl?...",   // or QR code data
  "qr_code_url": "https://...",                     // QR image URL for display
  "amount_cents": 1200,
  "expires_at": "2026-04-08T11:30:00"
}
```

#### `POST /api/subscription/payment-callback`

Called by the payment provider (WeChat Pay / Alipay) server-to-server. Verifies signature, updates `payment_record` status, activates `user_subscription`.

### User Profile Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `PUT` | `/api/user/profile` | Bearer | Update nickname, avatar |
| `GET` | `/api/user/practice-history` | Bearer | Paginated practice records |

---

## 7. Payment Integration

### Recommended Provider: WeChat Pay (微信支付)

WeChat Pay is the most common payment method for Chinese users. Alipay can be added as a second option.

### Integration Approach

For MVP, use **WeChat Pay Native Payment (Native 支付)** — generates a QR code that the user scans with WeChat to pay. This avoids the complexity of in-app payment SDKs.

### Flow

```
1. User clicks "Subscribe" on pricing page
   ↓
2. Frontend: POST /api/subscription/create-order { plan_id, payment_method }
   ↓
3. Backend:
   a. Create payment_record (status=pending)
   b. Create user_subscription (status=pending)
   c. Call WeChat Pay Unified Order API → get code_url
   d. Return QR code URL to frontend
   ↓
4. Frontend: Display QR code + countdown timer
   ↓
5. User scans QR with WeChat, confirms payment
   ↓
6. WeChat server → POST /api/subscription/payment-callback
   a. Verify signature
   b. Update payment_record (status=success)
   c. Activate user_subscription (status=active, set start_date/end_date)
   ↓
7. Frontend polls GET /api/subscription/my every 3s
   → Detects active subscription → redirects to success page
```

### Alternative: Manual / Test Mode

For development and testing before obtaining WeChat Pay merchant credentials:

- Add a `PAYMENT_MODE=test` env var
- In test mode, `create-order` immediately activates the subscription (no real payment)
- This allows end-to-end testing of the subscription flow

---

## 8. Migration Strategy

Since the project does not use Alembic yet, we have two options:

### Option A: Add Alembic (Recommended)

```bash
pip install alembic
alembic init alembic
# Configure alembic.ini with MySQL connection
# Generate migration: alembic revision --autogenerate -m "add user and subscription tables"
# Apply: alembic upgrade head
```

### Option B: Manual SQL Scripts

Create `backend/db/migrations/` directory with numbered SQL files:

```
backend/db/migrations/
├── 001_create_user_table.sql
├── 002_create_subscription_plan_table.sql
├── 003_create_user_subscription_table.sql
├── 004_create_payment_record_table.sql
├── 005_seed_subscription_plans.sql
└── 006_add_user_fk_to_practice_record.sql
```

**Recommendation:** Go with **Option A (Alembic)** to establish proper migration practices early.

---

## 9. Implementation Phases

### Phase 1: User Management (Backend + Frontend) — ~3-4 days

**Backend:**
- [ ] Create `User` model and migration
- [ ] Implement `auth_service.py` (bcrypt hashing, JWT creation/verification)
- [ ] Implement `user_repository.py` and `user_service.py`
- [ ] Create `auth_controller.py` (register, login, refresh, me)
- [ ] Create `auth_middleware.py` (`get_current_user` dependency)
- [ ] Update `user_practice_controller.py` to require auth and populate `user_id`

**Frontend:**
- [ ] Create `AuthProvider.tsx` context
- [ ] Create `Navbar.tsx` component
- [ ] Build `/login` page
- [ ] Build `/register` page
- [ ] Update `layout.tsx` to include Navbar and AuthProvider
- [ ] Create `ProtectedRoute.tsx` wrapper
- [ ] Update home page to use auth (show login prompt if unauthenticated)

### Phase 2: Subscription System (Backend) — ~2-3 days

- [ ] Create `SubscriptionPlan` and `UserSubscription` models + migrations
- [ ] Seed subscription plans
- [ ] Implement `subscription_service.py` and `subscription_repository.py`
- [ ] Create `subscription_controller.py` (plans, my-subscription, create-order)
- [ ] Implement `subscription_guard.py` middleware
- [ ] Apply access control to existing endpoints
- [ ] Add `payment_record` table and basic `payment_service.py` (test mode)

### Phase 3: Pricing Page (Frontend) — ~2 days

- [ ] Build `PricingCard.tsx` component
- [ ] Build `/pricing` page with three-tier layout
- [ ] Add FAQ section
- [ ] Wire up "Subscribe" buttons to create-order API
- [ ] Build payment QR code display page (`/payment`)
- [ ] Build payment success/failure callback page
- [ ] Add subscription status badge to Navbar

### Phase 4: User Dashboard — ~1-2 days

- [ ] Build `/dashboard` page
- [ ] Show subscription status and expiry
- [ ] Show paginated practice history
- [ ] Add "Renew/Upgrade" subscription button

### Phase 5: Real Payment Integration — ~2-3 days

- [ ] Apply for WeChat Pay merchant account (or Alipay)
- [ ] Implement actual payment provider SDK calls
- [ ] Implement webhook signature verification
- [ ] End-to-end payment testing
- [ ] Add Alipay as secondary payment method (optional)

### Phase 6: Polish & Hardening — ~1-2 days

- [ ] Cron job / scheduled task to expire subscriptions
- [ ] Rate limiting on auth endpoints (prevent brute force)
- [ ] Email verification on registration (optional, future)
- [ ] Error handling and edge case coverage
- [ ] Testing (unit + integration)

**Total estimated effort: ~12-16 days**

---

## 10. Security Considerations

| Area | Approach |
|---|---|
| Password storage | bcrypt with salt (never store plaintext) |
| JWT secret | Strong random key, stored in env variable, never committed |
| Token expiry | Access: 30 min, Refresh: 7 days |
| Payment callbacks | Verify provider signature before processing |
| SQL injection | Parameterized queries via SQLAlchemy ORM |
| CORS | Restrict to known frontend origin |
| Rate limiting | Apply to `/auth/login` and `/auth/register` to prevent brute force |
| Input validation | Pydantic models for all request bodies |
| Sensitive data | Never log passwords, tokens, or payment credentials |
| HTTPS | Required for production (payment providers mandate it) |

---

## 11. Open Questions

1. **Payment provider** — WeChat Pay, Alipay, or both? Need merchant account credentials.
2. **Email verification** — Require email verification on registration, or defer to later?
3. **Auto-renewal** — The current plan assumes no auto-renewal (user re-subscribes manually). Should we add auto-renewal?
4. **Refund policy** — How to handle refund requests? Manual admin process or automated?
5. **Free trial** — Should new users get a free trial period (e.g., 7 days) of the full subscription?
6. **Subscription stacking** — If a user buys a new plan while an existing one is active, extend the end date or replace?
7. **Admin panel** — Do we need an admin dashboard to manage users and subscriptions?
8. **Mobile app** — Will there be a mobile app in the future that needs in-app purchase integration?
