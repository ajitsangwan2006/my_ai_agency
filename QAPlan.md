# GlowSync Portfolio & Booking Engine: Comprehensive Testing Strategy
**To:** Engineering Team, Product Owners, Security Lead
**From:** Director of Quality Assurance
**Status:** MANDATORY IMPLEMENTATION
**Subject:** Quality Standards and Testing Protocol v1.0

I have reviewed the Security Audit and Technical Specifications. Let me be clear: **A bug in production is a failure of our process.** Given the sensitivity of PII and the financial implications of the booking engine, we will not be "moving fast and breaking things." We will move with precision.

This strategy outlines our multi-layered defense. If a test case is missing, the feature is not "Done."

---

## 1. Unit Testing Strategy (The Logic Layer)
*Focus: Isolated business logic, utility functions, and data validation.*

### 1.1. Security & Encryption Utilities
*   **PII Encryption (AES-256-GCM):**
    *   `encryptField()`: Verify that input strings return a formatted ciphertext + IV + Auth Tag.
    *   `decryptField()`: Verify that valid ciphertext returns the original PII.
    *   `encryptionIntegrity`: Ensure that a modified Auth Tag or ciphertext throws a decryption error (preventing tampering).
    *   `kmsMock`: Verify the utility fails gracefully if the KMS (Key Management Service) is unreachable.
*   **Password Hashing:**
    *   `hashPassword()`: Verify Argon2id output format and salt uniqueness.
    *   `verifyPassword()`: Ensure correct rejection of incorrect passwords and acceptance of valid ones.

### 1.2. Validation & Schema (Zod)
*   **Input Sanitization:**
    *   Test that HTML tags are stripped/escaped from `service_description` and `client_notes`.
    *   Verify that `booking_date` only accepts ISO-8601 strings and rejects past dates.
*   **Financial Integrity:**
    *   `validatePrice`: Ensure prices cannot be negative or zero.
    *   Verify that `service_id` and `price` cross-reference logic rejects client-provided prices that don't match the DB record.

### 1.3. Business Logic (The "Brain")
*   **Availability Engine:**
    *   `calculateSlots()`: Test time-zone conversions (e.g., Artist in EST, Client in PST).
    *   `isSlotAvailable()`: Test boundary conditions (e.g., booking exactly at the end of a blackout window).
    *   `bufferTime`: Verify that a 30-minute buffer is correctly applied between two 1-hour appointments.
*   **Ghost Slot Logic:**
    *   Verify that a "Pending" booking expires and becomes "Available" exactly after 15 minutes of inactivity.

---

## 2. Integration Testing Strategy (The Connection Layer)
*Focus: Database interactions, API contracts, and Authentication flows.*

### 2.1. Database & Prisma (The Persistence Layer)
*   **Row Level Security (RLS):**
    *   **Test Case:** Authenticate as `Artist_A`. Attempt to query `bookings` where `user_id = Artist_B`. Verify 0 results or 403 Forbidden.
    *   **Test Case:** Attempt to update a `service` record belonging to another user via the Prisma client. Verify failure.
*   **ACID Compliance & Race Conditions:**
    *   **Concurrency Test:** Simulate 10 simultaneous `POST /api/v1/bookings` requests for the *exact same* time slot.
    *   **Success Criteria:** Exactly 1 request succeeds; 9 requests return a 409 Conflict. No double-bookings.
*   **Audit Logging:**
    *   Verify that every `UPDATE` or `DELETE` on the `bookings` table triggers an entry in the `audit_logs` table with the correct `actor_id`.

### 2.2. Authentication & Authorization (NextAuth)
*   **MFA Flow:**
    *   Verify that a valid password login *without* a TOTP/WebAuthn token results in a "Pending MFA" state, not an authenticated session.
    *   Verify session invalidation after 12 hours.
*   **RBAC (Role-Based Access Control):**
    *   `GET /api/v1/admin/*`: Test with a "Client" session. Verify 403 Forbidden.
    *   `GET /api/v1/admin/*`: Test with an "Unauthenticated" session. Verify 401 Unauthorized.

### 2.3. API & Middleware
*   **Rate Limiting:**
    *   **Public API:** Trigger 21 requests within 60 seconds from one IP. Verify the 21st request receives 429 Too Many Requests.
    *   **Booking Exhaustion:** Trigger 4 booking attempts within 1 hour. Verify block.
*   **Security Headers:**
    *   Verify every response contains `Content-Security-Policy`, `X-Frame-Options: DENY`, and `Strict-Transport-Security`.
*   **Cloudinary Integration:**
    *   Test `POST /api/v1/admin/upload`: Verify that unsigned requests or files > 5MB are rejected by the server-side middleware before hitting Cloudinary.

---

## 3. Edge Case & "Hostile" Testing
*Focus: Anticipating the "unhappy path" and malicious actors.*

| Category | Test Case | Expected Result |
| :--- | :--- | :--- |
| **BOLA** | Change UUID in `PATCH /api/v1/admin/services/:id` to a known ID of another user. | 404 Not Found or 403 Forbidden. |
| **Data Integrity** | Submit a booking with a `service_id` of a "Soft Deleted" (inactive) service. | 400 Bad Request. |
| **Payload Injection** | Submit a booking with a 50KB string in the `client_name` field. | Zod validation error (Max length exceeded). |
| **Time-Travel** | Attempt to book a slot in the past by manipulating the system clock/payload. | 400 Bad Request. |
| **PII Leakage** | Trigger a 500 Internal Server Error. | Verify the error response contains a generic message and NO stack traces or DB queries. |
| **Log Masking** | Inspect Vercel/Cloudwatch logs after a `createClient` action. | Verify `email` and `phone` are masked (e.g., `e***@domain.com`). |

---

## 4. User Acceptance Criteria (UAC)
*Focus: Final verification of the product requirements.*

1.  **Portfolio:** Artist can upload 5 images, reorder them, and they load in < 2s on mobile.
2.  **Booking:** A client can select a service, see only valid slots, and receive a confirmation email within 30s.
3.  **CRM:** Artist can view a client's history, but the phone number is only decrypted on-demand in the UI (not pre-loaded in the bulk list).
4.  **Admin:** Artist can toggle "Vacation Mode," which instantly removes all availability from the public calendar.

---

## 5. Testing Tooling & Infrastructure
*   **Unit/Integration:** `Vitest` with `Prisma Mock` for logic; `Testcontainers` for real PostgreSQL integration tests.
*   **E2E:** `Playwright` for critical path testing (Booking flow, Admin login).
*   **Security:** `OWASP ZAP` for automated vulnerability scanning in CI.
*   **Load:** `k6` to simulate the "IG Influencer Drop" (100 concurrent bookings/sec).

**Final Directive:** No PR shall be merged without 90% code coverage on the `services/` and `lib/crypto` directories. We are the last line of defense for the user's data. **Don't ship bugs.**

**Director of Quality Assurance**
*Trust is a vulnerability. Verification is the cure.*