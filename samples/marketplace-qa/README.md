# Marketplace QA: risk-based release-readiness assessment (portfolio exercise)

**Status:** Synthetic assessment template, not a report about any real customer, vendor, or employer. No marketplace system was accessed, no test cases were executed against a live application, and no defects are asserted. Created as a reusable demonstration of QA planning and traceability for an ordering/delivery product.

## Scope, assumptions and evidence standard

Assumed roles: customer, vendor, rider, support operator and administrator. Assumed workflows: catalog, cart, order placement, payment, dispatch, tracking, cancellation, refunds, notifications and role-scoped access. Actual architecture, payment processor, mobile clients, SLAs, GPS behavior and business rules must be confirmed with the product owner before execution. All data in this plan is **fictional test data**. Never use a live card, personal address, or real customer account.

**Evidence rules:** record build/commit, environment, test-data identifier, timestamp with timezone, request/response identifiers (with secrets redacted), steps, expected result, observed result, screenshot/video reference and retest status. Do not mark PASS without running the test. Do not call a system production-ready from the number of cases alone.

### Risk model

P0: money movement, unauthorized access, double charge, lost order, critical dispatch failure, or data exposure. P1: core journey broken with workaround or incorrect user state. P2: recoverable functional/UX defect. Severity (impact) and priority (fix order) must be assessed separately. Release decision: block for any open P0, require owner sign-off and mitigations for open P1, record accepted P2 risk; also require observability and rollback evidence.

## Candidate test cases

These are **planned**, not executed. Replace placeholders with actual product rules and API contracts before use.

| ID | Priority | Area | Setup / action | Expected result / acceptance oracle |
|---|---|---|---|---|
| MQA-01 | P0 | Authorization | Customer A requests Customer B's order by guessed ID | 403/404 as designed; no B data or side-channel detail |
| MQA-02 | P0 | Authorization | Vendor A attempts to update Vendor B's inventory | Request rejected; no cross-tenant mutation |
| MQA-03 | P0 | Payments | Repeat same checkout idempotency key during timeout/retry | Exactly one charge and one logical order; replay returns consistent result |
| MQA-04 | P0 | Payments | Payment authorized, order creation fails | Compensating/refund workflow or recoverable pending state; alert emitted |
| MQA-05 | P0 | Payments | Duplicate/out-of-order signed provider webhooks | Signature verified; event deduplicated; order state cannot regress |
| MQA-06 | P0 | Price integrity | Change unit price in client request before checkout | Server calculates trusted amount; manipulation rejected |
| MQA-07 | P0 | Inventory | Two customers concurrently purchase final unit | At most one successful reservation; inventory never negative |
| MQA-08 | P0 | Dispatch | Two riders accept same unassigned job simultaneously | Exactly one assignment succeeds; loser sees conflict |
| MQA-09 | P0 | PII | Rider queries unrelated customer addresses/phone numbers | Data minimized to authorized active delivery; unrelated details denied |
| MQA-10 | P0 | State machine | Delivered order receives stale 'preparing' event | Terminal state preserved; event handled idempotently |
| MQA-11 | P1 | Catalog | Vendor disables out-of-stock item mid-cart | Checkout validates availability; clear non-destructive feedback |
| MQA-12 | P1 | Cart | Customer changes quantities and removes last item | Totals and empty state consistent across refresh |
| MQA-13 | P1 | Checkout | Invalid delivery zone or incomplete address | Order cannot be submitted; actionable field validation |
| MQA-14 | P1 | Network | Mobile loses network after checkout request sent | Client recovers state by order lookup; no blind duplicate purchase |
| MQA-15 | P1 | Cancellation | Cancel before/after dispatch cut-off | Rules enforced; refund eligibility and audit history consistent |
| MQA-16 | P1 | GPS | Rider location permission denied or stale | Graceful fallback; stale timestamp surfaced, no fabricated live position |
| MQA-17 | P1 | Notifications | Push delivery fails or arrives twice | Order state remains authoritative; retries do not duplicate business actions |
| MQA-18 | P1 | Accessibility | Keyboard-only checkout, focus, labels and errors | Controls reachable, focus visible, errors announced; evaluate WCAG 2.2 AA |
| MQA-19 | P1 | Time zones | Cross-midnight order in different client/vendor zones | Stored timestamps and displayed ETA use explicit offsets and consistent rules |
| MQA-20 | P1 | Refund | Partial refund issued after substitution | Refund amount bounded by captured balance; ledger and customer view reconcile |
| MQA-21 | P1 | Reliability | Restart API worker mid-payment webhook | Durable processing resumes; event not lost or applied twice |
| MQA-22 | P2 | Usability | Slow 3G catalog loading and image failures | Useful skeleton/error states; user can retry without losing cart |
| MQA-23 | P2 | Internationalization | Long item names and locale-specific currency display | No clipped actionable text; currency and minor units unambiguous |
| MQA-24 | P1 | Admin audit | Support operator adjusts order/refund with valid authorization | Immutable audit entry includes actor, reason, time and before/after values |

## Suggested API-level checks (illustrative contracts only)

1. `POST /checkout` with a stable `Idempotency-Key` and a synthetic cart. Retry concurrently. Inspect payment-provider test-mode transactions, order count and idempotency record. **Do not assume the endpoint exists.**
2. `GET /orders/{id}` using a different synthetic customer's token. Assert access denial and absence of PII in response and logs.
3. Simulate webhook redelivery and out-of-order transitions using the provider's official sandbox and signed fixtures. Verify state invariants and audit.
4. Verify cancellation/dispatch concurrency with repeatable barriers and a clean database fixture. Check committed state, not only HTTP status.

No payment sandbox credentials, system endpoints or API schemas are supplied in this exercise; these steps are a test design, not an executed result.

## Reproducible defect report template

- **ID / summary / severity / priority:**
- **Environment:** build SHA, service version, device/browser/OS, test account, timezone.
- **Preconditions:** synthetic data, role, feature flags, network conditions.
- **Steps to reproduce:** numbered, deterministic, minimal.
- **Expected result:** explicit acceptance criterion or product specification link.
- **Actual result:** objective observation; attach redacted request/response IDs and screenshots.
- **Reproducibility:** N runs / N failures, with timestamps.
- **Impact / workaround / affected users:** measured or marked unknown.
- **Root cause:** unconfirmed until engineering investigation.
- **Retest evidence:** fix SHA, date, exact cases rerun, regression result.

## Exit checklist

Requirements and API contracts approved; P0 cases executed and passed; unresolved risks owned; critical-path regression across customer/vendor/rider/admin completed; monitoring and alerts tested; backup/recovery and rollback verified; payment reconciliation confirmed in sandbox; security review signed off; privacy/retention checks completed; release owner approval recorded. **No release recommendation is possible without actual evidence.**

## Portfolio positioning

This artifact demonstrates **risk-based QA design and documentation**, not 2–5 years of professional QA employment, hands-on access to a named employer's application, or executed tests. A prospective client can request a bounded paid QA milestone after providing authorized staging access and acceptance criteria.
