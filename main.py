import sys
from app.utils.file_helper import load_settings
from app.utils.logger import logger
from app.gui.dashboard import DashboardApp

def main():
    logger.log("CN Browser Multi-Control Application starting...")
    
    # Initialize settings and folders
    settings = load_settings()
    logger.log(f"Settings loaded. Found {len(settings.get('profiles', []))} profiles.")
    
    # Launch main CustomTkinter GUI Dashboard
    try:
        app = DashboardApp()
        app.mainloop()
    except Exception as e:
        logger.log(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
