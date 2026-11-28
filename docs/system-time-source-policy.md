# KOMAROVA_CORE — system time source policy

**Status:** approved implementation rule  
**Scope:** browser clients, backend services, calendar, archive metadata, audit records and tests.

## Decision

KOMAROVA_CORE does not obtain the current time from websites, public time APIs, remote widgets or other network time services. The application does not implement its own internet time synchronization.

## Required behavior

1. **Browser/local interface:** use the computer or phone operating-system clock through native browser date/time APIs. Do not hardcode a country, region, UTC offset or fixed daylight-saving rule.
2. **Backend records and audit:** use the backend host operating-system clock. Normalize timestamps to timezone-aware UTC for storage and exchange. UTC is a timestamp representation, not a remote time source.
3. **Historical data:** event dates, photo capture dates, document dates and place visits must come from the user or recorded source. Upload time must never overwrite a historical date.
4. **Calendar:** preserve explicit event timezone and all-day semantics. For events without an explicit timezone, use the device's local timezone for display and editing.
5. **Incorrect system clock:** do not silently fall back to an online clock. Preserve supplied source timestamps and make clock-related uncertainty visible where it affects the record.
6. **Testing:** use a controllable/frozen clock in deterministic tests. Do not replace the production OS clock with a network time dependency.

## Current code assessment

- `backend/app/models.py` defines `utc_now()` as `datetime.now(timezone.utc)`. Python reads the backend host's system clock; timezone-aware UTC is applied to the returned value.
- `assets/js/supabase-archive.js` uses the browser's native `Date` parsing/formatting for date metadata. It does not call an external time service.
- No dedicated online time provider is required or approved.

## Acceptance checks

- No HTTP request to a time API or clock website is made to obtain the current time.
- Local UI time follows the device OS clock and its configured timezone.
- Backend audit timestamps follow the backend host OS clock and are serialized as UTC.
- Historical user/source dates remain unchanged by upload or display conversion.
- Calendar timezone and all-day values survive save/load/export round trips.

This policy does not set the device clock, change Windows time settings, or claim that a device/server clock is accurate. Clock accuracy remains an operating-system administration concern.
