1️⃣ Client → Gateway -- HTTPS 
What happens
    • Client sends HTTPS request:
POST https://api.example.com/projects/123
Authorization: Bearer eyJhbGciOi...
X-Tenant-Id: tenant_a
Gateway responsibilities
    • TLS termination
    • Request normalization
    • Header extraction
Implementation (Gateway)
    • Use FastAPI + Uvicorn
    • HTTPS via:
        ◦ Nginx in front (recommended)
        ◦ or FastAPI with SSL certs

2️⃣ Authentication（JWT and API Key）
What happens
    • Gateway verifies identity
    • Does NOT trust backend requests without verification
JWT Flow (Recommended)
    1. Extract Authorization header
    2. Verify JWT signature
    3. Validate:
        ◦ expiration
        ◦ issuer
        ◦ audience
Implementation
def authenticate(request):
    token = request.headers.get("Authorization")
    payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    return payload  # user_id, roles
🔹 API Key flow is similar but lookup is usually MySQL.

3️⃣ Authorization（user）
What happens
    • Check what the user is active
user_id=42
user_id=username
Implementation
    • Gateway enforces coarse-grained auth
    • Backend enforces fine-grained business rules

4️⃣ Rate Limiting
What happens
    • Prevent abuse
    • Protect backend services
Common strategies
    • Per IP
    • Per user
    • Per tenant
    • Per API key
Implementation (Redis)
key = rate:{user_id}:{api}
INCR key
EXPIRE key 60
If exceeded → 429 Too Many Requests
✔️ Tools:
    • Redis
    • Token Bucket / Leaky Bucket algorithm

5️⃣ Route Matching
What happens
    • Gateway decides which backend service handles the request
Example routing table
/projects/**  → project-service
/auth/**      → auth-service
/ecs/**       → ecs-service
Implementation
ROUTES = {
    "/projects": "project-service",
    "/auth": "auth-service"
}
✔️ Can be:
    • Static config
    • DB-driven
    • Nacos

6️⃣ Load Balancing
What happens
    • Choose one instance of a service
Strategies
    • Round-robin
    • Least connections
    • Weighted
Implementation
instances = [
  "http://project-service-1:8000",
  "http://project-service-2:8000"
]

target = random.choice(instances)
✔️ handled by:
    • Kubernetes Service
    • Nginx upstream
    • Service mesh (Istio)

7️⃣ Proxy Forwarding
What happens
    • Gateway forwards request to backend
    • Adds trusted headers
Headers added
X-User-Id: 42
X-Active: true
X-Request-Id: uuid
Implementation
async with httpx.AsyncClient() as client:
    response = await client.request(
        method=request.method,
        url=target_url,
        headers=forward_headers,
        content=body
    )
🚫 Backend must NOT re-authenticate JWT
✔️ Trust gateway via mTLS / internal network

8️⃣ Logging & Tracing
What happens
    • Track request across services
    • Debug latency and failures
Logging
{
  "request_id": "abc-123",
  "service": "gateway",
  "path": "/projects/123",
  "status": 200,
  "latency_ms": 38
}
Tracing
    • OpenTelemetry
Client → Gateway → project-service → DB
✔️ Gateway generates X-Trace-Id

9️⃣ Backend Microservices（What they do）
Backend responsibilities
    • Business logic
    • DB operations
    • Internal validation
What backend trusts
    • X-User-Id
    • X-Roles
Example (project-service)
user_id = request.headers["X-User-Id"]
projects = db.query(Project).filter_by(user_id=user_id)
🚫 Backend does NOT:
    • Parse JWT
    • Do rate limiting
    • Do routing




API Categories   -----Exposure
External APIs
Login, Logout, Registration, Project List, Dashboard, Public Service APIs
Internal APIs
User management (sys_user CRUD), Tenant configs, Service-to-Service gRPC calls
Monitoring / Metrics APIs
/actuator/metrics
/health, /ready


