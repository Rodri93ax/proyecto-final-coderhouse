from flask import Flask, Response, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUESTS = Counter(
    "app_requests_total",
    "Total de solicitudes HTTP",
    ["endpoint", "status"],
)


@app.after_request
def record_request(response):
    if request.endpoint != "metrics":
        REQUESTS.labels(
            endpoint=request.endpoint or "not_found",
            status=str(response.status_code),
        ).inc()
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'; "
        "base-uri 'none'; form-action 'none'"
    )
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def index():
    return {
        "proyecto": "Pipeline CI/CD - Coderhouse",
        "autor": "Rodrigo Arrocha",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)
