/**
 * Email Leak Checker Dashboard
 * Real-time scanning and results visualization
 */

const API_URL = 'http://localhost:8000';
let ws = null;
let scanResults = [];
let charts = {};

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    initializeWebSocket();
    initializeCharts();
    initializeEventListeners();
    loadStats();
});

// ==================== WEBSOCKET ====================

function initializeWebSocket() {
    ws = new WebSocket('ws://localhost:3001');
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        addActivity('System', 'Dashboard connected', 'success');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addActivity('System', 'Connection error', 'danger');
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected. Reconnecting...');
        setTimeout(initializeWebSocket, 3000);
    };
}

function handleWebSocketMessage(data) {
    if (data.type === 'scan_update') {
        updateScanProgress(data);
    } else if (data.type === 'scan_complete') {
        handleScanComplete(data);
    } else if (data.type === 'stats') {
        updateStats(data.stats);
    }
}

// ==================== EVENT LISTENERS ====================

function initializeEventListeners() {
    // Single scan
    document.getElementById('scanButton').addEventListener('click', startSingleScan);
    document.getElementById('singleEmail').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') startSingleScan();
    });
    
    // Bulk scan
    document.getElementById('bulkScanButton').addEventListener('click', startBulkScan);
    document.getElementById('uploadZone').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    document.getElementById('fileInput').addEventListener('change', handleFileUpload);
    
    // Drag and drop
    const uploadZone = document.getElementById('uploadZone');
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    uploadZone.addEventListener('drop', handleFileDrop);
    
    // Export
    document.getElementById('exportCSV').addEventListener('click', () => exportResults('csv'));
    document.getElementById('exportJSON').addEventListener('click', () => exportResults('json'));
    
    // Filter
    document.getElementById('filterRisk').addEventListener('change', filterResults);
    document.getElementById('searchEmail').addEventListener('input', filterResults);
}

// ==================== SINGLE SCAN ====================

