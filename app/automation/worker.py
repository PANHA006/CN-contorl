import threading
import time
from app.utils.logger import logger

class LaunchWorker(threading.Thread):
    """Background thread worker to launch multiple Chrome instances with a configured delay and grid positions."""
    def __init__(self, selected_profiles: list, delay_sec: float, manager, 
                 screen_w: int = 1920, screen_h: int = 1080, tile: bool = False,
                 small_window: bool = False, mobile_mode: bool = False, 
                 on_launch_callback=None, on_finished_callback=None):
        super().__init__()
        self.selected_profiles = selected_profiles
        self.delay_sec = delay_sec
        self.manager = manager
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.tile = tile
        self.small_window = small_window
        self.mobile_mode = mobile_mode
        self.on_launch = on_launch_callback
        self.on_finished = on_finished_callback
        self.daemon = True

    def run(self):
        """Iterates over selected profiles, launching them one-by-one with delay and optional grid layout."""
        count = len(self.selected_profiles)
        if count == 0:
            if self.on_finished:
                try:
                    self.on_finished()
                except Exception:
                    pass
            return
        
        # Grid layout calculation:
        if self.small_window:
            # For small window mode, fix window size to portrait style (e.g. 390x820)
            win_w = 390
            win_h = min(820, self.screen_h - 80)
            # Calculate how many small windows fit side-by-side
            cols = max(1, self.screen_w // win_w)
            rows = max(1, (self.screen_h - 80) // win_h)
        else:
            # Determine number of columns and rows based on browser count for desktop grid
            cols = 2
            if count <= 1:
                cols = 1
            elif count <= 4:
                cols = 2
            else:
                cols = 3
                
            rows = (count + cols - 1) // cols
            
            # Individual window size (subtracting taskbar/margins)
            win_w = self.screen_w // cols
            win_h = (self.screen_h - 60) // rows  # 60px padding for taskbar/titlebars
        
        for index, profile in enumerate(self.selected_profiles):
            profile_id = profile["id"]
            profile_name = profile["name"]
            user_data_dir = profile["user_data_dir"]
            proxy = profile.get("proxy")
            proxy_user = profile.get("proxy_user")
            proxy_pass = profile.get("proxy_pass")
            
            # Apply grid positioning if tile layout is checked
            win_x, win_y = None, None
            if self.tile:
                r = index // cols
                c = index % cols
                win_x = c * win_w
                win_y = r * win_h
                logger.log(f"[{profile_name}] Arranging position at Grid: ({win_x}, {win_y}) with Size: {win_w}x{win_h}")

            if index > 0 and self.delay_sec > 0:
                logger.log(f"Delaying {self.delay_sec} seconds before launching next browser...")
                time.sleep(self.delay_sec)
            
            logger.log(f"Launching browser for profile: '{profile_name}' (Tile: {self.tile}, Small: {self.small_window}, Mobile: {self.mobile_mode})...")
            # Launch through ChromeGroupManager
            self.manager.launch_instance(
                profile_id=profile_id,
                profile_name=profile_name,
                user_data_dir=user_data_dir,
                proxy=proxy,
                proxy_user=proxy_user,
                proxy_pass=proxy_pass,
                win_x=win_x,
                win_y=win_y,
                win_w=win_w,
                win_h=win_h,
                small_window=self.small_window,
                mobile_mode=self.mobile_mode,
                on_close_callback=self.on_launch  # Reuse callback to notify closure
            )
            
            # Notify GUI of successful launch
            if self.on_launch:
                try:
                    self.on_launch(profile_id, is_running=True)
                except Exception:
                    pass
        
        if self.on_finished:
            try:
                self.on_finished()
            except Exception:
                pass


class NavigationWorker(threading.Thread):
    """Background thread worker to navigate active Chrome instances to a URL with a delay."""
    def __init__(self, active_instances: list, url: str, delay_sec: float, on_finished_callback=None):
        super().__init__()
        self.active_instances = active_instances
        self.url = url
        self.delay_sec = delay_sec
        self.on_finished = on_finished_callback
        self.daemon = True

    def run(self):
        """Iterates over active instances, navigating them to the URL with delay."""
        for index, instance in enumerate(self.active_instances):
            if index > 0 and self.delay_sec > 0:
                logger.log(f"Delaying {self.delay_sec} seconds before navigating next browser...")
                time.sleep(self.delay_sec)
            
            logger.log(f"Navigating browser '{instance.profile_name}' to link...")
            instance.navigate_to(self.url)

        if self.on_finished:
            try:
                self.on_finished()
            except Exception:
                pass
