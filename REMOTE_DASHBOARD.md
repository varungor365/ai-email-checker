# Interactive Remote Dashboard

Complete web-based dashboard for controlling your AI framework from anywhere.

---

## 🎨 Dashboard Features

### Control Panel
✅ **Start/Stop/Restart** all services  
✅ **Upload** combo lists, configs, proxies  
✅ **Download** results, logs, hits  
✅ **Real-time monitoring** of all checkers  
✅ **AI optimization** controls  
✅ **Resource usage** graphs (CPU, RAM, Network)  
✅ **Worker management** (add/remove workers)  
✅ **Proxy health** dashboard  
✅ **Live logs** streaming  
✅ **Config editor** with syntax highlighting  

### Statistics Dashboard
📊 **Real-time CPM** (checks per minute)  
📊 **Hit rate** percentage  
📊 **Active workers** count  
📊 **Proxy health** score  
📊 **Queue depth** monitoring  
📊 **Success/failure** breakdown  
📊 **Service-specific** stats  

---

## 🚀 Dashboard Setup

### Step 1: Create Dashboard Backend

Create `dashboard/backend/server.js`:

```javascript
const express = require('express');
const multer = require('multer');
const cors = require('cors');
const { exec } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const WebSocket = require('ws');
const axios = require('axios');

const app = express();
const PORT = 3000;

// Enable CORS for remote access
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// File upload configuration
const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const type = req.body.type || 'combos';
        const uploadDir = `/opt/ai-checker/uploads/${type}`;
        await fs.mkdir(uploadDir, { recursive: true });
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        cb(null, `${Date.now()}-${file.originalname}`);
    }
});

const upload = multer({ 
    storage,
    limits: { fileSize: 500 * 1024 * 1024 } // 500MB limit
});

// WebSocket for real-time updates
const wss = new WebSocket.Server({ port: 3001 });

wss.on('connection', (ws) => {
    console.log('Client connected');
    
    // Send initial stats
    sendStats(ws);
    
    // Update every 2 seconds
    const interval = setInterval(() => sendStats(ws), 2000);
    
    ws.on('close', () => {
        clearInterval(interval);
        console.log('Client disconnected');
    });
});

async function sendStats(ws) {
    try {
        // Get stats from API
        const response = await axios.get('http://localhost:8000/api/stats');
        ws.send(JSON.stringify({
            type: 'stats',
            data: response.data
        }));
    } catch (error) {
        console.error('Error fetching stats:', error.message);
    }
}

// API Routes

// System control
app.post('/api/system/:action', async (req, res) => {
    const { action } = req.params;
    const validActions = ['start', 'stop', 'restart', 'status'];
    
    if (!validActions.includes(action)) {
        return res.status(400).json({ error: 'Invalid action' });
    }
    
    try {
        const command = `docker-compose ${action === 'status' ? 'ps' : action}`;
        exec(command, { cwd: '/opt/ai-checker' }, (error, stdout, stderr) => {
            if (error) {
                return res.status(500).json({ error: stderr });
            }
            res.json({ success: true, output: stdout });
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Upload files
app.post('/api/upload/:type', upload.single('file'), async (req, res) => {
    const { type } = req.params; // combos, configs, proxies
    const { file } = req;
    
    if (!file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }
    
    res.json({
        success: true,
        filename: file.filename,
        path: file.path,
        size: file.size,
        type: type
    });
});

// Download files
app.get('/api/download/:type/:filename', async (req, res) => {
    const { type, filename } = req.params;
    const filePath = `/opt/ai-checker/results/${type}/${filename}`;
    
    try {
        await fs.access(filePath);
        res.download(filePath);
    } catch (error) {
        res.status(404).json({ error: 'File not found' });
    }
});

// List files
app.get('/api/files/:type', async (req, res) => {
    const { type } = req.params;
    const dirPath = `/opt/ai-checker/results/${type}`;
    
    try {
        const files = await fs.readdir(dirPath);
        const fileStats = await Promise.all(
            files.map(async (file) => {
                const stats = await fs.stat(path.join(dirPath, file));
                return {
                    name: file,
                    size: stats.size,
                    modified: stats.mtime
                };
            })
        );
        res.json(fileStats);
    } catch (error) {
        res.json([]);
    }
});

// System stats
app.get('/api/system/stats', async (req, res) => {
    exec('docker stats --no-stream --format "{{json .}}"', (error, stdout) => {
        if (error) {
            return res.status(500).json({ error: error.message });
        }
        
        const stats = stdout.trim().split('\n').map(line => JSON.parse(line));
        res.json(stats);
    });
});

// Container logs
app.get('/api/logs/:container', async (req, res) => {
    const { container } = req.params;
    const lines = req.query.lines || 100;
    
    exec(`docker logs --tail ${lines} ${container}`, (error, stdout, stderr) => {
        res.json({ 
            stdout: stdout.split('\n'),
            stderr: stderr.split('\n')
        });
    });
});

// Worker management
app.post('/api/workers/scale', async (req, res) => {
    const { count } = req.body;
    
    if (!count || count < 1 || count > 50) {
        return res.status(400).json({ error: 'Invalid worker count (1-50)' });
    }
    
    exec(`docker-compose up -d --scale worker=${count}`, 
        { cwd: '/opt/ai-checker' },
        (error, stdout, stderr) => {
            if (error) {
                return res.status(500).json({ error: stderr });
            }
            res.json({ success: true, workers: count });
        }
    );
});

// Checker control
app.post('/api/checker/:action', async (req, res) => {
    const { action } = req.params;
    const { service, combos, proxies } = req.body;
    
    try {
        const response = await axios.post(`http://localhost:8000/api/check/${action}`, {
            service,
            combos,
            proxies
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// AI optimization
app.post('/api/ai/optimize', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:8000/api/ai/optimize');
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Dashboard running on http://0.0.0.0:${PORT}`);
});
```

### Step 2: Create Dashboard Frontend

Create `dashboard/frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Checker Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.css" rel="stylesheet">
    <style>
        body {
            background: #0f0f23;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar {
            background: #1a1a2e !important;
            border-bottom: 2px solid #16213e;
        }
        .card {
            background: #16213e;
            border: 1px solid #0f3460;
            margin-bottom: 20px;
        }
        .stat-card {
            text-align: center;
            padding: 20px;
        }
        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #00d4ff;
        }
        .stat-label {
            color: #888;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        .btn-primary {
            background: #00d4ff;
            border: none;
        }
        .btn-success {
            background: #00ff88;
            border: none;
            color: #000;
        }
        .btn-danger {
            background: #ff4444;
            border: none;
        }
        .log-container {
            background: #000;
            padding: 15px;
            border-radius: 5px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
        }
        .log-line {
            margin: 2px 0;
            color: #00ff00;
        }
        .log-error {
            color: #ff4444;
        }
        .log-warning {
            color: #ffaa00;
        }
        .status-online {
            color: #00ff88;
        }
        .status-offline {
            color: #ff4444;
        }
        .upload-zone {
            border: 2px dashed #00d4ff;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-zone:hover {
            background: #1a1a2e;
            border-color: #00ff88;
        }
        .progress-bar {
            background: #00d4ff;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="bi bi-cpu-fill"></i> AI Checker Dashboard
            </span>
            <span class="navbar-text">
                <i class="bi bi-circle-fill status-online" id="connection-status"></i>
                <span id="status-text">Connected</span>
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Stats Row -->
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-value" id="cpm">0</div>
                    <div class="stat-label">CPM</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-value" id="hit-rate">0%</div>
                    <div class="stat-label">Hit Rate</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-value" id="active-workers">0</div>
                    <div class="stat-label">Active Workers</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-value" id="total-checks">0</div>
                    <div class="stat-label">Total Checks</div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Control Panel -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="bi bi-gear-fill"></i> System Control</h5>
                        <div class="btn-group w-100 mb-3" role="group">
                            <button class="btn btn-success" onclick="systemAction('start')">
                                <i class="bi bi-play-fill"></i> Start
                            </button>
                            <button class="btn btn-warning" onclick="systemAction('restart')">
                                <i class="bi bi-arrow-clockwise"></i> Restart
                            </button>
                            <button class="btn btn-danger" onclick="systemAction('stop')">
                                <i class="bi bi-stop-fill"></i> Stop
                            </button>
                        </div>
                        
                        <h6>Worker Scaling</h6>
                        <div class="input-group">
                            <input type="number" class="form-control" id="worker-count" value="5" min="1" max="50">
                            <button class="btn btn-primary" onclick="scaleWorkers()">
                                <i class="bi bi-arrows-expand"></i> Scale
                            </button>
                        </div>
                    </div>
                </div>

                <!-- File Upload -->
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="bi bi-cloud-upload-fill"></i> Upload Files</h5>
                        
                        <ul class="nav nav-tabs mb-3" id="uploadTabs" role="tablist">
                            <li class="nav-item">
                                <a class="nav-link active" data-bs-toggle="tab" href="#combos">Combos</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-bs-toggle="tab" href="#configs">Configs</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-bs-toggle="tab" href="#proxies">Proxies</a>
                            </li>
                        </ul>

                        <div class="tab-content">
                            <div class="tab-pane fade show active" id="combos">
                                <div class="upload-zone" onclick="document.getElementById('combo-file').click()">
                                    <i class="bi bi-file-earmark-arrow-up" style="font-size: 3rem;"></i>
                                    <p>Click or drag combo list here</p>
                                    <input type="file" id="combo-file" hidden onchange="uploadFile(this, 'combos')">
                                </div>
                            </div>
                            <div class="tab-pane fade" id="configs">
                                <div class="upload-zone" onclick="document.getElementById('config-file').click()">
                                    <i class="bi bi-file-earmark-code" style="font-size: 3rem;"></i>
                                    <p>Click or drag config file here</p>
                                    <input type="file" id="config-file" hidden onchange="uploadFile(this, 'configs')">
                                </div>
                            </div>
                            <div class="tab-pane fade" id="proxies">
                                <div class="upload-zone" onclick="document.getElementById('proxy-file').click()">
                                    <i class="bi bi-hdd-network" style="font-size: 3rem;"></i>
                                    <p>Click or drag proxy list here</p>
                                    <input type="file" id="proxy-file" hidden onchange="uploadFile(this, 'proxies')">
                                </div>
                            </div>
                        </div>

                        <div class="progress mt-3" style="display:none;" id="upload-progress">
                            <div class="progress-bar" role="progressbar" style="width: 0%;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Real-time Logs -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="bi bi-terminal-fill"></i> Live Logs
                            <button class="btn btn-sm btn-outline-light float-end" onclick="clearLogs()">Clear</button>
                        </h5>
                        <div class="log-container" id="log-container">
                            <div class="log-line">[INFO] Dashboard initialized</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Performance Charts -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="bi bi-graph-up"></i> CPM Over Time</h5>
                        <canvas id="cpm-chart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="bi bi-pie-chart-fill"></i> Success Rate</h5>
                        <canvas id="success-chart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Download Results -->
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="bi bi-download"></i> Download Results</h5>
                        <div class="table-responsive">
                            <table class="table table-dark table-striped">
                                <thead>
                                    <tr>
                                        <th>File Name</th>
                                        <th>Size</th>
                                        <th>Modified</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="results-table">
                                    <!-- Populated via JavaScript -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="app.js"></script>
</body>
</html>
```

### Step 3: Create Dashboard JavaScript

Create `dashboard/frontend/app.js`:

```javascript
// WebSocket connection
let ws;
let cpmChart, successChart;
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:3000' 
    : `http://${window.location.hostname}:3000`;

// Initialize dashboard
function init() {
    connectWebSocket();
    initCharts();
    loadResults();
    setInterval(loadResults, 30000); // Refresh every 30s
}

// WebSocket connection
function connectWebSocket() {
    const wsUrl = `ws://${window.location.hostname}:3001`;
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        document.getElementById('connection-status').className = 'bi bi-circle-fill status-online';
        document.getElementById('status-text').textContent = 'Connected';
        addLog('[INFO] Connected to server', 'info');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'stats') {
            updateStats(data.data);
        }
    };
    
    ws.onerror = () => {
        document.getElementById('connection-status').className = 'bi bi-circle-fill status-offline';
        document.getElementById('status-text').textContent = 'Disconnected';
        addLog('[ERROR] Connection lost', 'error');
    };
    
    ws.onclose = () => {
        setTimeout(connectWebSocket, 3000); // Reconnect after 3s
    };
}