async function startSingleScan() {
    const email = document.getElementById('singleEmail').value.trim();
    
    if (!email || !isValidEmail(email)) {
        showAlert('Please enter a valid email address', 'warning');
        return;
    }
    
    const button = document.getElementById('scanButton');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Scanning...';
    
    // Show progress
    document.getElementById('scanProgress').classList.remove('d-none');
    document.getElementById('singleResult').classList.add('d-none');
    
    addActivity('Scan', `Started scan for ${email}`, 'info');
    
    try {
        const response = await fetch(`${API_URL}/api/leak-check/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displaySingleResult(result.data);
            scanResults.push(result.data);
            updateCharts();
            addActivity('Scan', `Completed for ${email}`, 'success');
        } else {
            throw new Error(result.message || 'Scan failed');
        }
    } catch (error) {
        console.error('Scan error:', error);
        showAlert(`Scan failed: ${error.message}`, 'danger');
        addActivity('Scan', `Failed for ${email}`, 'danger');
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-search"></i> Scan Email';
        document.getElementById('scanProgress').classList.add('d-none');
    }
}

function displaySingleResult(data) {
    const resultDiv = document.getElementById('singleResult');
    const riskClass = data.risk_level.toLowerCase();
    
    const html = `
        <div class="card bg-dark border-${getRiskColor(data.risk_level)}">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-envelope-at"></i> ${data.email}</span>
                <span class="badge bg-${getRiskColor(data.risk_level)} fs-6">
                    ${data.risk_level} RISK
                </span>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h2 class="risk-${riskClass} mb-0">${data.risk_score}/100</h2>
                        <p class="text-muted">Risk Score</p>
                    </div>
                    <div class="col-md-6">
                        <h2 class="mb-0">${data.sources_found}/${data.total_sources}</h2>
                        <p class="text-muted">Sources Found Leaks</p>
                    </div>
                </div>
                
                ${data.breaches && data.breaches.length > 0 ? `
                    <div class="mb-3">
                        <h6><i class="bi bi-database-exclamation"></i> Breaches Found (${data.breaches.length})</h6>
                        <div style="max-height: 200px; overflow-y: auto;">
                            ${data.breaches.map(b => `
                                <div class="breach-card">
                                    <strong>${b.name}</strong>
                                    <small class="text-muted d-block">via ${b.source}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div>
                    <h6><i class="bi bi-shield-check"></i> Recommendations</h6>
                    <ul class="list-unstyled">
                        ${data.recommendations.map(r => `
                            <li class="mb-2">
                                <i class="bi bi-check-circle text-success"></i> ${r}
                            </li>
                        `).join('')}
                    </ul>
                </div>
                
                <button class="btn btn-sm btn-outline-info w-100 mt-3" onclick="showDetailedResults('${data.email}')">
                    <i class="bi bi-eye"></i> View Detailed Results
                </button>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
    resultDiv.classList.remove('d-none');
}

// ==================== BULK SCAN ====================

async function startBulkScan() {
    const bulkText = document.getElementById('bulkEmails').value.trim();
    const emails = bulkText.split('\n').map(e => e.trim()).filter(e => e && isValidEmail(e));
    
    if (emails.length === 0) {
        showAlert('Please provide at least one valid email', 'warning');
        return;
    }
    
    if (emails.length > 1000) {
        showAlert('Maximum 1000 emails per bulk scan', 'warning');
        return;
    }
    
    const maxConcurrent = parseInt(document.getElementById('maxConcurrent').value);
    const button = document.getElementById('bulkScanButton');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Scanning...';
    
    // Show progress
    document.getElementById('bulkProgress').classList.remove('d-none');
    document.getElementById('bulkTotal').textContent = emails.length;
    document.getElementById('bulkProcessed').textContent = '0';
    
    addActivity('Bulk Scan', `Started scanning ${emails.length} emails`, 'info');
    
    try {
        const response = await fetch(`${API_URL}/api/leak-check/bulk`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                emails,
                max_concurrent: maxConcurrent
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.results) {
                // Immediate results (small batch)
                scanResults.push(...result.results);
                updateResultsTable();
                updateCharts();
                showAlert(`Bulk scan completed! ${result.processed} emails scanned.`, 'success');
                addActivity('Bulk Scan', `Completed ${result.processed} emails`, 'success');
                
                // Show summary
                const summary = result.summary;
                showAlert(`Found: ${summary.critical} Critical, ${summary.high} High, ${summary.medium} Medium, ${summary.low} Low`, 'info');
            } else {
                // Background job (large batch)
                showAlert(`Bulk scan started! Job ID: ${result.job_id}`, 'info');
                monitorBulkJob(result.job_id);
            }
        } else {
            throw new Error(result.message || 'Bulk scan failed');
        }
    } catch (error) {
        console.error('Bulk scan error:', error);
        showAlert(`Bulk scan failed: ${error.message}`, 'danger');
        addActivity('Bulk Scan', 'Failed', 'danger');
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-rocket-takeoff"></i> Start Bulk Scan';
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('bulkEmails').value = e.target.result;
        };
        reader.readAsText(file);
    }
}

function handleFileDrop(event) {
    event.preventDefault();
    const uploadZone = document.getElementById('uploadZone');
    uploadZone.classList.remove('dragover');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('bulkEmails').value = e.target.result;
        };
        reader.readAsText(file);
    }
}

// ==================== RESULTS ====================

