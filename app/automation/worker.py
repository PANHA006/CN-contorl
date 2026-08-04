import threading
import time
import random
from app.utils.logger import logger
from app.utils.file_helper import get_profile_dir

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
            latitude = profile.get("latitude")
            longitude = profile.get("longitude")
            
            # Apply grid positioning if tile layout is checked
            win_x, win_y = None, None
            if self.tile:
                r = index // cols
                c = index % cols
                win_x = c * win_w
                win_y = r * win_h
                logger.log(f"[{profile_name}] Arranging position at Grid: ({win_x}, {win_y}) with Size: {win_w}x{win_h}")

            if index > 0 and self.delay_sec > 0:
                actual_delay = random.uniform(1.0, max(1.0, float(self.delay_sec)))
                logger.log(f"Delaying {actual_delay:.1f}s (random 1.0s - {self.delay_sec}s) before launching next browser...")
                time.sleep(actual_delay)
            
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
                latitude=latitude,
                longitude=longitude,
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


class AutomationTaskWorker(threading.Thread):
    """Background thread worker to execute Facebook automation tasks (Like, Follow, Comment, Share) sequentially across active Chrome instances."""
    def __init__(self, tasks_list: list, active_instances: list, target_url: str, delay_sec: float, options: dict = None, on_finished_callback=None):
        super().__init__()
        self.tasks_list = tasks_list if isinstance(tasks_list, list) else [tasks_list]
        self.active_instances = active_instances
        self.target_url = target_url
        self.delay_sec = delay_sec
        self.options = options or {}
        self.on_finished = on_finished_callback
        self.daemon = True

    def run(self):
        from app.automation.facebook_actions import (
            execute_auto_like, execute_auto_follow, execute_auto_comment, execute_auto_share
        )
        import random
        
        # Initialize non-repeating comment pool with thread lock
        raw_comments = self.options.get("comment_list", [])
        comment_pool = list(raw_comments)
        comment_pool_lock = threading.Lock()
        task_str = ", ".join(self.tasks_list)
        
        threads = []
        
        for index, instance in enumerate(self.active_instances):
            # Calculate staggered initial launch delay per browser (e.g. Browser 0=0s, Browser 1=1.5s, Browser 2=3.1s...)
            stagger_delay = (index * random.uniform(1.0, max(1.0, self.delay_sec))) if index > 0 else 0.0
            
            def run_instance_pipeline(inst=instance, initial_delay=stagger_delay):
                if initial_delay > 0:
                    logger.log(f"[{inst.profile_name}] Staggered start delay: pausing {initial_delay:.1f}s before starting tasks...")
                    slept = 0.0
                    while slept < initial_delay and not inst.stop_event.is_set():
                        time.sleep(0.5)
                        slept += 0.5
                    
                if inst.stop_event.is_set():
                    logger.log(f"[{inst.profile_name}] Browser stopped before task execution.")
                    return

                logger.log(f"[{inst.profile_name}] Starting parallel [{task_str}] tasks on: {self.target_url}...")
                
                action_finished_event = threading.Event()
                
                def perform_action(i=inst, evt=action_finished_event):
                    try:
                        nonlocal comment_pool
                        page = i.page
                        if not page or page.is_closed():
                            logger.log(f"[{i.profile_name}] Error: Page is closed or unavailable.")
                            return
                            
                        # Navigate ONCE to target URL for this profile task pipeline
                        if self.target_url and page.url != self.target_url:
                            try:
                                page.goto(self.target_url, timeout=30000)
                                page.wait_for_timeout(2500)
                            except Exception as e:
                                logger.log(f"[{i.profile_name}] Navigation error: {e}")
                                
                        # Watch Video Time Delay before actions (only run if LIKE, COMMENT, or SHARE post tasks are enabled)
                        is_post_action = any(t in self.tasks_list for t in ["LIKE", "COMMENT", "SHARE"])
                        raw_watch = float(self.options.get("watch_time", 0))
                        watch_time = raw_watch if is_post_action else 0.0

                        if watch_time > 0:
                            actual_watch = watch_time + random.uniform(0.5, 2.0)
                            logger.log(f"[{i.profile_name}] Playing and watching Reel/Video for {actual_watch:.1f}s before actions...")
                            try:
                                v_elem = page.query_selector("video, div[aria-label='Play']")
                                if v_elem:
                                    v_elem.click()
                            except Exception:
                                pass
                            time.sleep(actual_watch)
                                
                        for t_idx, task in enumerate(self.tasks_list):
                            if i.stop_event.is_set():
                                break

                            if t_idx > 0 or watch_time > 0:
                                inter_delay = random.uniform(1.0, 3.0)
                                logger.log(f"[{i.profile_name}] Inter-action step delay: pausing {inter_delay:.1f}s before {task}...")
                                time.sleep(inter_delay)

                            if task == "LIKE":
                                reaction = self.options.get("reaction", "LIKE")
                                random_react = self.options.get("random_reaction", False)
                                allowed_reacts = self.options.get("allowed_reactions", [])
                                execute_auto_like(page, self.target_url, reaction_type=reaction, random_reaction=random_react, allowed_reactions=allowed_reacts, navigate_first=False)
                                time.sleep(random.uniform(1.0, 2.5))
                                
                            elif task == "COMMENT":
                                selected_cmt = None
                                with comment_pool_lock:
                                    if not comment_pool and raw_comments:
                                        comment_pool = list(raw_comments)
                                    if comment_pool:
                                        selected_cmt = random.choice(comment_pool)
                                        comment_pool.remove(selected_cmt)
                                
                                c_list = [selected_cmt] if selected_cmt else raw_comments
                                enable_emoji = self.options.get("enable_emoji", True)
                                execute_auto_comment(page, self.target_url, comment_list=c_list, enable_emoji=enable_emoji, navigate_first=False)
                                time.sleep(random.uniform(1.0, 2.5))
                                
                            elif task == "SHARE":
                                destination = self.options.get("destination", "PUBLIC")
                                captions = self.options.get("captions", [])
                                execute_auto_share(page, self.target_url, destination=destination, captions=captions, navigate_first=False)
                                time.sleep(random.uniform(1.0, 2.5))
                                
                            elif task == "FOLLOW":
                                target_type = self.options.get("target_type", "USER")
                                set_favorites = self.options.get("set_favorites", True)
                                execute_auto_follow(page, self.target_url, target_type=target_type, set_favorites=set_favorites, navigate_first=False)
                                time.sleep(random.uniform(1.0, 2.5))
                    except Exception as ex:
                        logger.log(f"[{i.profile_name}] Error during action execution: {ex}")
                    finally:
                        evt.set()

                inst.action_queue.put(("custom", perform_action))

                # Periodically check action_finished_event or browser stop_event (thread safe)
                while not action_finished_event.is_set():
                    if inst.stop_event.is_set():
                        action_finished_event.set()
                        break
                    action_finished_event.wait(timeout=0.5)

            t = threading.Thread(target=run_instance_pipeline, daemon=True)
            threads.append(t)
            t.start()

        # Wait for all parallel instance threads in current batch to complete
        for t in threads:
            t.join()

        if self.on_finished:
            try:
                self.on_finished()
            except Exception:
                pass