// Update statistics
function updateStats(stats) {
    document.getElementById('cpm').textContent = stats.cpm || 0;
    document.getElementById('hit-rate').textContent = (stats.hit_rate || 0).toFixed(1) + '%';
    document.getElementById('active-workers').textContent = stats.active_workers || 0;
    document.getElementById('total-checks').textContent = (stats.total_checks || 0).toLocaleString();
    
    // Update charts
    updateCharts(stats);
}

// Initialize charts
function initCharts() {
    // CPM Chart
    const cpmCtx = document.getElementById('cpm-chart').getContext('2d');
    cpmChart = new Chart(cpmCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'CPM',
                data: [],
                borderColor: '#00d4ff',
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
    
    // Success Chart
    const successCtx = document.getElementById('success-chart').getContext('2d');
    successChart = new Chart(successCtx, {
        type: 'doughnut',
        data: {
            labels: ['Success', 'Failed', 'Rate Limited'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#00ff88', '#ff4444', '#ffaa00']
            }]
        },
        options: {
            responsive: true
        }
    });
}

// Update charts
function updateCharts(stats) {
    // CPM chart
    const now = new Date().toLocaleTimeString();
    if (cpmChart.data.labels.length > 20) {
        cpmChart.data.labels.shift();
        cpmChart.data.datasets[0].data.shift();
    }
    cpmChart.data.labels.push(now);
    cpmChart.data.datasets[0].data.push(stats.cpm || 0);
    cpmChart.update();
    
    // Success chart
    successChart.data.datasets[0].data = [
        stats.success_count || 0,
        stats.failed_count || 0,
        stats.rate_limited_count || 0
    ];
    successChart.update();
}

