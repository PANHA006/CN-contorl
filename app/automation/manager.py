import threading
import time
import queue
from playwright.sync_api import sync_playwright
from app.utils.logger import logger

class ChromeInstance:
    """Represents a single automated Chrome instance using Playwright, running in a dedicated thread."""
    def __init__(self, profile_id: str, profile_name: str, user_data_dir: str, proxy_str: str = None, 
                 proxy_user: str = None, proxy_pass: str = None,
                 win_x: int = None, win_y: int = None, win_w: int = None, win_h: int = None,
                 small_window: bool = False, mobile_mode: bool = False,
                 latitude: float = None, longitude: float = None):
        self.profile_id = profile_id
        self.profile_name = profile_name
        self.user_data_dir = user_data_dir
        self.proxy_str = proxy_str
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass
        self.small_window = small_window
        self.mobile_mode = mobile_mode
        self.latitude = latitude
        self.longitude = longitude
        
        # Window sizing/positioning
        self.win_x = win_x
        self.win_y = win_y
        self.win_w = win_w
        self.win_h = win_h
        
        self.browser_context = None
        self.page = None
        self.stop_event = threading.Event()
        self.action_queue = queue.Queue()
        self.thread = None
        self.on_close_callback = None

    def fetch_active_ip(self) -> str:
        """Fetches active public IP address of the browser context."""
        try:
            if self.page and not self.page.is_closed():
                response = self.page.request.get("https://api.ipify.org?format=json", timeout=5000)
                if response.ok:
                    data = response.json()
                    ip = data.get("ip", "")
                    if ip:
                        return ip
        except Exception:
            pass
        return ""

    def start(self, on_close_callback=None):
        """Starts the browser lifecycle in a background thread."""
        self.on_close_callback = on_close_callback
        self.stop_event.clear()
        # Clear action queue in case of restarts
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except queue.Empty:
                break
        self.thread = threading.Thread(target=self._run_browser_loop, daemon=True)
        self.thread.start()

    def _run_browser_loop(self):
        """Playwright synchronous event loop running inside the background thread."""
        try:
            with sync_playwright() as p:
                # Prepare proxy dictionary if configured
                proxy_config = None
                if self.proxy_str and self.proxy_str.strip() and self.proxy_str.strip().lower() != "no proxy":
                    # Standardize server format (requires http/socks scheme)
                    server_url = self.proxy_str.strip()
                    if not (server_url.startswith("http://") or server_url.startswith("https://") or server_url.startswith("socks5://")):
                        server_url = f"http://{server_url}"
                    
                    proxy_config = {"server": server_url}
                    if self.proxy_user:
                        proxy_config["username"] = self.proxy_user
                    if self.proxy_pass:
                        proxy_config["password"] = self.proxy_pass

                # Set launch arguments (headed, no-sandbox, window size/position)
                args = ["--no-sandbox", "--disable-setuid-sandbox"]
                if self.small_window:
                    args.append("--start-normal")
                    
                if self.win_x is not None and self.win_y is not None:
                    args.append(f"--window-position={self.win_x},{self.win_y}")
                if self.win_w is not None and self.win_h is not None:
                    args.append(f"--window-size={self.win_w},{self.win_h}")
                else:
                    if self.small_window:
                        args.append("--window-size=480,720")
                    else:
                        args.append("--start-maximized")

                # Prepare mobile emulation configurations
                user_agent = None
                viewport = None
                is_mobile = None
                has_touch = None
                
                if self.mobile_mode:
                    user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
                    viewport = {"width": 375, "height": 812}
                    is_mobile = True
                    has_touch = True

                geolocation = None
                permissions = None
                if self.latitude is not None and self.longitude is not None:
                    try:
                        geolocation = {"latitude": float(self.latitude), "longitude": float(self.longitude)}
                        permissions = ["geolocation"]
                        logger.log(f"[{self.profile_name}] Spoofing GPS Geolocation: Lat {self.latitude}, Lng {self.longitude}")
                    except Exception as e:
                        logger.log(f"[{self.profile_name}] Invalid geolocation coordinates: {e}")

                logger.log(f"[{self.profile_name}] Launching browser with persistent context...")
                
                # Launch persistent Chrome browser context
                self.browser_context = p.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=False,
                    proxy=proxy_config,
                    args=args,
                    no_viewport=not self.mobile_mode,  # Do not override viewport unless in mobile mode
                    user_agent=user_agent,
                    viewport=viewport,
                    is_mobile=is_mobile,
                    has_touch=has_touch,
                    geolocation=geolocation,
                    permissions=permissions
                )

                # Set default page or open new page
                pages = self.browser_context.pages
                self.page = pages[0] if pages else self.browser_context.new_page()
                
                # Enforce exact window bounds for Small Window or Tile Windows via CDP
                if self.small_window or (self.win_w is not None and self.win_h is not None):
                    try:
                        target_w = self.win_w if self.win_w else 480
                        target_h = self.win_h if self.win_h else 720
                        target_x = self.win_x if self.win_x is not None else 100
                        target_y = self.win_y if self.win_y is not None else 100
                        
                        cdp = self.browser_context.new_cdp_session(self.page)
                        win_info = cdp.send("Browser.getWindowForTarget")
                        window_id = win_info["windowId"]
                        cdp.send("Browser.setWindowBounds", {
                            "windowId": window_id,
                            "bounds": {
                                "windowState": "normal",
                                "width": target_w,
                                "height": target_h,
                                "left": target_x,
                                "top": target_y
                            }
                        })
                        logger.log(f"[{self.profile_name}] Applied small window size ({target_w}x{target_h}) via CDP.")
                    except Exception as e:
                        logger.log(f"[{self.profile_name}] Window bounds adjustment note: {e}")

                # Hook close event to trigger state change in GUI
                self.browser_context.on("close", lambda ctx: self._handle_browser_closed_event())
                
                # Initially navigate to Facebook
                try:
                    logger.log(f"[{self.profile_name}] Navigating to facebook.com...")
                    self.page.goto("https://www.facebook.com", timeout=30000)
                except Exception as e:
                    logger.log(f"[{self.profile_name}] Navigation error: {e}")

                # Keep thread alive, check stop event, and execute queued tasks
                while not self.stop_event.is_set():
                    # Check if the page/browser is closed by the user
                    try:
                        if not self.page or self.page.is_closed():
                            logger.log(f"[{self.profile_name}] Page closed by user.")
                            break
                    except Exception:
                        logger.log(f"[{self.profile_name}] Browser connection lost.")
                        break

                    try:
                        # Non-blocking check on action queue
                        action, data = self.action_queue.get_nowait()
                        if action == "navigate":
                            logger.log(f"[{self.profile_name}] Navigating to: {data}...")
                            self.page.goto(data, timeout=30000)
                        elif action == "custom" and callable(data):
                            data()
                    except queue.Empty:
                        # Yield control to Playwright's asyncio loop to process events
                        try:
                            self.page.wait_for_timeout(200)
                        except Exception:
                            logger.log(f"[{self.profile_name}] Connection lost during wait.")
                            break
                    except Exception as e:
                        logger.log(f"[{self.profile_name}] Error executing action '{action}': {e}")

                # Close browser context if stop_event was set programmatically
                logger.log(f"[{self.profile_name}] Closing browser context...")
                try:
                    self.browser_context.close()
                except Exception:
                    pass

        except Exception as e:
            logger.log(f"[{self.profile_name}] Playwright thread error: {e}")
        finally:
            # Ensure the GUI is ALWAYS notified when the thread exits
            self._handle_browser_closed_event()

    def navigate_to(self, url: str):
        """Pushes a navigation task to the background thread's queue."""
        self.action_queue.put(("navigate", url))

    def close(self):
        """Safely shuts down the browser context and Playwright instance by setting the stop event."""
        self.stop_event.set()

    def _handle_browser_closed_event(self):
        """Internal callback fired when browser context is closed by the user or programmatically."""
        self.stop_event.set()
        if self.on_close_callback:
            try:
                self.on_close_callback(self.profile_name)
            except Exception:
                pass


