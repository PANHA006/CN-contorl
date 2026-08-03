import datetime

class GUIOutputLogger:
    """Helper logger class that holds log history and callbacks to update GUI."""
    def __init__(self):
        self.logs = []
        self.listeners = []

    def log(self, message: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.logs.append(formatted_message)
        print(formatted_message)  # Fallback to terminal console
        
        # Notify GUI listeners
        for listener in self.listeners:
            try:
                listener(formatted_message)
            except Exception:
                pass

    def add_listener(self, callback) -> None:
        self.listeners.append(callback)

# Global logger instance
logger = GUIOutputLogger()
