# KOMAROVA_CORE — family mail, mailbox and feedback architecture

**Document status:** approved architecture specification, 23 November 2026  
**Target branch:** `core-backend-foundation`  
**Implementation status:** architecture only. No mailbox connector, mail transport, message sync, public feedback backend or mail UI is implemented by this document.

## 1. Decision and scope

KOMAROVA_CORE will use a provider-neutral mail domain with separate adapters for Gmail and Yandex Mail. The family does not need to move to one provider to obtain a unified application.

Current provider allocation, as supplied by the project owner:
- Mother: Yandex Mail.
- Father: Gmail.
- Son: Gmail.

This is a recorded design input, not a live connection. Do not change addresses, migrate mailboxes, enable forwarding or create aliases without the mailbox owner's explicit decision.

The module has two distinct workflows:
1. **Compose a message:** prepare a message for the user's configured mail client. This is the initial, low-risk capability.
2. **Connect a mailbox:** authorized access to read, search, draft and/or send mail through a provider adapter. This is a later, separately approved integration.

A third workflow, **public feedback**, is separate from family mail and must not expose or directly target personal family mailboxes.

## 2. Provider-neutral domain model

The domain model must not make Gmail or Yandex-specific fields authoritative.

| Entity | Purpose | Stable identifier |
|---|---|---|
| Mailbox | One owner's mailbox connection and policy boundary | MAILBOX-ID |
| MailProvider | Provider adapter type (GMAIL, YANDEX, future provider) | PROVIDER-ID |
| MailAuthorization | Owner consent, scopes, status, expiry and revocation | MAILAUTH-ID |
| MailContact | Contact point and normalized address, linked optionally to a person | MAILCONTACT-ID |
| MailMessage | Message metadata and protected content reference | MAIL-ID |
| MailThread | Provider thread grouping, not a person identity | MAILTHREAD-ID |
| MailAttachment | Attachment metadata and quarantined binary reference | MAILATTACH-ID |
| MailDraft | Draft state and ownership | MAILDRAFT-ID |
| MailAction | Auditable compose, import, draft, send, revoke action | MAILACTION-ID |
| FeedbackSubmission | Public feedback intake record | FEEDBACK-ID |

All IDs are permanent and never reused. Email addresses, provider message IDs, thread IDs and usernames are external attributes, not primary family identity keys. A contact can have multiple addresses and a person can have multiple contact points. Address changes must preserve history and provenance.

## 3. Ownership, consent and permissions

Every mailbox has exactly one accountable owner. A connection is authorized independently for each mailbox.

- The owner initiates provider authorization and sees the requested scopes.
- A family administrator does not automatically gain access to another person's mailbox.
- Consent records identify the owner, provider, granted scopes, purpose, timestamp, status and revocation event.
- Read, search, draft and send are separate capabilities. Request the minimum scopes needed for the selected feature.
- Revocation disables connector access and records an audit event. It does not delete the owner's original mailbox.
- The son is a minor: require age-appropriate explanation/assent and guardian oversight, and restrict access and retention accordingly.
- Never ask a user to paste a password, app password, OAuth code, refresh token or session cookie into chat or project documentation.

Roles must be mapped to actions before implementation. Default policy is owner-only mailbox access. Any shared family mailbox view or delegated access requires explicit owner approval, a defined audience, a narrow scope and an audit trail.

## 4. Provider adapters

### Gmail

Use Google's supported OAuth/API mechanisms for the selected Gmail features. OAuth scopes must be narrow and explained. Store access/refresh tokens only in a protected server-side secret store or encrypted credential vault. Do not put tokens in frontend JavaScript, Git, SQLite plaintext fields, logs or static-site artifacts.

### Yandex Mail

Use only currently supported Yandex authorization and mail access mechanisms. Before implementation, verify current Yandex OAuth, IMAP/SMTP availability, account security requirements and any app-password limitations against current official documentation. Do not assume Gmail OAuth behavior maps directly to Yandex.

### Adapter contract

Each adapter implements a common interface for:
- authorization start/callback and secure token refresh;
- mailbox identity verification;
- capability discovery;
- list/search messages within authorized scope;
- fetch message metadata and body on demand;
- create/update drafts;
- send only when the send capability is explicitly granted;
- retrieve attachment streams into quarantine;
- revoke/disconnect and report provider errors.

Provider-specific IDs and raw payloads are retained only as provenance in protected storage. The domain layer consumes normalized fields and does not depend on a provider's message schema.

## 5. Initial compose workflow

The first implementation milestone may offer a **Написать письмо** action inside the authenticated private family application.

Inputs:
- selected recipient from the authorized private contact directory;
- optional subject;
- message body.

