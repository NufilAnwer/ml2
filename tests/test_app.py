"""
Unit & Integration Tests for VisionGuard
Tests:
- GET / (Home page renders)
- GET /health (Healthcheck endpoint)
- GET /history (Database history page)
- File validation (rejects invalid extensions and unparseable payloads)
"""

import io
import unittest
from app.app import app
from app.database import init_db

class VisionGuardTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        init_db()
        cls.client = app.test_client()

    def test_home_page(self):
        """Test that the index/upload page loads successfully."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"VisionGuard", response.data)
        self.assertIn(b"AI-Generated", response.data)

    def test_health_endpoint(self):
        """Test the healthcheck endpoint."""
        response = self.client.get("/health")
        self.assertIn(response.status_code, [200, 503])
        json_data = response.get_json()
        self.assertIn("status", json_data)
        self.assertIn("timestamp", json_data)

    def test_history_page(self):
        """Test the persistent audit trail page loads."""
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Prediction History", response.data)

    def test_reject_invalid_extension(self):
        """Test uploading an unauthorized file type (.pdf)."""
        data = {
            "file": (io.BytesIO(b"%PDF-1.4 fake pdf data"), "document.pdf")
        }
        response = self.client.post("/predict", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)

    def test_reject_corrupted_image(self):
        """Test uploading a file with image extension but corrupt content."""
        data = {
            "file": (io.BytesIO(b"garbage not an image"), "corrupted.jpg")
        }
        response = self.client.post("/predict", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