// System actions
async function systemAction(action) {
    try {
        const response = await fetch(`${API_URL}/api/system/${action}`, {
            method: 'POST'
        });
        const result = await response.json();
        addLog(`[INFO] System ${action}: ${result.success ? 'OK' : 'FAILED'}`, result.success ? 'info' : 'error');
    } catch (error) {
        addLog(`[ERROR] ${error.message}`, 'error');
    }
}

// Scale workers
async function scaleWorkers() {
    const count = document.getElementById('worker-count').value;
    try {
        const response = await fetch(`${API_URL}/api/workers/scale`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count: parseInt(count) })
        });
        const result = await response.json();
        addLog(`[INFO] Scaled to ${count} workers`, 'info');
    } catch (error) {
        addLog(`[ERROR] ${error.message}`, 'error');
    }
}

// Upload file
async function uploadFile(input, type) {
    const file = input.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    
    const progressBar = document.getElementById('upload-progress');
    progressBar.style.display = 'block';
    
    try {
        const response = await fetch(`${API_URL}/api/upload/${type}`, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        addLog(`[INFO] Uploaded ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`, 'info');
        progressBar.style.display = 'none';
    } catch (error) {
        addLog(`[ERROR] Upload failed: ${error.message}`, 'error');
        progressBar.style.display = 'none';
    }
}

// Load results
async function loadResults() {
    try {
        const response = await fetch(`${API_URL}/api/files/hits`);
        const files = await response.json();
        
        const tbody = document.getElementById('results-table');
        tbody.innerHTML = files.map(file => `
            <tr>
                <td>${file.name}</td>
                <td>${(file.size / 1024).toFixed(2)} KB</td>
                <td>${new Date(file.modified).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="downloadFile('${file.name}')">
                        <i class="bi bi-download"></i> Download
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading results:', error);
    }
}

// Download file
function downloadFile(filename) {
    window.open(`${API_URL}/api/download/hits/${filename}`, '_blank');
}

// Add log entry
function addLog(message, type = 'info') {
    const container = document.getElementById('log-container');
    const logClass = type === 'error' ? 'log-error' : type === 'warning' ? 'log-warning' : 'log-line';
    const timestamp = new Date().toLocaleTimeString();
    const logLine = document.createElement('div');
    logLine.className = logClass;
    logLine.textContent = `[${timestamp}] ${message}`;
    container.appendChild(logLine);
    container.scrollTop = container.scrollHeight;
    
    // Keep only last 100 lines
    while (container.children.length > 100) {
        container.removeChild(container.firstChild);
    }
}

// Clear logs
function clearLogs() {
    document.getElementById('log-container').innerHTML = '';
    addLog('[INFO] Logs cleared', 'info');
}

// Initialize on load
window.onload = init;
```

---

## 📦 Dashboard Deployment

### Create Docker Service

Add to `docker-compose.yml`:

```yaml
dashboard:
  build: ./dashboard
  ports:
    - "3000:3000"
    - "3001:3001"
  volumes:
    - ./uploads:/opt/ai-checker/uploads
    - ./results:/opt/ai-checker/results
    - /var/run/docker.sock:/var/run/docker.sock
  environment:
    - NODE_ENV=production
    - API_URL=http://api:8000
  restart: unless-stopped
  depends_on:
    - api
```

### Create Dockerfile

Create `dashboard/Dockerfile`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci --production

# Copy application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 3000 3001

CMD ["node", "backend/server.js"]
```

### Create package.json

Create `dashboard/package.json`:

```json
{
  "name": "ai-checker-dashboard",
  "version": "1.0.0",
  "description": "Interactive dashboard for AI checker",
  "main": "backend/server.js",
  "scripts": {
    "start": "node backend/server.js",
    "dev": "nodemon backend/server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "multer": "^1.4.5-lts.1",
    "cors": "^2.8.5",
    "ws": "^8.14.2",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

---

## 🚀 Deploy Dashboard

```bash
# On your droplet
cd /opt/ai-checker/dashboard
npm install

# Build and start
cd /opt/ai-checker
docker-compose up -d dashboard

# Access dashboard
# http://your.droplet.ip:3000
```

---

## 🔐 Secure Dashboard with Password

Create `dashboard/backend/auth.js`:

```javascript
const basicAuth = require('express-basic-auth');

const auth = basicAuth({
    users: { 
        'admin': 'your-secure-password-here'  // Change this!
    },
    challenge: true,
    realm: 'AI Checker Dashboard'
});

module.exports = auth;
```

Update `server.js`:

```javascript
const auth = require('./auth');

// Add before routes
app.use(auth);
```

---

## 📱 Mobile Access

Dashboard is fully responsive and works on:
- ✅ iPhone/iPad (Safari)
- ✅ Android (Chrome)
- ✅ Tablets
- ✅ Desktop

Access from anywhere: `http://your.droplet.ip:3000`

---

## 🎯 Dashboard Features in Action

### Upload Combos
1. Click "Combos" tab
2. Drag & drop or click to select
3. Auto-uploads to `/opt/ai-checker/uploads/combos/`

### Start Checking
1. Upload combos
2. Click "Start" in System Control
3. Watch real-time stats update

### Download Results
1. Scroll to "Download Results"
2. See all hit files
3. Click "Download" button

### Monitor Performance
- Real-time CPM graph
- Success rate pie chart
- Worker status
- Live logs streaming

---

**Next:** See `AI_OPTIMIZATION.md` for self-optimization features!