Behavior:
1. Validate recipient and encode subject/body safely.
2. Open the user's configured mail client using a `mailto:` URI or a supported platform deep link.
3. Clearly state that the message is opened in an external mail client and is not sent by KOMAROVA_CORE.
4. Do not claim delivery, save a sent copy or report success unless a later authorized provider adapter confirms it.
5. Do not place family addresses in public HTML or static JavaScript.

The private compose UI may select a family member's address only where the current user has permission to see that contact. A compose action does not grant read access to the recipient's mailbox.

## 6. Public feedback boundary

The public website must not offer a selector exposing family members' personal addresses.

Public feedback uses a dedicated project contact address or a protected server-side intake service. It requires:
- server-side validation and output encoding;
- anti-spam/rate limiting and abuse monitoring;
- minimal collection and a clear privacy notice;
- safe handling of attachments, or no attachments in the first version;
- a private queue with restricted access and an audit trail;
- no direct browser-to-personal-mailbox delivery and no embedded mail credentials.

If no dedicated project contact endpoint is configured, do not display a non-functional feedback form. A public mailto link is acceptable only if the owner explicitly approves a separate public project address.

## 7. Message, attachment and archive relationships

Messages may be linked to existing PERSON-ID, EVENT-ID, PLACE-ID, JOURNEY-ID, STORY-ID, SOURCE-ID and archive records through typed relationships. A message is not automatically a verified fact: preserve sender, timestamp, source mailbox, import time, provenance and confidence where applicable.

Email attachments are not immediately trusted archive originals. Intake flow:
1. owner selects a message or attachment and confirms import;
2. copy the attachment into private quarantine, leaving the source mailbox unchanged;
3. File Engine validates type and size, computes SHA-256 and checks duplicates;
4. record provenance and assign MATERIAL-ID / archive identifiers;
5. review metadata and entity links;
6. promote into the private archive only after successful checks.

No mailbox-wide bulk import, automatic forwarding, background indexing or public publication is enabled by this specification.

## 8. Data protection and retention

- Private mailbox addresses, message subjects, bodies, headers, attachments, provider IDs and contact relationships are confidential.
- Never include them in public GitHub Pages output, source maps, client bundles, public API responses, analytics events or ordinary logs.
- Encrypt data in transit and at rest. Keep provider tokens in a dedicated protected secret store.
- Logs record action type, actor, mailbox ID, result and trace ID, but not message bodies, credentials or full addresses unless strictly necessary.
- Define retention and deletion rules before enabling message import. Disconnecting a provider must not silently delete imported archive records; deletion must be an explicit, auditable operation.
- Public and private systems remain separate. GitHub Pages is not a mailbox client, secret store or private message database.

## 9. Delivery phases

**M0 — architecture and privacy contract:** this document; no runtime integration.

**M1 — private compose:** authenticated UI, private contact lookup, mailto/deep link, permission checks and tests. No server-side sending.

**M2 — one-mailbox pilot:** choose one consenting owner and provider; verify official provider APIs and scopes; implement read-only mailbox identity and bounded search before message bodies or attachments.

**M3 — controlled message workflow:** selected-message fetch, draft support and optional send capability, each separately authorized and audited.

**M4 — additional providers/mailboxes:** add Yandex/Gmail adapters per owner consent. Do not infer permission from family relationship.

**M5 — public feedback:** separate project endpoint and dedicated public contact identity, anti-spam and privacy review.

**M6 — archive linking:** selected attachment intake through File Engine, checksum, duplicate review and permanent IDs.

## 10. Acceptance criteria

1. Gmail and Yandex are represented by the same provider-neutral mailbox contract.
2. No provider migration or forwarding occurs without explicit owner approval.
3. A mailbox cannot be connected without owner authorization and a recorded scope.
4. One family member cannot read another mailbox by default.
5. Read/search/draft/send permissions are independently enforceable.
6. Revocation disables future connector access and creates an audit event.
7. No credentials or tokens appear in Git, frontend assets, logs or public output.
8. Public pages never reveal personal family email addresses or private message metadata.
9. Public feedback cannot route directly to a personal family mailbox.
10. A compose action truthfully opens an external mail client and never claims the message was sent.
11. Selected attachments are copied to quarantine, checksummed and duplicate-reviewed before archive registration.
12. Email contacts link to existing PERSON-ID records and never create identity duplicates.
13. Provider outages do not break the family registry or public site.
14. No feature is marked implemented until code, automated tests and a successful workflow exist.

## 11. Current status

This document records the approved target architecture only. The repository currently has no mail tables, provider adapters, OAuth flow, IMAP/SMTP integration, mailbox search, message import, compose interface or public feedback service. Those capabilities must be implemented and tested in later delivery phases.
