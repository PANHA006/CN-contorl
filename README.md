# Facebook Chrome Multi-Control Dashboard

A professional Python-based desktop dashboard built with CustomTkinter and Playwright to manage and automate multiple isolated Google Chrome browser instances.

## Features
- **Profile Management**: Add, name, and manage independent Chrome profiles.
- **Persistent Sessions**: Log in manually once; cookies and sessions are saved locally per profile.
- **Group & Individual Controls**: Open links individually or on all selected instances concurrently.
- **Launch Delay**: Prevent account flags by adding a delay between launching profiles.
- **Window Grid Layout**: Tiling of open Chrome windows on the screen for easy monitoring.
- **Proxy per Profile**: Route traffic of each profile through a separate proxy server.

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

3. **Run Application**:
   ```bash
   python main.py
   ```
