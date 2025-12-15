# API Usage Guide

Complete guide to using the AI-Driven Email Security Research Framework API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API is open for development. Production deployments should implement:
- JWT authentication
- API key management
- Rate limiting per user

## Endpoints

### 1. Health & Status

#### GET /health
Check system health.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "task_queue": "up",
    "proxy_pool": "up",
    "active_proxies": 15
  }
}
```

#### GET /stats
Get system statistics.

**Response:**
```json
{
  "decision_engine": {
    "total_decisions": 1234,
    "learning_enabled": true
  },
  "orchestrator": {
    "active_workflows": 5,
    "workflows_completed": 42
  },
  "task_queue": {
    "pending": 10,
    "processing": 3
  },
  "proxy_pool": {
    "total": 50,
    "active": 48,
    "avg_health": 0.92
  }
}
```

### 2. Operations

#### POST /api/v1/operations/start
Start a new research operation.

**Request Body:**
```json
{
  "target_emails": [
    "target1@example.com",
    "target2@example.com"
  ],
  "services": ["mega", "dropbox", "pcloud"],
  "priority": 7,
  "use_osint": true,
  "use_llm": true
}
```

**Parameters:**
- `target_emails` (required): List of email addresses to research
- `services` (optional): Specific services to check (defaults to all)
- `priority` (optional): Task priority 1-10 (default: 5)
- `use_osint` (optional): Enable OSINT gathering (default: true)
- `use_llm` (optional): Use LLM for password generation (default: true)

**Response:**
```json
{
  "operation_id": "OP-2-12345",
  "target_count": 2,
  "workflows_created": 2,
  "status": "queued"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/v1/operations/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_emails": ["test@example.com"],
    "services": ["mega"],
    "priority": 8
  }'
```

**Example (Python):**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/operations/start',
    json={
        'target_emails': ['test@example.com'],
        'services': ['mega', 'dropbox'],
        'priority': 7
    }
)

operation = response.json()
print(f"Operation ID: {operation['operation_id']}")
```

#### GET /api/v1/operations/status/{operation_id}
Get operation status and progress.

**Response:**
```json
{
  "operation_id": "OP-2-12345",
  "status": "running",
  "progress": {
    "total": 10,
    "completed": 7,
    "failed": 1,
    "in_progress": 2
  }
}
```

#### GET /api/v1/operations/results/{operation_id}
Get operation results.

**Response:**
```json
{
  "operation_id": "OP-2-12345",
  "results": [
    {
      "email": "target@example.com",
      "service": "mega",
      "status": "success",
      "password": "found_password123",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "summary": {
    "total_targets": 2,
    "successful_hits": 1,
    "services_checked": ["mega", "dropbox"]
  }
}
```

### 3. Workflows

#### GET /api/v1/workflows/{workflow_id}
Get detailed workflow status.

**Response:**
```json
{
  "workflow_id": "wf-abc123",
  "target_email": "target@example.com",
  "status": "in_progress",
  "tasks_by_status": {
    "completed": 3,
    "in_progress": 2,
    "pending": 1
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### POST /api/v1/workflows/{workflow_id}/cancel
Cancel a running workflow.

**Response:**
```json
{
  "workflow_id": "wf-abc123",
  "status": "cancelled"
}
```

### 4. Monitoring

#### GET /api/v1/monitoring/metrics
Prometheus-compatible metrics endpoint.

**Response:** (Prometheus format)
```
# HELP workflows_total Total workflows created
# TYPE workflows_total counter
workflows_total 42.0

# HELP tasks_total Total tasks executed
# TYPE tasks_total counter
tasks_total{task_type="osint_gather",status="success"} 38.0
tasks_total{task_type="attack_execute",status="success"} 25.0
```

#### GET /api/v1/monitoring/stats
Detailed system statistics.

## Usage Examples

### Complete Workflow Example

```python
import requests
import time