class ChromeGroupManager:
    """Manages collection of active ChromeInstances and handles orchestration."""
    def __init__(self):
        self.active_instances = {}

    def launch_instance(self, profile_id: str, profile_name: str, user_data_dir: str, 
                        proxy: str = None, proxy_user: str = None, proxy_pass: str = None,
                        win_x: int = None, win_y: int = None, win_w: int = None, win_h: int = None,
                        small_window: bool = False, mobile_mode: bool = False,
                        latitude: float = None, longitude: float = None,
                        on_close_callback=None) -> ChromeInstance:
        """Creates, launches, and registers a new ChromeInstance."""
        if profile_id in self.active_instances:
            logger.log(f"Browser '{profile_name}' is already running.")
            return self.active_instances[profile_id]

        instance = ChromeInstance(
            profile_id=profile_id,
            profile_name=profile_name,
            user_data_dir=user_data_dir,
            proxy_str=proxy,
            proxy_user=proxy_user,
            proxy_pass=proxy_pass,
            win_x=win_x,
            win_y=win_y,
            win_w=win_w,
            win_h=win_h,
            small_window=small_window,
            mobile_mode=mobile_mode,
            latitude=latitude,
            longitude=longitude
        )
        
        self.active_instances[profile_id] = instance
        instance.start(on_close_callback=lambda pid_name: self._handle_instance_close(profile_id, on_close_callback))
        return instance

    def close_instance(self, profile_id: str):
        """Closes a specific tracked ChromeInstance."""
        if profile_id in self.active_instances:
            self.active_instances[profile_id].close()

    def close_all(self):
        """Closes all tracked ChromeInstances."""
        for instance in list(self.active_instances.values()):
            instance.close()

    def _handle_instance_close(self, profile_id: str, user_callback):
        """Fires when an instance closes to clean up registration and trigger GUI callback."""
        if profile_id in self.active_instances:
            del self.active_instances[profile_id]
        if user_callback:
            user_callback(profile_id)
