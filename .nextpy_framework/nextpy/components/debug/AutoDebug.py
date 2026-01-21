"""
Auto Debug System - Automatically injects debug icon in development mode
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

def should_show_debug() -> bool:
    """Check if debug icon should be shown based on environment"""
    return (
        os.getenv("NEXTPY_DEBUG") == "true" or 
        os.getenv("DEBUG") == "true" or
        os.getenv("DEVELOPMENT") == "true" or
        "--debug" in sys.argv or
        not os.getenv("PRODUCTION")  # Default to debug in non-production
    )

def get_debug_config() -> Dict[str, Any]:
    """Get debug configuration from environment"""
    return {
        "show_debug_icon": should_show_debug(),
        "auto_capture_errors": os.getenv("NEXTPY_DEBUG_CAPTURE_ERRORS", "true").lower() == "true",
        "show_performance": os.getenv("NEXTPY_DEBUG_PERFORMANCE", "true").lower() == "true",
        "show_console": os.getenv("NEXTPY_DEBUG_CONSOLE", "true").lower() == "true",
        "position": os.getenv("NEXTPY_DEBUG_POSITION", "bottom-right"),
        "theme": os.getenv("NEXTPY_DEBUG_THEME", "dark")
    }

def inject_debug_icon(html_content: str, page_props: Dict[str, Any] = None) -> str:
    """Inject debug icon and scripts into HTML content"""
    config = get_debug_config()
    
    if not config["show_debug_icon"]:
        return html_content
    
    # Debug icon HTML
    debug_icon_html = f'''
    <!-- NextPy Debug Icon - Auto-injected in development -->
    <div class="nextpy-debug-overlay">
        <!-- Debug Icon Button -->
        <div 
            class="nextpy-debug-icon"
            onclick="toggleDebugPanel()"
            title="NextPy Debug Panel"
        >
            <span class="nextpy-debug-text">NP</span>
            <span class="nextpy-debug-badge nextpy-debug-warning" id="nextpy-debug-badge">0</span>
        </div>
        
        <!-- Debug Panel -->
        <div class="nextpy-debug-panel" id="nextpy-debug-panel" style="display: none;">
            <!-- Header -->
            <div class="nextpy-debug-header">
                <div class="nextpy-debug-title">
                    <h3>NextPy Debug</h3>
                    <span class="nextpy-debug-version">v2.0.0</span>
                </div>
                <button 
                    class="nextpy-debug-close"
                    onclick="toggleDebugPanel()"
                    title="Close"
                >
                    ×
                </button>
            </div>
            
            <!-- Current Route Info -->
            <div class="nextpy-debug-section">
                <h4>📍 Current Route</h4>
                <div class="nextpy-debug-info">
                    <div class="nextpy-debug-row">
                        <span class="nextpy-debug-label">Path:</span>
                        <span class="nextpy-debug-value" id="nextpy-current-route">{page_props.get("route", "/") if page_props else "/"}</span>
                    </div>
                    <div class="nextpy-debug-row">
                        <span class="nextpy-debug-label">Render Time:</span>
                        <span class="nextpy-debug-value" id="nextpy-render-time">0ms</span>
                    </div>
                    <div class="nextpy-debug-row">
                        <span class="nextpy-debug-label">Environment:</span>
                        <span class="nextpy-debug-value">Development</span>
                    </div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="nextpy-debug-section">
                <h4>⚡ Performance</h4>
                <div class="nextpy-debug-metrics">
                    <div class="nextpy-debug-row">
                        <span class="nextpy-debug-label">Components:</span>
                        <span class="nextpy-debug-value" id="nextpy-component-count">0</span>
                    </div>
                    <div class="nextpy-debug-row">
                        <span class="nextpy-debug-label">Re-renders:</span>
                        <span class="nextpy-debug-value" id="nextpy-rerender-count">0</span>
                    </div>
                    <div class="nextpy-debug-row">
                        <span class="nextpy-debug-label">API Calls:</span>
                        <span class="nextpy-debug-value" id="nextpy-api-calls">0</span>
                    </div>
                    <div class="nextpy-debug-row">
                        <span class="nextpy-debug-label">Memory:</span>
                        <span class="nextpy-debug-value" id="nextpy-memory-usage">0MB</span>
                    </div>
                </div>
            </div>
            
            <!-- Page Props -->
            {f'''<div class="nextpy-debug-section">
                <h4>📄 Page Props</h4>
                <div class="nextpy-debug-props">
                    <pre class="nextpy-debug-code">{__format_props(page_props) if page_props else '{}'}</pre>
                </div>
            </div>''' if page_props else ""}
            
            <!-- Development Tools -->
            <div class="nextpy-debug-section">
                <h4>🛠️  Tools</h4>
                <div class="nextpy-debug-tools">
                    <button 
                        class="nextpy-debug-tool-btn"
                        onclick="toggleComponentBoundaries()"
                        title="Toggle component boundaries"
                    >
                        📦 Boundaries
                    </button>
                    <button 
                        class="nextpy-debug-tool-btn"
                        onclick="toggleRerenderHighlight()"
                        title="Highlight re-renders"
                    >
                        🔄 Re-renders
                    </button>
                    <button 
                        class="nextpy-debug-tool-btn"
                        onclick="toggleVerboseLogging()"
                        title="Enable verbose logging"
                    >
                        📝 Verbose
                    </button>
                    <button 
                        class="nextpy-debug-tool-btn"
                        onclick="togglePerformanceMode()"
                        title="Performance monitoring"
                    >
                        ⚡ Performance
                    </button>
                    <button 
                        class="nextpy-debug-tool-btn"
                        onclick="clearDebugLogs()"
                        title="Clear debug logs"
                    >
                        🧹 Clear
                    </button>
                    <button 
                        class="nextpy-debug-tool-btn"
                        onclick="exportDebugData()"
                        title="Export debug data"
                    >
                        📤 Export
                    </button>
                </div>
            </div>
            
            <!-- Console Logs -->
            <div class="nextpy-debug-section">
                <h4>📋 Console Logs</h4>
                <div class="nextpy-debug-logs" id="nextpy-debug-logs">
                    <div class="nextpy-debug-log-item nextpy-debug-log-info">
                        <span class="nextpy-debug-log-time">12:34:56</span>
                        <span class="nextpy-debug-log-level">INFO</span>
                        <span class="nextpy-debug-log-message">NextPy Debug initialized</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    # Debug scripts
    debug_scripts = f'''
    <script>
        // NextPy Debug System - Auto-injected
        (function() {{
            const DEBUG_CONFIG = {config};
            
            // Global debug state
            window.nextpyDebug = {{
                logs: [],
                metrics: {{
                    componentCount: 0,
                    rerenderCount: 0,
                    apiCalls: 0,
                    renderTime: 0,
                    startTime: performance.now()
                }},
                settings: DEBUG_CONFIG
            }};
            
            // Toggle debug panel
            function toggleDebugPanel() {{
                const panel = document.getElementById('nextpy-debug-panel');
                const icon = document.querySelector('.nextpy-debug-icon');
                
                if (panel.style.display === 'block') {{
                    panel.style.display = 'none';
                    icon.classList.remove('active');
                }} else {{
                    panel.style.display = 'block';
                    icon.classList.add('active');
                    updateMetrics();
                }}
            }}
            
            // Update metrics
            function updateMetrics() {{
                const metrics = window.nextpyDebug.metrics;
                const currentTime = performance.now();
                metrics.renderTime = Math.round(currentTime - metrics.startTime);
                
                // Update UI
                document.getElementById('nextpy-render-time').textContent = metrics.renderTime + 'ms';
                document.getElementById('nextpy-component-count').textContent = metrics.componentCount;
                document.getElementById('nextpy-rerender-count').textContent = metrics.rerenderCount;
                document.getElementById('nextpy-api-calls').textContent = metrics.apiCalls;
                
                // Memory usage (if available)
                if (performance.memory) {{
                    const memoryMB = Math.round(performance.memory.usedJSHeapSize / 1048576);
                    document.getElementById('nextpy-memory-usage').textContent = memoryMB + 'MB';
                }}
            }}
            
            // Development tools
            function toggleComponentBoundaries() {{
                const btn = event.target;
                btn.classList.toggle('active');
                const isActive = btn.classList.contains('active');
                
                if (isActive) {{
                    // Add component boundaries
                    document.querySelectorAll('[data-component]').forEach(el => {{
                        el.style.outline = '2px dashed #0070f3';
                        el.style.outlineOffset = '2px';
                    }});
                    addDebugLog('INFO', 'Component boundaries enabled');
                }} else {{
                    // Remove component boundaries
                    document.querySelectorAll('[data-component]').forEach(el => {{
                        el.style.outline = '';
                        el.style.outlineOffset = '';
                    }});
                    addDebugLog('INFO', 'Component boundaries disabled');
                }}
            }}
            
            function toggleRerenderHighlight() {{
                const btn = event.target;
                btn.classList.toggle('active');
                const isActive = btn.classList.contains('active');
                addDebugLog('INFO', 'Re-render highlights ' + (isActive ? 'enabled' : 'disabled'));
            }}
            
            function toggleVerboseLogging() {{
                const btn = event.target;
                btn.classList.toggle('active');
                const isActive = btn.classList.contains('active');
                addDebugLog('INFO', 'Verbose logging ' + (isActive ? 'enabled' : 'disabled'));
            }}
            
            function togglePerformanceMode() {{
                const btn = event.target;
                btn.classList.toggle('active');
                const isActive = btn.classList.contains('active');
                
                if (isActive) {{
                    startPerformanceMonitoring();
                }} else {{
                    stopPerformanceMonitoring();
                }}
                addDebugLog('INFO', 'Performance monitoring ' + (isActive ? 'enabled' : 'disabled'));
            }}
            
            function clearDebugLogs() {{
                const logs = document.getElementById('nextpy-debug-logs');
                logs.innerHTML = '<div class="nextpy-debug-log-item nextpy-debug-log-info"><span class="nextpy-debug-log-time">' + new Date().toLocaleTimeString() + '</span><span class="nextpy-debug-log-level">INFO</span><span class="nextpy-debug-log-message">Debug logs cleared</span></div>';
                window.nextpyDebug.logs = [];
                updateErrorBadge();
            }}
            
            function exportDebugData() {{
                const debugData = {{
                    timestamp: new Date().toISOString(),
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    metrics: window.nextpyDebug.metrics,
                    logs: window.nextpyDebug.logs,
                    config: window.nextpyDebug.settings
                }};
                
                const dataStr = JSON.stringify(debugData, null, 2);
                const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
                const url = URL.createObjectURL(dataBlob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = 'nextpy-debug-' + Date.now() + '.json';
                a.click();
                
                URL.revokeObjectURL(url);
                addDebugLog('INFO', 'Debug data exported');
            }}
            
            // Console capture
            function addDebugLog(level, message) {{
                const logEntry = {{
                    timestamp: new Date().toISOString(),
                    time: new Date().toLocaleTimeString(),
                    level: level,
                    message: message
                }};
                
                window.nextpyDebug.logs.push(logEntry);
                
                const logs = document.getElementById('nextpy-debug-logs');
                if (logs) {{
                    const logItem = document.createElement('div');
                    logItem.className = `nextpy-debug-log-item nextpy-debug-log-${{level.toLowerCase()}}`;
                    logItem.innerHTML = `
                        <span class="nextpy-debug-log-time">${{logEntry.time}}</span>
                        <span class="nextpy-debug-log-level">${{level}}</span>
                        <span class="nextpy-debug-log-message">${{message}}</span>
                    `;
                    logs.appendChild(logItem);
                    logs.scrollTop = logs.scrollHeight;
                    
                    // Keep only last 100 logs
                    if (logs.children.length > 100) {{
                        logs.removeChild(logs.firstChild);
                    }}
                }}
                
                updateErrorBadge();
            }}
            
            function updateErrorBadge() {{
                const badge = document.getElementById('nextpy-debug-badge');
                const errorCount = window.nextpyDebug.logs.filter(log => log.level === 'ERROR').length;
                const warningCount = window.nextpyDebug.logs.filter(log => log.level === 'WARN').length;
                
                if (errorCount > 0) {{
                    badge.textContent = errorCount;
                    badge.className = 'nextpy-debug-badge nextpy-debug-error';
                }} else if (warningCount > 0) {{
                    badge.textContent = warningCount;
                    badge.className = 'nextpy-debug-badge nextpy-debug-warning';
                }} else {{
                    badge.textContent = '0';
                    badge.className = 'nextpy-debug-badge nextpy-debug-warning';
                }}
            }}
            
            // Console override
            const originalLog = console.log;
            const originalWarn = console.warn;
            const originalError = console.error;
            
            console.log = function(...args) {{
                originalLog.apply(console, args);
                addDebugLog('INFO', args.join(' '));
            }};
            
            console.warn = function(...args) {{
                originalWarn.apply(console, args);
                addDebugLog('WARN', args.join(' '));
            }};
            
            console.error = function(...args) {{
                originalError.apply(console, args);
                addDebugLog('ERROR', args.join(' '));
            }};
            
            // Error capture
            window.addEventListener('error', function(event) {{
                addDebugLog('ERROR', event.message + ' at ' + event.filename + ':' + event.lineno);
            }});
            
            window.addEventListener('unhandledrejection', function(event) {{
                addDebugLog('ERROR', 'Unhandled promise rejection: ' + event.reason);
            }});
            
            // Performance monitoring
            let performanceInterval = null;
            
            function startPerformanceMonitoring() {{
                performanceInterval = setInterval(updateMetrics, 1000);
            }}
            
            function stopPerformanceMonitoring() {{
                if (performanceInterval) {{
                    clearInterval(performanceInterval);
                    performanceInterval = null;
                }}
            }}
            
            // Make debug icon draggable
            let isDragging = false;
            let currentX = 0;
            let currentY = 0;
            let initialX = 0;
            let initialY = 0;
            let xOffset = 0;
            let yOffset = 0;
            
            const debugIcon = document.querySelector('.nextpy-debug-icon');
            if (debugIcon) {{
                debugIcon.addEventListener('mousedown', dragStart);
                document.addEventListener('mousemove', drag);
                document.addEventListener('mouseup', dragEnd);
            }}
            
            function dragStart(e) {{
                if (e.target.classList.contains('nextpy-debug-icon')) {{
                    initialX = e.clientX - xOffset;
                    initialY = e.clientY - yOffset;
                    isDragging = true;
                }}
            }}
            
            function dragEnd(e) {{
                initialX = currentX;
                initialY = currentY;
                isDragging = false;
            }}
            
            function drag(e) {{
                if (isDragging) {{
                    e.preventDefault();
                    currentX = e.clientX - initialX;
                    currentY = e.clientY - initialY;
                    xOffset = currentX;
                    yOffset = currentY;
                    
                    if (debugIcon) {{
                        debugIcon.style.transform = `translate(${{currentX}}px, ${{currentY}}px)`;
                    }}
                }}
            }}
            
            // Initialize
            addDebugLog('INFO', 'NextPy Debug system initialized');
            updateMetrics();
            
            // Auto-update metrics every 2 seconds
            setInterval(updateMetrics, 2000);
        }})();
    </script>
    '''
    
    # CSS styles
    debug_css = '''
    <style>
        /* NextPy Debug Styles - Auto-injected */
        .nextpy-debug-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9999;
        }
        
        .nextpy-debug-icon {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 48px;
            height: 48px;
            background: #1a1a1a;
            border: 2px solid #333;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-family: 'SF Mono', 'Monaco', monospace;
            font-size: 12px;
            font-weight: bold;
            color: #fff;
            transition: all 0.2s ease;
            pointer-events: all;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            user-select: none;
        }
        
        .nextpy-debug-icon:hover {
            background: #333;
            border-color: #555;
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        }
        
        .nextpy-debug-icon.active {
            background: #0070f3;
            border-color: #0051cc;
        }
        
        .nextpy-debug-text {
            font-size: 14px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        .nextpy-debug-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            min-width: 18px;
            height: 18px;
            background: #ffaa00;
            color: white;
            border-radius: 50%;
            font-size: 10px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #1a1a1a;
        }
        
        .nextpy-debug-badge.nextpy-debug-error {
            background: #ff4444;
        }
        
        .nextpy-debug-panel {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 400px;
            max-height: 600px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            overflow: hidden;
            pointer-events: all;
            font-family: 'SF Mono', 'Monaco', monospace;
            font-size: 12px;
            color: #fff;
        }
        
        .nextpy-debug-header {
            background: #2a2a2a;
            padding: 12px 16px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .nextpy-debug-title {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .nextpy-debug-title h3 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
            color: #fff;
        }
        
        .nextpy-debug-version {
            background: #0070f3;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 500;
        }
        
        .nextpy-debug-close {
            background: none;
            border: none;
            color: #999;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        .nextpy-debug-close:hover {
            background: #ff4444;
            color: white;
        }
        
        .nextpy-debug-section {
            border-bottom: 1px solid #333;
            padding: 12px 16px;
        }
        
        .nextpy-debug-section:last-child {
            border-bottom: none;
        }
        
        .nextpy-debug-section h4 {
            margin: 0 0 8px 0;
            font-size: 12px;
            font-weight: 600;
            color: #ccc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .nextpy-debug-info,
        .nextpy-debug-metrics {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .nextpy-debug-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 2px 0;
        }
        
        .nextpy-debug-label {
            color: #999;
            font-size: 11px;
        }
        
        .nextpy-debug-value {
            color: #fff;
            font-weight: 500;
            font-size: 11px;
        }
        
        .nextpy-debug-props {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 8px;
            max-height: 120px;
            overflow-y: auto;
        }
        
        .nextpy-debug-code {
            margin: 0;
            font-size: 10px;
            line-height: 1.4;
            color: #ccc;
            white-space: pre-wrap;
            word-break: break-all;
        }
        
        .nextpy-debug-tools {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        
        .nextpy-debug-tool-btn {
            background: #2a2a2a;
            border: 1px solid #444;
            color: #ccc;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
        }
        
        .nextpy-debug-tool-btn:hover {
            background: #3a3a3a;
            border-color: #666;
            color: #fff;
        }
        
        .nextpy-debug-tool-btn.active {
            background: #0070f3;
            border-color: #0051cc;
            color: white;
        }
        
        .nextpy-debug-logs {
            max-height: 200px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .nextpy-debug-log-item {
            display: flex;
            gap: 8px;
            padding: 4px 8px;
            border-radius: 2px;
            font-size: 10px;
            line-height: 1.3;
            align-items: flex-start;
        }
        
        .nextpy-debug-log-info {
            background: rgba(0, 112, 243, 0.1);
            border-left: 3px solid #0070f3;
        }
        
        .nextpy-debug-log-warning {
            background: rgba(255, 170, 0, 0.1);
            border-left: 3px solid #ffa500;
        }
        
        .nextpy-debug-log-error {
            background: rgba(255, 68, 68, 0.1);
            border-left: 3px solid #ff4444;
        }
        
        .nextpy-debug-log-time {
            color: #666;
            font-family: monospace;
            white-space: nowrap;
            min-width: 60px;
        }
        
        .nextpy-debug-log-level {
            font-weight: bold;
            min-width: 40px;
        }
        
        .nextpy-debug-log-message {
            color: #ccc;
            flex: 1;
            word-break: break-word;
        }
        
        @media (max-width: 480px) {
            .nextpy-debug-panel {
                width: calc(100vw - 40px);
                right: 20px;
                left: 20px;
                max-height: 70vh;
            }
            
            .nextpy-debug-tools {
                grid-template-columns: 1fr;
            }
        }
    </style>
    '''
    
    # Insert debug icon before closing body tag
    if "</body>" in html_content:
        # Insert before </body>
        parts = html_content.split("</body>")
        html_content = parts[0] + debug_icon_html + debug_scripts + debug_css + "</body>" + parts[1] if len(parts) > 1 else parts[0] + debug_icon_html + debug_scripts + debug_css + "</body>"
    else:
        # Append at the end
        html_content += debug_icon_html + debug_scripts + debug_css
    
    return html_content

def __format_props(props: Dict[str, Any]) -> str:
    """Format props for display"""
    import json
    return json.dumps(props, indent=2, default=str)
