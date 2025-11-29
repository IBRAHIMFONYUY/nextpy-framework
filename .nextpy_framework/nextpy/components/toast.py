"""
Toast Notification Component
Display temporary alerts/notifications
"""

from typing import Literal


class Toast:
    """Toast notification system"""
    
    def __init__(self):
        self.toasts = []
    
    def add(self, message: str, type: Literal["success", "error", "info", "warning"] = "info", duration: int = 3000):
        """Add a toast notification"""
        toast_id = len(self.toasts)
        self.toasts.append({
            "id": toast_id,
            "message": message,
            "type": type,
            "duration": duration
        })
        return toast_id
    
    def remove(self, toast_id: int):
        """Remove a toast"""
        self.toasts = [t for t in self.toasts if t["id"] != toast_id]
    
    def clear_all(self):
        """Clear all toasts"""
        self.toasts = []


def toast_html() -> str:
    """Generate toast container HTML"""
    return '''
    <div id="toast-container" class="fixed top-4 right-4 z-50 space-y-2" hx-ext="sse" sse-connect="/api/toasts">
        <div hx-target="#toast-container" hx-swap="beforeend"></div>
    </div>
    
    <style>
        .toast {
            animation: slideInRight 0.3s ease-out, slideOutRight 0.3s ease-in 3s forwards;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            font-weight: 500;
        }
        
        .toast.success {
            background-color: #10b981;
            color: white;
        }
        
        .toast.error {
            background-color: #ef4444;
            color: white;
        }
        
        .toast.info {
            background-color: #3b82f6;
            color: white;
        }
        
        .toast.warning {
            background-color: #f59e0b;
            color: white;
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    </style>
    '''


# Global toast instance
_toast = Toast()

def get_toast() -> Toast:
    """Get global toast instance"""
    return _toast
