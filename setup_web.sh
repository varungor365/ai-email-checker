#!/bin/bash
# Fix Nginx configuration and set up web dashboard

echo "🌐 Setting up Nginx and Web Dashboard..."

# Install Nginx if not present
apt-get install -y nginx

# Create web dashboard directory
mkdir -p /var/www/ai-checker

# Create simple status dashboard
cat > /var/www/ai-checker/index.html << 'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Email Checker - Live Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 40px 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 15px;
            margin-bottom: 30px;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { font-size: 1.2em; opacity: 0.9; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h2 {
            font-size: 1.3em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4ade80;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .stat:last-child { border-bottom: none; }
        .value {
            font-weight: bold;
            color: #4ade80;
        }
        .commands {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .command {
            background: rgba(255,255,255,0.1);
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 8px;
            font-family: monospace;
        }
        .command-name {
            color: #fbbf24;
            font-weight: bold;
        }
        .btn {
            display: inline-block;
            background: #4ade80;
            color: #1a1a1a;
            padding: 12px 30px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px 5px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: scale(1.05); }
        .telegram-link {
            text-align: center;
            margin: 30px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Email Checker</h1>
            <p class="subtitle">Autonomous Self-Learning Email Validation System</p>
        </div>

        <div class="grid">
            <div class="card">
                <h2><span class="status-indicator"></span> System Status</h2>
                <div class="stat">
                    <span>Service</span>
                    <span class="value" id="service-status">Running</span>
                </div>
                <div class="stat">
                    <span>Uptime</span>
                    <span class="value" id="uptime">Loading...</span>
                </div>
                <div class="stat">
                    <span>Docker Services</span>
                    <span class="value">11 Active</span>
                </div>
                <div class="stat">
                    <span>AI Model</span>
                    <span class="value">Mistral (Ollama)</span>
                </div>
            </div>

            <div class="card">
                <h2>📊 Current Session</h2>
                <div class="stat">
                    <span>Processing Speed</span>
                    <span class="value" id="speed">100 emails/sec</span>
                </div>
                <div class="stat">
                    <span>Quality Threshold</span>
                    <span class="value">75%</span>
                </div>
                <div class="stat">
                    <span>Workers</span>
                    <span class="value">2 Active</span>
                </div>
                <div class="stat">
                    <span>Auto-Learning</span>
                    <span class="value">Enabled</span>
                </div>
            </div>

            <div class="card">
                <h2>🎯 Features</h2>
                <div class="stat">
                    <span>Smart File Detection</span>
                    <span class="value">✅</span>
                </div>
                <div class="stat">
                    <span>6-Layer Quality Validation</span>
                    <span class="value">✅</span>
                </div>
                <div class="stat">
                    <span>Real-time Notifications</span>
                    <span class="value">✅</span>
                </div>
                <div class="stat">
                    <span>Auto-Optimization</span>
                    <span class="value">✅</span>
                </div>
            </div>
        </div>

        <div class="telegram-link">
            <a href="https://t.me/ai_email_checker_bot" class="btn" target="_blank">
                📱 Open Telegram Bot
            </a>
            <a href="/api/docs" class="btn" style="background: #8b5cf6;">
                📖 API Docs
            </a>
        </div>

        <div class="card">
            <h2>💬 Telegram Bot Commands</h2>
            <div class="commands">
                <div class="command">
                    <span class="command-name">/start</span> - Welcome & bot info
                </div>
                <div class="command">
                    <span class="command-name">/help</span> - List all commands
                </div>
                <div class="command">
                    <span class="command-name">/auto_scan</span> - Start autonomous scanning
                </div>
                <div class="command">
                    <span class="command-name">/autonomous_status</span> - System status & stats
                </div>
                <div class="command">
                    <span class="command-name">/ml_status</span> - ML learning progress
                </div>
                <div class="command">
                    <span class="command-name">/quality_report</span> - Quality validation stats
                </div>
                <div class="command">
                    <span class="command-name">/train</span> - Trigger model retraining
                </div>
                <div class="command">
                    <span class="command-name">/optimize</span> - Run system optimization
                </div>
                <div class="command">
                    <span class="command-name">/pause</span> - Pause processing
                </div>
                <div class="command">
                    <span class="command-name">/resume</span> - Resume processing
                </div>
            </div>
        </div>

        <div class="card" style="margin-top: 20px; text-align: center;">
            <h2>🚀 Quick Start Guide</h2>
            <p style="margin: 15px 0; line-height: 1.6;">
                1. Open Telegram → Search <strong>@ai_email_checker_bot</strong><br>
                2. Send <span class="command-name">/start</span> to initialize<br>
                3. Upload your combo file (email:password format)<br>
                4. Bot auto-detects file type automatically<br>
                5. Send <span class="command-name">/auto_scan</span> to start<br>
                6. Get real-time updates every 60 seconds
            </p>
        </div>
    </div>

    <script>
        // Update uptime
        async function updateStatus() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                document.getElementById('uptime').textContent = data.uptime || 'Active';
                document.getElementById('service-status').textContent = 'Running';
            } catch (e) {
                document.getElementById('service-status').textContent = 'Starting...';
            }
        }
        
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
HTML

# Configure Nginx
cat > /etc/nginx/sites-available/ai-checker << 'NGINX'
server {
    listen 80;
    server_name 143.110.254.40;

    # Web Dashboard
    location / {
        root /var/www/ai-checker;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
NGINX

# Enable site
ln -sf /etc/nginx/sites-available/ai-checker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t && systemctl reload nginx

echo "✅ Web dashboard configured at http://143.110.254.40"
