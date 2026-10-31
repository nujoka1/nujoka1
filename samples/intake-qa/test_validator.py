import io
import json
import unittest

from validator import InquiryValidationError, run_cli, validate_inquiry


VALID = {
    "name": "Ada Okafor",
    "email": "Ada@Example.COM",
    "service": "qa-audit",
    "brief": "Please check our inquiry form for duplicate submissions and errors.",
}


class InquiryValidationTests(unittest.TestCase):
    def test_valid_normalizes_domain(self):
        result = validate_inquiry(VALID)
        self.assertEqual(result.email, "Ada@example.com")
        self.assertEqual(result.service, "qa-audit")

    def test_brief_requires_useful_description(self):
        with self.assertRaisesRegex(InquiryValidationError, "brief: length"):
            validate_inquiry({**VALID, "brief": "Too short"})

    def test_control_and_header_injection_rejected(self):
        for field, injected in (("email", "a@example.com\nBcc:x@e.com"), ("name", "A\r\nBcc: x")):
            with self.subTest(field=field), self.assertRaises(InquiryValidationError):
                validate_inquiry({**VALID, field: injected})

    def test_conservative_email_validation(self):
        for address in ("foo@localhost", "a..b@example.com", "x@-example.com", "x @example.com", "x@example.c", "a@@b.com"):
            with self.subTest(address=address), self.assertRaisesRegex(InquiryValidationError, "email: invalid"):
                validate_inquiry({**VALID, "email": address})

    def test_reject_non_string_and_non_dict(self):
        with self.assertRaisesRegex(InquiryValidationError, "name: expected text"):
            validate_inquiry({**VALID, "name": 12})
        with self.assertRaisesRegex(InquiryValidationError, "inquiry: expected an object"):
            validate_inquiry([VALID])

    def test_reject_unsupported_category(self):
        with self.assertRaisesRegex(InquiryValidationError, "unsupported category"):
            validate_inquiry({**VALID, "service": "send-money"})

    def test_honeypot_rejected(self):
        with self.assertRaisesRegex(InquiryValidationError, "inquiry: rejected"):
            validate_inquiry({**VALID, "website": "https://spam.example"})

    def test_normalized_brief_has_same_fingerprint(self):
        a = validate_inquiry(VALID)
        b = validate_inquiry({**VALID, "brief": VALID["brief"].upper().replace(" ", "  ")})
        self.assertEqual(a.dedupe_fingerprint, b.dedupe_fingerprint)

    def test_different_brief_has_different_fingerprint(self):
        a = validate_inquiry(VALID)
        b = validate_inquiry({**VALID, "brief": "Please check our inquiry form for validation bugs and missing fields."})
        self.assertNotEqual(a.dedupe_fingerprint, b.dedupe_fingerprint)

    def test_cli_redacts_personal_data(self):
        stdout = io.StringIO()
        code = run_cli(io.BytesIO(json.dumps(VALID).encode()), stdout)
        self.assertEqual(code, 0)
        response = json.loads(stdout.getvalue())
        self.assertTrue(response["valid"])
        self.assertNotIn(VALID["email"], stdout.getvalue())
        self.assertNotIn(VALID["name"], stdout.getvalue())

    def test_cli_rejects_bad_json(self):
        stdout = io.StringIO()
        self.assertEqual(run_cli(io.BytesIO(b"not json"), stdout), 2)
        self.assertEqual(json.loads(stdout.getvalue())["error"], "inquiry: invalid JSON")

    def test_cli_input_size_limit(self):
        stdout = io.StringIO()
        self.assertEqual(run_cli(io.BytesIO(b"x" * (16 * 1024 + 1)), stdout), 2)
        self.assertIn("too large", stdout.getvalue())

    def test_no_unneeded_storage_side_effect(self):
        self.assertEqual(len(validate_inquiry(VALID).dedupe_fingerprint), 64)


if __name__ == "__main__":
    unittest.main()
