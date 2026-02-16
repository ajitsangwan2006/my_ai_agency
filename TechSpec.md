This is the Technical Design Document for **GlowSync Portfolio & Booking Engine**. 

As CTO, my priority is a system that is boringly reliable, handles race conditions in bookings with ACID compliance, and ensures the artist's portfolio loads instantly on a mobile device over a 4G connection. We are avoiding "hype-train" tech in favor of a stack that has a massive talent pool and proven stability.

---

## 1. Technology Stack Rationale

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14 (App Router) | SSR for SEO-friendly portfolios; React Server Components for fast initial loads. |
| **Backend** | Next.js API Routes (Node.js) | Unified codebase; handles the "BFF" (Backend for Frontend) pattern efficiently. |
| **Language** | TypeScript | Mandatory. We need type safety across the booking logic to prevent runtime errors. |
| **Database** | PostgreSQL (Managed) | Relational integrity is required for scheduling. NoSQL is inappropriate for booking concurrency. |
| **ORM** | Prisma | Type-safe queries and simplified migrations. |
| **Authentication** | NextAuth.js | Secure, session-based auth for the Admin; supports future OAuth (Google/IG) easily. |
| **Image Hosting** | Cloudinary | Automatic transformation/WebP conversion. Essential for the "High-Res Gallery" mobile KPI. |
| **Scheduling Logic** | Date-fns + Luxon | Robust timezone handling. We store everything in UTC and project to the Artist's local time. |
| **Infrastructure** | Vercel + Neon DB | Serverless scale with a "Scale to Zero" cost profile for early-stage cost effectiveness. |

---

## 2. Database Schema (PostgreSQL)

We will use a relational structure to ensure that deleting or archiving a service does not orphan historical booking data.

### Table: `users` (Admin/Artist)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK, Default: gen_random_uuid() | Unique identifier. |
| `email` | String | Unique, Not Null | Admin login. |
| `password_hash`| String | Not Null | Argon2id hash. |
| `business_name`| String | Not Null | Display name for the portfolio. |
| `timezone` | String | Not Null, Default: 'UTC' | Artist's local timezone (e.g., 'America/New_York'). |

### Table: `services`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | |
| `name` | String | Not Null | Service title (e.g., "Bridal Makeup"). |
| `description` | Text | | |
| `price` | Decimal | 10, 2, Not Null | Stored in major units. |
| `currency` | String | Default: 'USD' | |
| `duration_min` | Integer | Not Null, Min: 15 | Duration in minutes. |
| `is_active` | Boolean | Default: true | Soft delete/archive flag. |
| `created_at` | Timestamp| Default: now() | |

### Table: `clients`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | |
| `full_name` | String | Not Null | |
| `email` | String | Not Null | For confirmations. |
| `phone` | String | Not Null | |

### Table: `bookings`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | |
| `client_id` | UUID | FK -> clients.id | |
| `service_id` | UUID | FK -> services.id | |
| `start_time` | Timestamp| Not Null | UTC start time. |
| `end_time` | Timestamp| Not Null | UTC end time (Calculated via service duration). |
| `status` | Enum | 'confirmed', 'cancelled'| |
| `notes` | Text | | Internal admin notes. |

### Table: `blackouts` (Availability Manager)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | |
| `start_time` | Timestamp| Not Null | |
| `end_time` | Timestamp| Not Null | |
| `reason` | String | | e.g., "Doctor Appointment". |
| `is_recurring` | Boolean | Default: false | For "Closed every Monday" logic. |

---

## 3. API Structure (RESTful)

All Admin endpoints require a valid session cookie via NextAuth. Public endpoints are rate-limited to prevent calendar scraping or booking spam.

### 3.1. Public Endpoints (Client-Facing)

*   **`GET /api/v1/services`**
    *   *Description:* Fetch all active services for the menu.
    *   *Security:* Public.
*   **`GET /api/v1/availability?service_id={uuid}&month={YYYY-MM}`**
    *   *Description:* Returns available time slots. 
    *   *Logic:* Computes slots by checking `bookings` and `blackouts` for the requested range.
*   **`POST /api/v1/bookings`**
    *   *Description:* Create a new booking.
    *   *Payload:* `{ service_id, client_name, client_email, client_phone, start_time }`
    *   *Logic:* **Atomic Transaction.** Must verify slot availability again before inserting to prevent double-booking (Race Condition Handling).

### 3.2. Admin Endpoints (Protected)

*   **`GET /api/v1/admin/appointments?start={date}&end={date}`**
    *   *Description:* Fetch list of appointments for the dashboard.
*   **`POST /api/v1/admin/services`**
    *   *Description:* Create a new service.
*   **`PATCH /api/v1/admin/services/:id`**
    *   *Description:* Update or Archive (toggle `is_active`) a service.
*   **`POST /api/v1/admin/blackouts`**
    *   *Description:* Block out dates/times.
*   **`DELETE /api/v1/admin/bookings/:id`**
    *   *Description:* Cancel an appointment and trigger email notification.

---

## 4. Key Logic & Logistics

### 4.1. Concurrency Control
To prevent two clients from booking the same 2:00 PM slot simultaneously, we will use a **PostgreSQL Transaction** with an `ISOLATION LEVEL SERIALIZABLE` or a manual check-and-insert lock:
```sql
-- Pseudo-logic for booking
BEGIN;
  IF EXISTS (SELECT 1 FROM bookings WHERE start_time < :new_end AND end_time > :new_start) 
  OR EXISTS (SELECT 1 FROM blackouts WHERE start_time < :new_end AND end_time > :new_start)
  THEN
    ROLLBACK; -- Slot taken
  ELSE
    INSERT INTO bookings ...;
COMMIT;
```

### 4.2. Timezone Management
*   **Storage:** All timestamps in PostgreSQL are `TIMESTAMP WITH TIME ZONE` (stored in UTC).
*   **API:** API returns ISO-8601 UTC strings.
*   **Frontend:** The client-side calendar uses `Intl.DateTimeFormat` or `Luxon` to display slots in the Artist's configured business timezone, regardless of where the client is browsing from.

### 4.3. Performance & Security
*   **Image Optimization:** Portfolio images will be uploaded to Cloudinary. The frontend will request images with parameters: `q_auto,f_auto,w_800` to ensure small payloads for mobile users.
*   **Input Validation:** All API routes will use **Zod** for schema validation (e.g., ensuring `duration_min` > 15).
*   **Security:** 
    *   CSRF protection via NextAuth.
    *   Rate limiting on `/api/v1/bookings` (max 5 attempts per IP per hour) using Redis or a simple memory cache to prevent bot attacks.
    *   Sensitive data masking: Client phone numbers masked in logs.

### 4.4. Deployment Pipeline
*   **CI/CD:** GitHub Actions running Vitest for unit tests (booking logic) and Playwright for E2E tests (booking flow).
*   **Environment:** 
    *   `Staging`: Mirror of production for testing migrations.
    *   `Production`: Vercel edge network.

This architecture is pragmatic. It prioritizes data integrity and mobile performance while keeping operational costs near zero until the artist starts scaling their volume.