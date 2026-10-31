"""A local, dependency-free example of secure lead-inquiry input validation.

This module does not send emails, save customer data, or connect to a service.
It is a portfolio QA sample, not the Nujoka Studio production form handler.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from typing import Mapping

SERVICES = frozenset({"backend-repair", "workflow-automation", "qa-audit", "documentation"})
_MAX_STDIN_BYTES = 16 * 1024
_DOMAIN_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
_LOCAL_PART = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+\Z")


class InquiryValidationError(ValueError):
    """Validation failure whose message contains no submitted personal data."""


@dataclass(frozen=True)
class Inquiry:
    name: str
    email: str
    service: str
    brief: str

    @property
    def dedupe_fingerprint(self) -> str:
        """Stable equivalence key; NOT anonymity, authentication, or secure storage."""
        normalized_brief = " ".join(self.brief.split()).casefold()
        message = json.dumps(
            [self.email.casefold(), self.service, normalized_brief],
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return hashlib.sha256(message.encode("utf-8")).hexdigest()


def _string_field(raw: Mapping[str, object], key: str, lo: int, hi: int) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise InquiryValidationError(f"{key}: expected text")
    value = value.strip()
    if not lo <= len(value) <= hi:
        raise InquiryValidationError(f"{key}: length must be {lo}–{hi} characters")
    if any(ord(c) < 32 and c not in "\n\t\r" for c in value):
        raise InquiryValidationError(f"{key}: invalid control character")
    return value


def _email(value: str) -> str:
    if any(c.isspace() for c in value) or value.count("@") != 1:
        raise InquiryValidationError("email: invalid address")
    local, domain = value.rsplit("@", 1)
    if not (1 <= len(local) <= 64 and _LOCAL_PART.fullmatch(local)):
        raise InquiryValidationError("email: invalid address")
    if local.startswith(".") or local.endswith(".") or ".." in local:
        raise InquiryValidationError("email: invalid address")
    labels = domain.lower().split(".")
    if not (len(labels) >= 2 and 2 <= len(labels[-1]) <= 63):
        raise InquiryValidationError("email: invalid address")
    if any(not _DOMAIN_LABEL.fullmatch(label) for label in labels):
        raise InquiryValidationError("email: invalid address")
    return f"{local}@{domain.lower()}"


def validate_inquiry(raw: object) -> Inquiry:
    """Reject malformed submissions; return a normalized, immutable Inquiry.

    This intentionally supports a conservative ASCII-only email subset; it is
    not a complete RFC 5322 or internationalized-address validator.
    """
    if not isinstance(raw, dict):
        raise InquiryValidationError("inquiry: expected an object")
    if raw.get("website") not in (None, ""):
        raise InquiryValidationError("inquiry: rejected")  # honeypot field
    name = _string_field(raw, "name", 2, 80)
    if "\r" in name or "\n" in name:
        raise InquiryValidationError("name: line breaks not allowed")
    email = _email(_string_field(raw, "email", 3, 254))
    service = _string_field(raw, "service", 2, 40)
    if service not in SERVICES:
        raise InquiryValidationError("service: unsupported category")
    brief = _string_field(raw, "brief", 40, 4000)
    return Inquiry(name=name, email=email, service=service, brief=brief)


def run_cli(stdin: object = None, stdout: object = None, stderr: object = None) -> int:
    """Read at most 16 KiB, emit a PII-free validation result and exit status."""
    source = sys.stdin.buffer if stdin is None else stdin
    target = sys.stdout if stdout is None else stdout
    errors = sys.stderr if stderr is None else stderr
    try:
        raw = source.read(_MAX_STDIN_BYTES + 1)
        if len(raw) > _MAX_STDIN_BYTES:
            raise InquiryValidationError("inquiry: input too large")
        data = json.loads(raw.decode("utf-8"))
        inquiry = validate_inquiry(data)
    except (InquiryValidationError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        reason = str(exc) if isinstance(exc, InquiryValidationError) else "inquiry: invalid JSON"
        print(json.dumps({"valid": False, "error": reason}), file=target)
        return 2
    print(json.dumps({"valid": True, "service": inquiry.service, "fingerprint": inquiry.dedupe_fingerprint}), file=target)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
