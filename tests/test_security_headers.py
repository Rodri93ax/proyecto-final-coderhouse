import unittest

from app import app


class SecurityHeadersTests(unittest.TestCase):
    def test_headers_on_success_and_not_found(self):
        client = app.test_client()

        for path, status in (
            ("/", 200),
            ("/health", 200),
            ("/metrics", 200),
            ("/robots.txt", 404),
            ("/sitemap.xml", 404),
        ):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.status_code, status)
                self.assertEqual(
                    response.headers.get("X-Content-Type-Options"), "nosniff"
                )
                self.assertEqual(
                    response.headers.get("Cache-Control"), "no-store"
                )
                self.assertEqual(
                    response.headers.get("Cross-Origin-Resource-Policy"),
                    "same-origin",
                )
                csp = response.headers.get("Content-Security-Policy", "")
                for directive in (
                    "default-src 'none'",
                    "frame-ancestors 'none'",
                    "base-uri 'none'",
                    "form-action 'none'",
                ):
                    self.assertIn(directive, csp)

                policy = response.headers.get("Permissions-Policy", "")
                for directive in ("camera=()", "microphone=()", "geolocation=()"):
                    self.assertIn(directive, policy)