function updateResultsTable() {
    const container = document.getElementById('resultsTable');
    
    if (scanResults.length === 0) {
        container.innerHTML = '<p class="text-center text-muted mt-4">No results yet. Start a scan!</p>';
        return;
    }
    
    const html = scanResults.map(result => `
        <div class="result-row ${result.risk_level.toLowerCase()}" data-email="${result.email}" data-risk="${result.risk_level}">
            <div class="row align-items-center">
                <div class="col-md-4">
                    <strong>${result.email}</strong>
                    <small class="text-muted d-block">${new Date(result.checked_at).toLocaleString()}</small>
                </div>
                <div class="col-md-2">
                    <span class="badge bg-${getRiskColor(result.risk_level)}">${result.risk_level}</span>
                </div>
                <div class="col-md-2">
                    <span class="risk-${result.risk_level.toLowerCase()}">${result.risk_score}/100</span>
                </div>
                <div class="col-md-2">
                    <small>${result.breaches ? result.breaches.length : 0} breaches</small>
                </div>
                <div class="col-md-2 text-end">
                    <button class="btn btn-sm btn-outline-info" onclick="showDetailedResults('${result.email}')">
                        <i class="bi bi-eye"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function filterResults() {
    const riskFilter = document.getElementById('filterRisk').value;
    const searchTerm = document.getElementById('searchEmail').value.toLowerCase();
    
    const rows = document.querySelectorAll('.result-row');
    rows.forEach(row => {
        const email = row.dataset.email.toLowerCase();
        const risk = row.dataset.risk;
        
        const matchesRisk = !riskFilter || risk === riskFilter;
        const matchesSearch = !searchTerm || email.includes(searchTerm);
        
        row.style.display = (matchesRisk && matchesSearch) ? 'block' : 'none';
    });
}

function showDetailedResults(email) {
    const result = scanResults.find(r => r.email === email);
    if (!result) return;
    
    // Show modal with detailed results
    const modal = new bootstrap.Modal(document.createElement('div'));
    // TODO: Implement detailed results modal
    console.log('Detailed results for:', email, result);
}

// ==================== CHARTS ====================

function initializeCharts() {
    // Risk Distribution Pie Chart
    const riskCtx = document.getElementById('riskChart').getContext('2d');
    charts.risk = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: ['#ff0040', '#ff6b00', '#ffc107', '#00d4aa'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#fff' }
                }
            }
        }
    });
    
    // Scan History Line Chart
    const historyCtx = document.getElementById('historyChart').getContext('2d');
    charts.history = new Chart(historyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Scans',
                data: [],
                borderColor: '#e94560',
                backgroundColor: 'rgba(233, 69, 96, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                x: { 
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            }
        }
    });
}

function updateCharts() {
    // Update risk distribution
    const riskCounts = {
        CRITICAL: 0,
        HIGH: 0,
        MEDIUM: 0,
        LOW: 0
    };
    
    scanResults.forEach(result => {
        riskCounts[result.risk_level]++;
    });
    
    charts.risk.data.datasets[0].data = [
        riskCounts.CRITICAL,
        riskCounts.HIGH,
        riskCounts.MEDIUM,
        riskCounts.LOW
    ];
    charts.risk.update();
    
    // Update history (last 24 hours)
    // TODO: Implement time-based history
}

// ==================== STATS ====================

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/api/leak-check/stats`);
        const result = await response.json();
        
        if (result.success) {
            updateStats(result.stats);
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

function updateStats(stats) {
    document.getElementById('totalScans').textContent = stats.total_scans || scanResults.length;
    document.getElementById('leaksFound').textContent = scanResults.filter(r => r.sources_found > 0).length;
    document.getElementById('totalBreaches').textContent = 
        scanResults.reduce((sum, r) => sum + (r.breaches ? r.breaches.length : 0), 0);
    
    const avgScore = scanResults.length > 0 
        ? Math.round(scanResults.reduce((sum, r) => sum + r.risk_score, 0) / scanResults.length)
        : 0;
    document.getElementById('avgRiskScore').textContent = avgScore;
    document.getElementById('scanCount').textContent = scanResults.length;
}

// ==================== ACTIVITY FEED ====================

function addActivity(type, message, level = 'info') {
    const feed = document.getElementById('activityFeed');
    const time = new Date().toLocaleTimeString();
    
    const icon = {
        success: 'check-circle',
        danger: 'x-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    }[level] || 'info-circle';
    
    const item = document.createElement('div');
    item.className = `mb-2 p-2 border-start border-${level} border-3`;
    item.innerHTML = `
        <small class="text-muted">${time}</small>
        <div><i class="bi bi-${icon} text-${level}"></i> <strong>${type}:</strong> ${message}</div>
    `;
    
    feed.prepend(item);
    
    // Keep only last 50 items
    while (feed.children.length > 50) {
        feed.removeChild(feed.lastChild);
    }
}

// ==================== EXPORT ====================

async function exportResults(format) {
    try {
        const response = await fetch(`${API_URL}/api/leak-check/export/${format}`);
        
        if (format === 'csv') {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `leak_scan_results_${Date.now()}.csv`;
            a.click();
        } else if (format === 'json') {
            const data = await response.json();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `leak_scan_results_${Date.now()}.json`;
            a.click();
        }
        
        showAlert(`Results exported as ${format.toUpperCase()}`, 'success');
    } catch (error) {
        showAlert(`Export failed: ${error.message}`, 'danger');
    }
}

// ==================== UTILITIES ====================

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function getRiskColor(level) {
    const colors = {
        CRITICAL: 'danger',
        HIGH: 'warning',
        MEDIUM: 'info',
        LOW: 'success'
    };
    return colors[level] || 'secondary';
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function updateScanProgress(data) {
    document.getElementById('currentSource').textContent = data.source;
    document.getElementById('progressPercent').textContent = data.progress;
    document.getElementById('progressBar').style.width = `${data.progress}%`;
}

function handleScanComplete(data) {
    console.log('Scan completed:', data);
}