# 1. Start an operation
response = requests.post(
    'http://localhost:8000/api/v1/operations/start',
    json={
        'target_emails': [
            'user1@example.com',
            'user2@example.com'
        ],
        'services': ['mega', 'dropbox', 'instagram'],
        'priority': 8,
        'use_osint': True,
        'use_llm': True
    }
)

operation_id = response.json()['operation_id']
print(f"Started operation: {operation_id}")

# 2. Poll for status
while True:
    status_response = requests.get(
        f'http://localhost:8000/api/v1/operations/status/{operation_id}'
    )
    
    status = status_response.json()
    print(f"Progress: {status['progress']}")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(5)  # Wait 5 seconds

# 3. Get results
results_response = requests.get(
    f'http://localhost:8000/api/v1/operations/results/{operation_id}'
)

results = results_response.json()

# 4. Process results
for result in results['results']:
    if result['status'] == 'success':
        print(f"✓ {result['email']} - {result['service']}: {result['password']}")
    else:
        print(f"✗ {result['email']} - {result['service']}: Failed")
```

### Batch Processing

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def process_batch(emails):
    """Process a batch of emails"""
    response = requests.post(
        'http://localhost:8000/api/v1/operations/start',
        json={'target_emails': emails}
    )
    return response.json()['operation_id']

# Read emails from file
with open('emails.txt', 'r') as f:
    all_emails = [line.strip() for line in f]

# Process in batches of 100
batch_size = 100
batches = [all_emails[i:i+batch_size] for i in range(0, len(all_emails), batch_size)]

# Submit batches in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    operation_ids = list(executor.map(process_batch, batches))

print(f"Created {len(operation_ids)} operations")
```

### Real-time Monitoring

```python
import requests
import time
from datetime import datetime

def monitor_system():
    """Monitor system health and statistics"""
    while True:
        # Get health
        health = requests.get('http://localhost:8000/health').json()
        
        # Get stats
        stats = requests.get('http://localhost:8000/stats').json()
        
        # Display
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}]")
        print(f"System Status: {health['status']}")
        print(f"Active Proxies: {stats['proxy_pool']['active']}/{stats['proxy_pool']['total']}")
        print(f"Queue: {stats['task_queue']['pending']} pending, {stats['task_queue']['processing']} processing")
        print(f"Workflows: {stats['orchestrator']['active_workflows']} active")
        
        time.sleep(10)

monitor_system()
```

## WebSocket Support (Coming Soon)

For real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/operations');

ws.on('message', (data) => {
    const update = JSON.parse(data);
    console.log('Operation update:', update);
});
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message here",
  "error_code": "INVALID_EMAIL",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example Error Handling:**
```python
try:
    response = requests.post(
        'http://localhost:8000/api/v1/operations/start',
        json={'target_emails': ['invalid']}
    )
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"Error: {e.response.json()['detail']}")
```

## Rate Limiting

- Default: 100 requests per minute per IP
- Configurable in `.env`:
  ```
  GLOBAL_RATE_LIMIT=100
  RATE_LIMIT_WINDOW=60
  ```

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1610712000
```

## Best Practices

1. **Batch Requests**: Group multiple emails into single operations
2. **Poll Wisely**: Don't poll status more than once per 5 seconds
3. **Handle Errors**: Always implement retry logic with backoff
4. **Monitor Health**: Check `/health` before submitting large batches
5. **Store Results**: Save results immediately, they may have TTL

## SDK (Python)

A Python SDK is available for easier integration:

```python
from ai_email_checker import AIEmailChecker

# Initialize
client = AIEmailChecker(
    base_url='http://localhost:8000',
    api_key='your-api-key'  # If auth enabled
)

# Start operation
operation = client.start_operation(
    emails=['test@example.com'],
    services=['mega', 'dropbox']
)

# Wait for completion
results = operation.wait_for_completion(timeout=300)

# Process results
for result in results:
    print(result)
```

## Next Steps

- Explore the [Interactive API Documentation](http://localhost:8000/docs)
- Read about [Custom Checkers](./custom-checkers.md)
- Set up [Monitoring](./monitoring.md)
- Review [Security Best Practices](./security.md)
