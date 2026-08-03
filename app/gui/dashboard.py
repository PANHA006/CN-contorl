import customtkinter as ctk
import time
from app.gui.styles import *
from app.gui.dialogs import AddProfileDialog
from app.utils.file_helper import load_settings, save_settings, add_profile, delete_profile
from app.utils.logger import logger
from app.automation.manager import ChromeGroupManager
from app.automation.worker import LaunchWorker, NavigationWorker
from app.config import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, DEFAULT_DELAY_SEC

class DashboardApp(ctk.CTk):
    """Main Dashboard Window for Facebook Chrome Multi-Control."""
    def __init__(self):
        super().__init__()
        self.title("🌐 CN Browser - Facebook Chrome Multi-Control")
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.configure(fg_color=COLOR_BG)
        
        # Initialize browser automation manager
        self.manager = ChromeGroupManager()
        
        # Keep track of active profile IDs
        self.running_profiles = set()
        self.checked_profiles = {}
        
        # Configure Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Profiles table expands to fill height
        
        self.setup_header()
        self.setup_controls()
        self.setup_profiles_table()
        self.setup_log_panel()
        self.setup_footer()
        
        # Load initial profiles from file
        self.refresh_profiles_list()
        
        # Subscribe to logger updates
        logger.add_listener(self.append_log_message)
        
        # Make sure browsers close on window exit
        self.protocol("WM_DELETE_WINDOW", self.on_close_app)

    def setup_header(self):
        """Builds header label with application title."""
        header_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_BG, height=60, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_lbl = ctk.CTkLabel(
            header_frame, 
            text="🌐 CN BROWSER MULTI-CONTROL", 
            font=FONT_TITLE, 
            text_color=COLOR_PRIMARY
        )
        title_lbl.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        subtitle_lbl = ctk.CTkLabel(
            header_frame, 
            text="Powered by Playwright & CustomTkinter", 
            font=FONT_TEXT, 
            text_color=COLOR_TEXT_MUTED
        )
        subtitle_lbl.grid(row=0, column=1, padx=20, pady=10, sticky="e")

    def setup_controls(self):
        """Builds control panel: Link Input, Delay setting, Run/Stop Group actions, Grid alignment."""
        controls_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_BG, corner_radius=8)
        controls_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        
        controls_frame.grid_columnconfigure(0, weight=1)
        
        # Row 0: Link Input
        link_lbl = ctk.CTkLabel(controls_frame, text="Video / Website Link:", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN)
        link_lbl.grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        
        self.link_entry = ctk.CTkEntry(
            controls_frame, 
            placeholder_text="Paste Facebook video URL here...", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.link_entry.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")
        
        # Row 1: Delay and Grid Controls
        delay_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        delay_frame.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        
        delay_lbl = ctk.CTkLabel(delay_frame, text="Delay (seconds):", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        delay_lbl.grid(row=0, column=0, padx=(0, 5), pady=5)
        
        # Load global delay
        settings = load_settings()
        init_delay = str(settings.get("global_delay", DEFAULT_DELAY_SEC))
        
        self.delay_entry = ctk.CTkEntry(
            delay_frame, 
            width=50, 
            placeholder_text=init_delay, 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.delay_entry.insert(0, init_delay)
        self.delay_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Window Grid checkbox toggle
        self.tile_on_launch_var = ctk.StringVar(value="off")
        tile_cb = ctk.CTkCheckBox(
            delay_frame, 
            text="Tile Windows on Launch", 
            font=FONT_TEXT_BOLD,
            text_color=COLOR_TEXT_MAIN,
            variable=self.tile_on_launch_var,
            onvalue="on",
            offvalue="off"
        )
        tile_cb.grid(row=0, column=2, padx=10, pady=5)

        # Small Window checkbox toggle
        self.small_window_var = ctk.StringVar(value="off")
        small_cb = ctk.CTkCheckBox(
            delay_frame, 
            text="Small Window (Portrait)", 
            font=FONT_TEXT_BOLD,
            text_color=COLOR_TEXT_MAIN,
            variable=self.small_window_var,
            onvalue="on",
            offvalue="off"
        )
        small_cb.grid(row=0, column=3, padx=10, pady=5)

        # Mobile Viewport checkbox toggle
        self.mobile_mode_var = ctk.StringVar(value="off")
        mobile_cb = ctk.CTkCheckBox(
            delay_frame, 
            text="Emulate Mobile (User-Agent)", 
            font=FONT_TEXT_BOLD,
            text_color=COLOR_TEXT_MAIN,
            variable=self.mobile_mode_var,
            onvalue="on",
            offvalue="off"
        )
        mobile_cb.grid(row=0, column=4, padx=10, pady=5)
        
        # Row 1: Action Buttons
        actions_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        actions_frame.grid(row=2, column=1, padx=15, pady=10, sticky="e")
        
        btn_start_selected = ctk.CTkButton(
            actions_frame, 
            text="▶️ Launch Checked", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_PRIMARY,
            hover_color="#5B85DB",
            text_color=COLOR_BG,
            width=130,
            command=self.on_launch_checked_clicked
        )
        btn_start_selected.grid(row=0, column=0, padx=5, pady=5)
        
        btn_open_link = ctk.CTkButton(
            actions_frame, 
            text="🔗 Open Link", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_SUCCESS,
            hover_color="#82B350",
            text_color=COLOR_BG,
            width=110,
            command=self.on_open_link_clicked
        )
        btn_open_link.grid(row=0, column=1, padx=5, pady=5)
        
        btn_stop_selected = ctk.CTkButton(
            actions_frame, 
            text="⏹️ Stop Checked", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_DANGER,
            hover_color="#D85C73",
            text_color=COLOR_BG,
            width=130,
            command=self.on_stop_checked_clicked
        )
        btn_stop_selected.grid(row=0, column=2, padx=5, pady=5)

    def setup_profiles_table(self):
        """Builds the table list showing profiles, checkmarks, proxies, status, and action buttons."""
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)
        
        # Table Header
        header_row = ctk.CTkFrame(table_container, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header_row.grid_columnconfigure(1, weight=3) # Profile Name
        header_row.grid_columnconfigure(2, weight=2) # Proxy
        header_row.grid_columnconfigure(3, weight=1) # Status
        header_row.grid_columnconfigure(4, weight=2) # Actions
        
        self.select_all_var = ctk.StringVar(value="off")
        select_all_cb = ctk.CTkCheckBox(
            header_row, 
            text="", 
            width=30,
            variable=self.select_all_var,
            onvalue="on",
            offvalue="off",
            command=self.on_select_all_toggled
        )
        select_all_cb.grid(row=0, column=0, padx=(10, 0))
        
        ctk.CTkLabel(header_row, text="Profile Name", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN, anchor="w").grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header_row, text="Proxy Configuration", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN, anchor="w").grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(header_row, text="Status", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN, anchor="w").grid(row=0, column=3, padx=10, sticky="w")
        ctk.CTkLabel(header_row, text="Actions", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN).grid(row=0, column=4, padx=10)
        
        # Scrollable rows list
        self.scrollable_frame = ctk.CTkScrollableFrame(
            table_container, 
            fg_color=COLOR_PANEL_BG, 
            scrollbar_button_color=COLOR_TEXT_MUTED,
            scrollbar_button_hover_color=COLOR_PRIMARY
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(1, weight=3)
        self.scrollable_frame.grid_columnconfigure(2, weight=2)
        self.scrollable_frame.grid_columnconfigure(3, weight=1)
        self.scrollable_frame.grid_columnconfigure(4, weight=2)

    def setup_log_panel(self):
        """Builds scrollable log list at the bottom."""
        log_container = ctk.CTkFrame(self, fg_color=COLOR_PANEL_BG, corner_radius=8, height=120)
        log_container.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="ew")
        log_container.grid_columnconfigure(0, weight=1)
        log_row = log_container.grid_rowconfigure(1, weight=1)
        
        log_title = ctk.CTkLabel(log_container, text="System Activity Logs:", font=FONT_TEXT_BOLD, text_color=COLOR_PRIMARY)
        log_title.grid(row=0, column=0, padx=15, pady=(5, 0), sticky="w")
        
        self.log_textbox = ctk.CTkTextbox(
            log_container, 
            fg_color=COLOR_BG, 
            text_color=COLOR_TEXT_MAIN, 
            font=FONT_CODE, 
            height=100,
            corner_radius=4
        )
        self.log_textbox.grid(row=1, column=0, padx=15, pady=(5, 10), sticky="ew")
        self.log_textbox.configure(state="disabled")

    def setup_footer(self):
        """Footer with Add Profile and clear logs buttons."""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=4, column=0, padx=20, pady=(5, 15), sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1)
        
        add_profile_btn = ctk.CTkButton(
            footer_frame, 
            text="➕ Add Chrome Profile", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_PRIMARY,
            hover_color="#5B85DB",
            text_color=COLOR_BG,
            command=self.on_add_profile_clicked
        )
        add_profile_btn.grid(row=0, column=0, sticky="w")
        
        clear_logs_btn = ctk.CTkButton(
            footer_frame, 
            text="🧹 Clear Logs", 
            font=FONT_TEXT,
            fg_color="transparent",
            hover_color=COLOR_PANEL_BG,
            text_color=COLOR_TEXT_MUTED,
            border_width=1,
            border_color=COLOR_TEXT_MUTED,
            command=self.on_clear_logs_clicked
        )
        clear_logs_btn.grid(row=0, column=2, sticky="e")

    # --- UI Refresh Logic ---
    
    def refresh_profiles_list(self):
        """Loads profiles from settings.json and redraws the rows inside scrollable frame."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        settings = load_settings()
        profiles = settings.get("profiles", [])
        
        self.checked_profiles = {}
        
        if not profiles:
            empty_lbl = ctk.CTkLabel(
                self.scrollable_frame, 
                text="No profiles added yet. Click 'Add Chrome Profile' below.", 
                font=FONT_TEXT, 
                text_color=COLOR_TEXT_MUTED
            )
            empty_lbl.grid(row=0, column=0, columnspan=5, padx=20, pady=40)
            return

        for index, profile in enumerate(profiles):
            profile_id = profile["id"]
            name = profile["name"]
            proxy = profile.get("proxy") or "No Proxy"
            is_running = profile_id in self.running_profiles
            
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            row_frame.grid(row=index, column=0, columnspan=5, sticky="ew", pady=4)
            row_frame.grid_columnconfigure(1, weight=3)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=1)
            row_frame.grid_columnconfigure(4, weight=2)
            
            cb_var = ctk.StringVar(value="off")
            self.checked_profiles[profile_id] = cb_var
            cb = ctk.CTkCheckBox(row_frame, text="", width=30, variable=cb_var, onvalue="on", offvalue="off")
            cb.grid(row=0, column=0, padx=(10, 0))
            
            name_lbl = ctk.CTkLabel(row_frame, text=name, font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN, anchor="w")
            name_lbl.grid(row=0, column=1, padx=10, sticky="w")
            
            proxy_lbl = ctk.CTkLabel(row_frame, text=proxy, font=FONT_TEXT, text_color=COLOR_TEXT_MUTED, anchor="w")
            proxy_lbl.grid(row=0, column=2, padx=10, sticky="w")
            
            status_text = "● Running" if is_running else "○ Stopped"
            status_color = COLOR_SUCCESS if is_running else COLOR_TEXT_MUTED
            status_lbl = ctk.CTkLabel(row_frame, text=status_text, font=FONT_TEXT_BOLD, text_color=status_color, anchor="w")
            status_lbl.grid(row=0, column=3, padx=10, sticky="w")
            
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=4, padx=10)
            
            if is_running:
                action_btn = ctk.CTkButton(
                    actions_frame, 
                    text="Stop", 
                    width=60, 
                    height=24,
                    fg_color=COLOR_DANGER,
                    hover_color="#D85C73",
                    text_color=COLOR_BG,
                    font=FONT_TEXT_BOLD,
                    command=lambda pid=profile_id: self.toggle_profile_run(pid)
                )
            else:
                action_btn = ctk.CTkButton(
                    actions_frame, 
                    text="Run", 
                    width=60, 
                    height=24,
                    fg_color=COLOR_PRIMARY,
                    hover_color="#5B85DB",
                    text_color=COLOR_BG,
                    font=FONT_TEXT_BOLD,
                    command=lambda pid=profile_id: self.toggle_profile_run(pid)
                )
            action_btn.grid(row=0, column=0, padx=2)
            
            delete_btn = ctk.CTkButton(
                actions_frame, 
                text="🗑️", 
                width=30, 
                height=24,
                fg_color="transparent",
                hover_color="#3A2A35",
                text_color=COLOR_DANGER,
                font=FONT_TEXT,
                command=lambda pid=profile_id: self.on_delete_profile_clicked(pid)
            )
            delete_btn.grid(row=0, column=1, padx=2)

    # --- Threads & Status Callbacks ---

    def on_browser_status_changed(self, profile_id: str, is_running: bool = False):
        """Thread-safe callback to register browser status and update GUI list."""
        def update_gui():
            if is_running:
                self.running_profiles.add(profile_id)
            else:
                if profile_id in self.running_profiles:
                    self.running_profiles.remove(profile_id)
                    settings = load_settings()
                    p_name = next((p["name"] for p in settings.get("profiles", []) if p["id"] == profile_id), "Unknown")
                    logger.log(f"Browser window '{p_name}' closed.")
            self.refresh_profiles_list()

        # Queue changes and redraw on main UI thread safely
        self.after(0, update_gui)

    def append_log_message(self, message: str):
        """Listens to logger calls and appends them to the textbox."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    # --- Actions / Event Handlers ---

    def on_add_profile_clicked(self):
        """Opens popup dialog to create new profile."""
        AddProfileDialog(self, self.save_new_profile)

    def save_new_profile(self, profile_data: dict):
        """Callback from AddProfileDialog to save the new profile."""
        new_prof = add_profile(profile_data)
        logger.log(f"Profile '{new_prof['name']}' created.")
        self.refresh_profiles_list()

    def on_delete_profile_clicked(self, profile_id: str):
        """Deletes selected profile if it is not running."""
        if profile_id in self.running_profiles:
            logger.log("Error: Cannot delete profile because it is currently running. Please stop it first.")
            return
            
        settings = load_settings()
        name = next((p["name"] for p in settings.get("profiles", []) if p["id"] == profile_id), "Unknown")
        delete_profile(profile_id)
        
        logger.log(f"Profile '{name}' and its local directory files deleted.")
        self.refresh_profiles_list()

    def toggle_profile_run(self, profile_id: str):
        """Starts or stops an individual profile in a background worker."""
        if profile_id in self.running_profiles:
            logger.log(f"Closing browser for profile ID: {profile_id}...")
            self.manager.close_instance(profile_id)
        else:
            settings = load_settings()
            profile = next((p for p in settings.get("profiles", []) if p["id"] == profile_id), None)
            if profile:
                delay = 0
                tile = self.tile_on_launch_var.get() == "on"
                small_window = self.small_window_var.get() == "on"
                mobile_mode = self.mobile_mode_var.get() == "on"
                
                # Fetch screen info for grid calculations
                screen_w = self.winfo_screenwidth()
                screen_h = self.winfo_screenheight()
                
                # Use LaunchWorker to launch a single profile cleanly in background
                LaunchWorker(
                    selected_profiles=[profile],
                    delay_sec=delay,
                    manager=self.manager,
                    screen_w=screen_w,
                    screen_h=screen_h,
                    tile=tile,
                    small_window=small_window,
                    mobile_mode=mobile_mode,
                    on_launch_callback=self.on_browser_status_changed
                ).start()

    def on_select_all_toggled(self):
        """Toggles checkboxes of all loaded profiles."""
        state = self.select_all_var.get()
        new_val = "on" if state == "on" else "off"
        for cb_var in self.checked_profiles.values():
            cb_var.set(new_val)

    def on_launch_checked_clicked(self):
        """Launches all selected profiles using background thread worker."""
        checked_ids = [pid for pid, var in self.checked_profiles.items() if var.get() == "on"]
        
        # Filter profiles that are not running already
        profiles_to_launch = []
        settings = load_settings()
        for p in settings.get("profiles", []):
            if p["id"] in checked_ids and p["id"] not in self.running_profiles:
                profiles_to_launch.append(p)
                
        if not profiles_to_launch:
            logger.log("Warning: No checked profiles need launching.")
            return
            
        delay = self.get_delay_seconds()
        tile = self.tile_on_launch_var.get() == "on"
        small_window = self.small_window_var.get() == "on"
        mobile_mode = self.mobile_mode_var.get() == "on"
        
        # Save delay setting globally
        settings["global_delay"] = delay
        save_settings(settings)
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        logger.log(f"Starting background LaunchWorker for {len(profiles_to_launch)} browser(s)...")
        LaunchWorker(
            selected_profiles=profiles_to_launch,
            delay_sec=delay,
            manager=self.manager,
            screen_w=screen_w,
            screen_h=screen_h,
            tile=tile,
            small_window=small_window,
            mobile_mode=mobile_mode,
            on_launch_callback=self.on_browser_status_changed
        ).start()

    def on_stop_checked_clicked(self):
        """Stops all checked browser instances."""
        checked_ids = [pid for pid, var in self.checked_profiles.items() if var.get() == "on"]
        
        active_checked = [pid for pid in checked_ids if pid in self.running_profiles]
        if not active_checked:
            logger.log("Warning: No checked profiles are currently running.")
            return
            
        logger.log(f"Stopping {len(active_checked)} browser(s)...")
        for pid in active_checked:
            self.manager.close_instance(pid)

    def on_open_link_clicked(self):
        """Triggers background NavigationWorker to open the link in all checked and running browsers."""
        link = self.link_entry.get().strip()
        if not link:
            logger.log("Error: Please enter a valid URL in the text entry field first!")
            return
            
        checked_ids = [pid for pid, var in self.checked_profiles.items() if var.get() == "on"]
        active_instances = [self.manager.active_instances[pid] for pid in checked_ids if pid in self.manager.active_instances]
        
        if not active_instances:
            logger.log("Warning: None of the checked profiles are currently running. Launch browsers first.")
            return
            
        delay = self.get_delay_seconds()
        logger.log(f"Starting background NavigationWorker to open URL: {link}...")
        
        NavigationWorker(
            active_instances=active_instances,
            url=link,
            delay_sec=delay
        ).start()

    def on_clear_logs_clicked(self):
        """Clears log console window."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def get_delay_seconds(self) -> float:
        """Retrieves and parses delay entry, defaults to DEFAULT_DELAY_SEC on error."""
        try:
            val = float(self.delay_entry.get().strip())
            return val if val >= 0 else 0
        except Exception:
            return DEFAULT_DELAY_SEC

    def on_close_app(self):
        """Cleans up and closes all browsers before exiting."""
        logger.log("Closing all browsers before exit...")
        self.manager.close_all()
        
        # Wait up to 3 seconds for all browser instances to close cleanly
        start_time = time.time()
        while self.manager.active_instances and (time.time() - start_time) < 3.0:
            self.update()
            time.sleep(0.1)
            
        self.destroy()
