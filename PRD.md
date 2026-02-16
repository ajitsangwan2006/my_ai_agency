# Product Requirement Document (PRD): GlowSync Portfolio & Booking Engine

**Version:** 1.1
**Status:** Final Draft
**Product Manager:** Senior PM

---

## 1. Executive Summary & "The Why"
**Problem Statement:**
Professional makeup artists (MUAs) manage their business across disparate platforms (Instagram for discovery, WhatsApp for negotiation, Paper Calendars for tracking). This leads to "admin fatigue," double bookings, and a high drop-off rate for clients who want instant gratification.

**The Solution:**
GlowSync is a unified web-based solution that converts social media followers into confirmed appointments. It combines a high-aesthetic portfolio with a programmatic availability engine, ensuring the artist is "always open" for business without being "always on" her phone.

---

## 2. Success Metrics (KPIs)
*   **Booking Conversion Rate:** % of site visitors who complete a booking.
*   **Admin Time Saved:** Reduction in hours spent manually coordinating schedules per week.
*   **No-Show Rate:** Monitoring the impact of automated email confirmations.
*   **Mobile Performance:** Page Load Time < 2.5s on 4G connections.

---

## 3. Target Personas
1.  **The Artist (Admin):** Focuses on artistry; needs a "set and forget" system for scheduling.
2.  **The High-Intent Client:** Wants to see the artist’s style and secure a specific time slot (e.g., for a wedding or event) immediately.

---

## 4. Feature List & Functional Requirements

### 4.1. Public Portfolio & Service Menu
*   **High-Res Gallery:** A masonry-style grid for work samples.
*   **Service Catalog:** List of offerings with price, duration, and "what's included" text.
*   **Responsive Booking Widget:** A calendar interface that filters out unavailable dates in real-time.

### 4.2. Admin Dashboard
*   **Centralized Schedule:** A dashboard showing upcoming appointments and client details.
*   **Service Builder:** Interface to create/edit/archive services.
*   **Blackout Manager:** Tool to block specific hours, full days, or recurring time off (e.g., "Closed every Monday").
*   **Client Directory:** A lightweight CRM to view booking history per client.

---

## 5. User Stories & Acceptance Criteria

### 5.1. Client Experience

#### **User Story 1: Service Selection**
*As a client, I want to see the duration and price of each makeup service so I can choose the one that fits my event.*
*   **Acceptance Criteria:**
    *   Each service must display: Title, Price (with currency), Duration (mins/hours), and Description.
    *   The "Book Now" button must lead directly to the calendar for that specific service.
    *   Services marked as "Inactive" by the Admin must not appear.

#### **User Story 2: Real-Time Booking**
*As a client, I want to see only the times the artist is actually free so I don’t book a time that results in a cancellation.*
*   **Acceptance Criteria:**
    *   The calendar must gray out dates in the past.
    *   The calendar must gray out dates/times marked as "Unavailable" by the Admin.
    *   The system must prevent "double-booking" the same time slot for the same artist.
    *   Booking form must validate email format and phone number length.

---

### 5.2. Admin Experience

#### **User Story 3: Service Management**
*As an Admin, I want to manage my service list so I can update my pricing and offerings seasonally.*
*   **Acceptance Criteria:**
    *   Admin can create a new service with a name, description, price, and duration.
    *   Admin can edit existing services; changes must reflect on the public site immediately.
    *   Admin can "Archive" a service to remove it from the public view without losing historical data.

#### **User Story 4: Availability & Blackout Dates**
*As an Admin, I want to block out specific times for personal errands or vacations so that I am not booked when I am unavailable.*
*   **Acceptance Criteria:**
    *   Admin can select a single date or a date range to mark as "Unavailable."
    *   Admin can select specific time blocks (e.g., 2:00 PM - 5:00 PM) on a specific day.
    *   The UI must provide a clear visual distinction between "Booked by Client" and "Blocked by Admin."

#### **User Story 5: Appointment Oversight**
*As an Admin, I want to see all my upcoming appointments in one place so I can prepare for my work week.*
*   **Acceptance Criteria:**
    *   A "List View" or "Calendar View" of all confirmed appointments.
    *   Clicking an appointment reveals client contact info and the specific service booked.
    *   Admin has a "Cancel Appointment" button which triggers an automated notification to the client.

---

## 6. Technical Constraints & Logic
*   **Timezone Handling:** All bookings must be recorded in the Artist's local timezone.
*   **Concurrency:** If two users are viewing the same slot, the first to click "Confirm" secures it; the second receives a "This slot is no longer available" message.
*   **Authentication:** Admin access requires Email/Password login with session persistence.
*   **Data Integrity:** Deleting a service should not delete the history of appointments already completed for that service.

---

## 7. Edge Cases & Error Handling
*   **Booking in the Past:** The system must programmatically disable any time slot that has already passed.
*   **Zero-Duration Services:** The system must require a minimum duration of 15 minutes for any service to prevent calendar logic errors.
*   **Invalid Contact Info:** If a client enters an invalid email, the "Confirm Booking" button remains disabled to ensure the artist can reach them.

---

## 8. Future Roadmap (v2.0)
*   **Payment Gateway:** Integration with Stripe/PayPal for non-refundable deposits.
*   **SMS Integration:** Automated text reminders 24 hours before the session.
*   **Instagram Sync:** A "Live Feed" component to pull the latest IG posts into the portfolio automatically.
*   **Custom Intake Forms:** Allow the artist to ask specific questions (e.g., "Do you have skin allergies?") during the booking flow.