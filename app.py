#!/usr/bin/env python3
"""
Flask Web Application for Tamil Cinema News Publisher
Provides API endpoints to trigger article publishing and monitoring
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime
import pytz
from flask import Flask, jsonify, request, render_template_string
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env.env')

# Import our modules
from main import NewsPublisher
from db import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cineulagam_publisher.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variables for status tracking
publisher_status = {
    'is_running': False,
    'last_run': None,
    'last_error': None,
    'articles_published': 0,
    'current_status': 'idle'
}

# Database manager for stats
db_manager = DatabaseManager()

# HTML template for the dashboard
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tamil Cinema News Publisher Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        .content {
            padding: 30px;
        }
        .status-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }
        .status-running {
            border-left-color: #27ae60;
        }
        .status-error {
            border-left-color: #e74c3c;
        }
        .btn {
            background: #3498db;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            transition: background 0.3s ease;
        }
        .btn:hover {
            background: #2980b9;
        }
        .btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
        .btn-danger {
            background: #e74c3c;
        }
        .btn-danger:hover {
            background: #c0392b;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .stat-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #3498db;
        }
        .log-container {
            background: #2c3e50;
            color: #ecf0f1;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Tamil Cinema News Publisher</h1>
            <p>Automated News Publishing Dashboard</p>
        </div>
        
        <div class="content">
            <div class="status-card" id="statusCard">
                <h3>Publisher Status</h3>
                <p><strong>Status:</strong> <span id="status">Loading...</span></p>
                <p><strong>Last Run:</strong> <span id="lastRun">Never</span></p>
                <p><strong>Articles Published:</strong> <span id="articlesCount">0</span></p>
                {% if publisher_status.last_error %}
                <p><strong>Last Error:</strong> <span style="color: #e74c3c;">{{ publisher_status.last_error }}</span></p>
                {% endif %}
            </div>
            
            <div>
                <button class="btn" id="startBtn" onclick="startPublisher()">Start Publisher</button>
                <button class="btn btn-danger" id="stopBtn" onclick="stopPublisher()" disabled>Stop Publisher</button>
                <button class="btn" onclick="refreshStatus()">Refresh Status</button>
                <button class="btn" onclick="getStats()">Get Statistics</button>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <!-- Stats will be loaded here -->
            </div>
            
            <div class="log-container" id="logContainer">
                <h4>Recent Activity</h4>
                <div id="logs">Loading logs...</div>
            </div>
        </div>
    </div>

    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = data.current_status;
                    document.getElementById('lastRun').textContent = data.last_run || 'Never';
                    document.getElementById('articlesCount').textContent = data.articles_published;
                    
                    const statusCard = document.getElementById('statusCard');
                    statusCard.className = 'status-card';
                    if (data.is_running) {
                        statusCard.classList.add('status-running');
                        document.getElementById('startBtn').disabled = true;
                        document.getElementById('stopBtn').disabled = false;
                    } else {
                        document.getElementById('startBtn').disabled = false;
                        document.getElementById('stopBtn').disabled = true;
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function startPublisher() {
            fetch('/api/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    updateStatus();
                })
                .catch(error => console.error('Error:', error));
        }
        
        function stopPublisher() {
            fetch('/api/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    updateStatus();
                })
                .catch(error => console.error('Error:', error));
        }
        
        function refreshStatus() {
            updateStatus();
            getStats();
        }
        
        function getStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    const statsGrid = document.getElementById('statsGrid');
                    statsGrid.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-number">${data.total_articles || 0}</div>
                            <div>Total Articles</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.today_articles || 0}</div>
                            <div>Today's Articles</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.last_article ? 'Yes' : 'No'}</div>
                            <div>Last Article</div>
                        </div>
                    `;
                })
                .catch(error => console.error('Error:', error));
        }
        
        // Update status every 5 seconds
        setInterval(updateStatus, 5000);
        
        // Initial load
        updateStatus();
        getStats();
    </script>
</body>
</html>
'''

def run_publisher():
    """Run the publisher in a separate thread"""
    global publisher_status
    
    try:
        publisher_status['is_running'] = True
        publisher_status['current_status'] = 'running'
        publisher_status['last_error'] = None
        
        logger.info("Starting publisher from API call")
        publisher = NewsPublisher()
        publisher.run_pipeline()
        
        publisher_status['is_running'] = False
        publisher_status['current_status'] = 'completed'
        publisher_status['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        publisher_status['articles_published'] += 1
        
        logger.info("Publisher completed successfully")
        
    except Exception as e:
        publisher_status['is_running'] = False
        publisher_status['current_status'] = 'error'
        publisher_status['last_error'] = str(e)
        logger.error(f"Publisher failed: {str(e)}")

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_TEMPLATE, publisher_status=publisher_status)

@app.route('/api/status')
def get_status():
    """Get current publisher status"""
    return jsonify(publisher_status)

@app.route('/api/start', methods=['POST','GET'])
def start_publisher():
    """Start the publisher"""
    global publisher_status
    # Handle POST request - start the publisher
    if publisher_status['is_running']:
        return jsonify({
            'success': False,
            'message': 'Publisher is already running'
        }), 400
    # Handle GET request - return HTML with current date and time

   
    
    # Start publisher in a separate thread
    thread = threading.Thread(target=run_publisher)
    thread.daemon = True
    thread.start()
    
    if request.method == 'GET':
        # Get UK time
        uk_tz = pytz.timezone('Europe/London')
        current_time = datetime.now(uk_tz).strftime('%Y-%m-%d %H:%M:%S')
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{current_time} - Extractor Started</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    padding: 40px;
                    text-align: center;
                    max-width: 600px;
                }}
                h1 {{
                    color: #2c3e50;
                    margin-bottom: 20px;
                }}
                .status {{
                    background: #27ae60;
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-size: 18px;
                }}
                .info {{
                    color: #7f8c8d;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{current_time} - Extractor Started</h1>
                <div class="status">Publisher Status: Ready to Start</div>
                <p>Use POST method to actually start the publisher</p>
                <div class="info">
                    <p>This page shows the current date and time when accessed via GET request</p>
                </div>
            </div>
        </body>
        </html>
        '''
        return html_content
    
    return jsonify({
        'success': True,
        'message': 'Publisher started successfully'
    })

@app.route('/api/stop', methods=['POST'])
def stop_publisher():
    """Stop the publisher (if running)"""
    global publisher_status
    
    if not publisher_status['is_running']:
        return jsonify({
            'success': False,
            'message': 'Publisher is not running'
        }), 400
    
    publisher_status['is_running'] = False
    publisher_status['current_status'] = 'stopped'
    
    return jsonify({
        'success': True,
        'message': 'Publisher stopped successfully'
    })

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    try:
        if db_manager.collection is None:
            return jsonify({
                'success': False,
                'message': 'Database not connected'
            }), 500
        
        stats = db_manager.get_stats()
        return jsonify({
            'success': True,
            'total_articles': stats.get('total_articles', 0),
            'today_articles': stats.get('today_articles', 0),
            'last_article': stats.get('most_recent'),
            'last_article_date': stats.get('most_recent_date')
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting stats: {str(e)}'
        }), 500

@app.route('/api/articles')
def get_articles():
    """Get list of published articles"""
    try:
        if db_manager.collection is None:
            return jsonify({
                'success': False,
                'message': 'Database not connected'
            }), 500
        
        limit = request.args.get('limit', 10, type=int)
        articles = db_manager.get_posted_articles(limit)
        
        return jsonify({
            'success': True,
            'articles': articles,
            'count': len(articles)
        })
    except Exception as e:
        logger.error(f"Error getting articles: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting articles: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database_connected': db_manager.collection is not None,
        'publisher_running': publisher_status['is_running']
    })

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    try:
        log_file = 'cineulagam_publisher.log'
        if not os.path.exists(log_file):
            return jsonify({
                'success': True,
                'logs': 'No log file found'
            })
        
        # Read last 50 lines
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-50:] if len(lines) > 50 else lines
        
        return jsonify({
            'success': True,
            'logs': ''.join(recent_lines)
        })
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error reading logs: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Initialize database connection
    if db_manager.collection is None:
        logger.error("Failed to connect to database. Please check your MongoDB configuration.")
        sys.exit(1)
    
    logger.info("Starting Tamil Cinema News Publisher Flask App")
    logger.info("Dashboard available at: http://localhost:5000")
    logger.info("API endpoints available at: http://localhost:5000/api/")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5000,
        debug=False,  # Set to False for production
        threaded=True
    )
