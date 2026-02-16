# Security Audit & Threat Model: GlowSync Portfolio & Booking Engine
**To:** Project Architect / Stakeholders
**From:** Lead Security Engineer
**Status:** CRITICAL - Action Required
**Subject:** Security Assessment of GlowSync Architecture v1.1

I have reviewed the PRD and Technical Specification. While the choice of a relational database for ACID compliance is a step in the right direction, the current architecture treats security as a "feature" rather than a foundation. In my world, "boringly reliable" is a euphemism for "complacent." 

We are building a system that stores PII (Personally Identifiable Information) and manages business livelihoods. If an attacker dumps the `clients` table or hijacks the Admin session, the brand is dead.

---

## 1. STRIDE Threat Analysis

| Threat | Category | Potential Impact | Mitigation Requirement |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Authentication | Attacker gains access to Admin Dashboard via session hijacking or credential stuffing. | Enforce MFA (TOTP/WebAuthn) and strict JWT/Session hardening. |
| **Tampering** | Data Integrity | Client modifies `price` or `service_id` in the `POST /bookings` request to get a discount. | Server-side price validation; never trust client-side payloads for financial data. |
| **Repudiation** | Non-repudiation | Admin claims they didn't cancel a high-value booking; Client claims they never booked. | Implement immutable audit logs for all state-changing actions. |
| **Info Disclosure** | Confidentiality | `GET /api/v1/availability` leaks specific client names or reasons for blackouts. | Scrub internal metadata from public API responses. |
| **Denial of Service** | Availability | Botnets exhaust the connection pool or lock all calendar slots via "pending" state exhaustion. | Implement strict rate limiting and "Ghost Slot" expiration logic. |
| **Elevation of Privilege** | Authorization | A client uses their session/ID to access `/api/v1/admin` endpoints. | Strict Middleware-level RBAC (Role-Based Access Control) and Row Level Security (RLS). |

---

## 2. Vulnerability Deep Dive & Technical Flaws

### 2.1. PII Exposure in "Client Directory"
The spec mentions a "lightweight CRM." Storing `full_name`, `email`, and `phone` in plain text in a managed cloud DB (Neon) is unacceptable. 
*   **Risk:** If the database is compromised or a backup is leaked, you have a data breach notification event.
*   **Requirement:** Application-level encryption for PII fields.

### 2.2. Broken Object Level Authorization (BOLA)
The `PATCH /api/v1/admin/services/:id` and `DELETE /api/v1/admin/bookings/:id` routes rely on UUIDs. 
*   **Risk:** If the session check only verifies "is logged in" but not "owns this resource," one artist could potentially delete another artist's bookings by guessing or scraping UUIDs (though UUIDs are hard to guess, the logic must be explicit).
*   **Requirement:** Every query must include a `WHERE user_id = current_user_id` clause.

### 2.3. Race Conditions & Locking Logic
The proposed SQL logic for booking is a start, but `SERIALIZABLE` isolation levels in serverless environments (Vercel/Neon) can lead to high retry rates and performance degradation.
*   **Risk:** Under high load (e.g., an IG influencer drop), the "Check then Insert" pattern can still fail if not handled at the database level with proper advisory locks.
*   **Requirement:** Use a Postgres `EXCLUSION` constraint or a specialized locking mechanism to ensure a time-slot cannot overlap for the same `user_id`.

### 2.4. Image Upload Security (Cloudinary)
The spec allows high-res uploads.
*   **Risk:** An attacker could upload a "Polyglot" file (an image that contains an executable script) or trigger a DoS by uploading 10GB files.
*   **Requirement:** Signed uploads only. Restrict file types (MIME-type validation) and file size (max 5MB) at the Edge/Middleware.

---

## 3. Mandatory Security Requirements (The "Hard Line")

### 3.1. Encryption Standards
I am enforcing the following standards. No deviations.
*   **Data in Transit:** TLS 1.3 only. HSTS (HTTP Strict Transport Security) must be enabled with `includeSubDomains` and `preload`.
*   **Data at Rest (PII):** Use **AES-256-GCM** for the `email` and `phone` columns in the `clients` table. The encryption key must be managed via a dedicated KMS (Key Management Service), not stored in `.env`.
*   **Password Hashing:** Argon2id is approved. Parameters: `m=65536 (64MB), t=3, p=4`.
*   **Session Management:** NextAuth cookies must be `HttpOnly`, `Secure`, and `SameSite=Lax`. Session expiry must be set to a maximum of 12 hours for Admin sessions.

### 3.2. Authentication & Authorization
*   **Admin MFA:** Mandatory. Use WebAuthn (Passkeys) or TOTP. Password-only access for a business management tool is a 2010-era mistake.
*   **Rate Limiting:** The proposed "5 attempts per hour" is too simplistic. 
    *   **Public API:** 20 requests/minute per IP.
    *   **Booking POST:** 3 requests/hour per IP (preventing calendar exhaustion).
    *   **Admin Login:** Exponential backoff after 3 failed attempts.

### 3.3. API Security & Headers
The following headers must be present on every response:
*   `Content-Security-Policy (CSP)`: Strict policy. Disallow `unsafe-inline` and restrict `script-src` to self and Cloudinary.
*   `X-Content-Type-Options: nosniff`
*   `X-Frame-Options: DENY`
*   `Permissions-Policy`: Disable camera, microphone, and geolocation unless explicitly required.

---

## 4. Database Hardening (PostgreSQL)

Since we are using Prisma and Neon (Postgres), we must implement **Row Level Security (RLS)**. 
1.  Prisma usually bypasses RLS if using a shadow database or admin user. We must use a restricted database user for the application.
2.  **Audit Log Table:** Create a non-deletable `audit_logs` table.
    *   `id`, `timestamp`, `actor_id`, `action` (CREATE_BOOKING, CANCEL_BOOKING), `ip_address`, `user_agent`.
3.  **Soft Deletes:** Ensure `is_active` logic is enforced at the database view level to prevent accidental data exposure of archived services.

---

## 5. Compliance & Privacy
*   **GDPR/CCPA:** Since we store client names and phones, we need a "Data Deletion" endpoint for clients.
*   **Logs:** Ensure that **no PII** (emails, phone numbers, or passwords) is ever written to Vercel/Cloudwatch logs. Use a masking utility for the `clients` object in your logger.

---

## 6. Implementation Checklist for Architect
- [ ] Implement AES-256-GCM encryption for the `clients` table.
- [ ] Add MFA flow to NextAuth configuration.
- [ ] Define a strict CSP.
- [ ] Move secrets from `.env` to a proper Secret Manager (Vercel Secrets or AWS KMS).
- [ ] Add Zod validation for *all* incoming headers and bodies, specifically checking for injection strings.
- [ ] Set up a Webhook signature verification for Cloudinary/future Stripe integrations.

**Final Note:** If these protocols are not implemented, I will not sign off on the production deployment. We assume the environment is hostile because it is. 

**Lead Security Engineer**
*Trust is a vulnerability.*