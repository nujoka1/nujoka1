# Nujoka Studio — Lead-inquiry QA sample

A **self-contained, locally testable demonstration** of validating a business inquiry payload. This sample supports Nujoka Studio's QA and backend-repair portfolio. It is **not wired to the live Nujoka Studio website**, is not a client implementation, and is not evidence of production security.

## Scope and acceptance criteria

- Accept JSON objects with `name` (2–80 characters), `email` (conservative ASCII address subset), `service` (approved enum) and `brief` (40–4,000 characters).
- Reject type errors, invalid address syntax, header/line-break injection in identity fields, unapproved services and the `website` honeypot if filled.
- Constrain CLI input to **16 KiB**, report structured errors without repeating user input, and produce a stable SHA-256 fingerprint for detecting **semantically identical inquiry attempts**.
- Keep input entirely in memory. **Do not** send emails, call remote APIs, save submissions, log user details or collect payments.
- Use only the Python standard library; unit tests must run without credentials or external services.

## Run

Requires Python 3.10+.

```bash
cd samples/intake-qa
python3 -m unittest -v test_validator.py
python3 validator.py <<'JSON'
{"name":"Ada Okafor","email":"ada@example.com","service":"qa-audit","brief":"Please check our inquiry form for duplicate submissions and errors."}
JSON
```

The CLI emits a response containing only validity, service and a fingerprint (on success), or a field-level error (on failure). It returns exit code 0 for valid input and 2 for invalid input.

## Threat model and deliberate limits

- The hash is **not encryption, anonymity, authentication or an identifier safe to publish across organizations**. Email addresses in a hashed input may still be guessed. Use a secret-key HMAC and a correctly managed key if fingerprints must be stored in a real service; retain data only as long as justified.
- A fingerprint is only a **key**. Duplicate suppression would require an atomic, durable store with expiry and idempotent processing; this demo does not perform that storage, lock or outbound side effect.
- Regex syntax checking does not prove mailbox ownership or deliverability. Internationalized email addresses and many RFC-valid forms are intentionally unsupported; production validation should use a reviewed library and product-specific policy.
- This does not include spam detection, CAPTCHA, authentication, rate limiting, consent records, secure storage, DPA/compliance obligations, threat logging or a browser E2E test.
- The Nujoka Studio site currently prepares an email using the visitor's own email app. This sample **does not claim to fix, host or replace** that form. In particular, form submission is not persisted until an actual backend or approved CRM is integrated and tested.

## Evidence

Check the accompanying `test_validator.py` for named, reproducible tests (including malformed input, duplicate equivalence, size bounds and data redaction). **Test counts/results should only be quoted after executing the tests in the target environment**.
