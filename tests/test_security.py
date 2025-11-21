"""
Test security features including headers, input sanitization, and rate limiting.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestSecurityHeaders:
    """Test security headers are properly set."""
    
    def test_security_headers_present(self):
        """Verify all security headers are present in responses."""
        response = client.get("/health")
        
        # Security headers
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Referrer-Policy" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
    
    def test_csp_header_validity(self):
        """Verify CSP header contains required directives."""
        response = client.get("/health")
        csp = response.headers.get("Content-Security-Policy", "")
        
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "base-uri 'self'" in csp


class TestInputSanitization:
    """Test input sanitization and validation."""
    
    def test_xss_prevention_in_destination(self):
        """Test that XSS attempts in destination are handled."""
        payload = {
            "destination": "<script>alert('XSS')</script>Tokyo",
            "language": "en"
        }
        response = client.post("/api/generate", json=payload)
        
        # Should either sanitize or reject
        assert response.status_code in [400, 422], "Should reject or sanitize dangerous input"
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are handled."""
        payload = {
            "destination": "'; DROP TABLE users; --",
            "language": "en"
        }
        response = client.post("/api/generate", json=payload)
        
        # Should reject invalid input
        assert response.status_code in [400, 422]
    
    def test_destination_length_validation(self):
        """Test destination length limits."""
        payload = {
            "destination": "A" * 101,  # Exceeds 100 char limit
            "language": "en"
        }
        response = client.post("/api/generate", json=payload)
        
        assert response.status_code in [400, 422]
        if response.status_code == 400:
            data = response.json()
            assert "too long" in data.get("message", "").lower()
    
    def test_empty_destination_rejected(self):
        """Test empty destination is rejected."""
        payload = {
            "destination": "",
            "language": "en"
        }
        response = client.post("/api/generate", json=payload)
        
        assert response.status_code in [400, 422]


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limit_headers_present(self):
        """Verify rate limit headers are included in responses."""
        response = client.get("/health")
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
    
    @pytest.mark.slow
    def test_rate_limit_enforcement(self):
        """Test that rate limiting blocks excessive requests."""
        # This test makes many requests and may be slow
        # Make requests until rate limit is hit
        responses = []
        for _ in range(105):  # Exceeds default limit of 100
            responses.append(client.get("/health"))
        
        # At least one response should be rate limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes, "Rate limiting should kick in"


class TestRequestValidation:
    """Test request validation and error handling."""
    
    def test_invalid_json_rejected(self):
        """Test that invalid JSON is rejected."""
        response = client.post(
            "/api/generate",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_field(self):
        """Test that missing required fields are rejected."""
        response = client.post("/api/generate", json={})
        assert response.status_code == 422
    
    def test_invalid_content_type(self):
        """Test that wrong content type is handled."""
        response = client.post(
            "/api/generate",
            data="destination=Tokyo",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # Should either reject or handle gracefully
        assert response.status_code in [400, 415, 422]


class TestCorrelationId:
    """Test correlation ID for request tracing."""
    
    def test_correlation_id_added(self):
        """Verify correlation ID is added to responses."""
        response = client.get("/health")
        assert "X-Correlation-ID" in response.headers
        
        # Should be a valid UUID format
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) == 36  # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    
    def test_correlation_id_preserved(self):
        """Verify provided correlation ID is preserved."""
        custom_id = "custom-correlation-123"
        response = client.get("/health", headers={"X-Correlation-ID": custom_id})
        assert response.headers["X-Correlation-ID"] == custom_id