class BatchAutomationWorker(threading.Thread):
    """Background thread worker to orchestrate mass account automation in batches (50-200 accounts)."""
    def __init__(self, selected_profiles: list, tasks_list: list, target_url: str, manager, 
                 batch_size: int = 5, batch_rest_delay: float = 30.0, delay_sec: float = 5.0, 
                 options: dict = None, progress_callback=None, on_finished_callback=None):
        super().__init__()
        self.selected_profiles = selected_profiles
        self.tasks_list = tasks_list
        self.target_url = target_url
        self.manager = manager
        self.batch_size = max(1, batch_size)
        self.batch_rest_delay = max(0.0, batch_rest_delay)
        self.delay_sec = delay_sec
        self.options = options or {}
        self.progress_callback = progress_callback
        self.on_finished = on_finished_callback
        self.stop_requested = False
        self.current_batch_instances = []
        self.daemon = True

    def stop(self):
        self.stop_requested = True
        if hasattr(self, 'current_batch_instances') and self.current_batch_instances:
            for inst in self.current_batch_instances:
                if inst and hasattr(inst, 'stop_event'):
                    inst.stop_event.set()

    def run(self):
        try:
            total_profiles = len(self.selected_profiles)
            logger.log(f"Starting Mass Automation Engine for {total_profiles} profile(s) (Batch Size: {self.batch_size}, Batch Rest: {self.batch_rest_delay}s)...")
            
            # Partition profiles into batches
            batches = [self.selected_profiles[i:i + self.batch_size] for i in range(0, total_profiles, self.batch_size)]
            completed_count = 0
            
            tile = self.options.get("tile", False)
            small_window = self.options.get("small_window", False)
            screen_w = self.options.get("screen_w", 1920)
            screen_h = self.options.get("screen_h", 1080)

            for b_index, batch_profiles in enumerate(batches):
                if self.stop_requested:
                    logger.log("Mass Automation task stopped by user.")
                    break
                    
                logger.log(f"--- Processing Batch {b_index + 1} / {len(batches)} ({len(batch_profiles)} profile(s)) ---")
                
                # Grid layout calculations for tiling
                count = len(batch_profiles)
                if small_window:
                    win_w = 390
                    win_h = min(820, screen_h - 80)
                    cols = max(1, screen_w // win_w)
                else:
                    cols = 2 if count <= 4 else (3 if count > 4 else 1)
                    rows = max(1, (count + cols - 1) // cols)
                    win_w = screen_w // cols
                    win_h = (screen_h - 60) // rows

                batch_instances = []
                self.current_batch_instances = batch_instances
                # 1. Launch current batch instances
                for idx, profile in enumerate(batch_profiles):
                    if self.stop_requested:
                        break
                    pid = profile["id"]
                    profile_dir = profile.get("user_data_dir") or get_profile_dir(pid)

                    win_x, win_y = None, None
                    if tile:
                        r = idx // cols
                        c = idx % cols
                        win_x = c * win_w
                        win_y = r * win_h

                    if pid not in self.manager.active_instances:
                        instance = self.manager.launch_instance(
                            profile_id=pid,
                            profile_name=profile["name"],
                            user_data_dir=profile_dir,
                            proxy=profile.get("proxy", ""),
                            proxy_user=profile.get("proxy_user", ""),
                            proxy_pass=profile.get("proxy_pass", ""),
                            win_x=win_x,
                            win_y=win_y,
                            win_w=win_w,
                            win_h=win_h,
                            small_window=small_window,
                            mobile_mode=self.options.get("mobile_mode", False),
                            latitude=profile.get("latitude"),
                            longitude=profile.get("longitude")
                        )
                    else:
                        instance = self.manager.active_instances[pid]
                    batch_instances.append(instance)
                    # Staggered launch delay (1s per browser)
                    time.sleep(random.uniform(1.0, 1.5))
                    
                if self.stop_requested:
                    break
                    
                time.sleep(2.0)
                
                # 2. Execute automation worker on current batch instances
                task_worker = AutomationTaskWorker(
                    tasks_list=self.tasks_list,
                    active_instances=batch_instances,
                    target_url=self.target_url,
                    delay_sec=self.delay_sec,
                    options=self.options
                )
                task_worker.start()
                task_worker.join()
                
                if self.stop_requested:
                    logger.log("Mass Automation task stopped before cleanup.")
                    break

                logger.log("Batch tasks completed. Pausing 3.0s for visual confirmation before closing browsers...")
                time.sleep(3.0)
                
                # 3. Close batch instances to free memory/RAM before next batch
                for inst in batch_instances:
                    self.manager.close_instance(inst.profile_id)
                    time.sleep(0.5)
                    
                completed_count += len(batch_profiles)
                
                if self.progress_callback:
                    try:
                        self.progress_callback(completed_count, total_profiles)
                    except Exception:
                        pass
                        
                if b_index < len(batches) - 1 and self.batch_rest_delay > 0 and not self.stop_requested:
                    min_rest = max(1.0, self.batch_rest_delay * 0.5)
                    max_rest = max(min_rest + 1.0, self.batch_rest_delay * 1.5)
                    actual_rest = random.uniform(min_rest, max_rest)
                    logger.log(f"Batch {b_index + 1} complete. Random rest delay for {actual_rest:.1f}s before next batch...")
                    
                    rest_slept = 0.0
                    while rest_slept < actual_rest and not self.stop_requested:
                        time.sleep(0.5)
                        rest_slept += 0.5

            logger.log(f"=== Mass Automation Completed! Processed all {total_profiles} profile(s) successfully. ===")
        except Exception as e:
            logger.log(f"Error in BatchAutomationWorker: {e}")
        finally:
            if self.on_finished:
                try:
                    self.on_finished()
                except Exception:
                    pass

