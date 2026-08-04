import customtkinter as ctk
import time
import threading
from tkinter import filedialog
from app.gui.styles import *
from app.gui.dialogs import AddProfileDialog, EditProfileDialog, BulkAddProfilesDialog
from app.utils.file_helper import load_settings, save_settings, add_profile, delete_profile, update_profile
from app.utils.logger import logger
from app.automation.manager import ChromeGroupManager
from app.automation.worker import LaunchWorker, NavigationWorker, AutomationTaskWorker, BatchAutomationWorker
from app.config import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, DEFAULT_DELAY_SEC

class DashboardApp(ctk.CTk):
    """Main Dashboard Window for Facebook Chrome Multi-Control (Mass Batch Automation Engine)."""
    def __init__(self):
        super().__init__()
        self.title("🌐 CN Browser - Facebook Chrome Multi-Control")
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.configure(fg_color=COLOR_BG)
        
        # Initialize browser automation manager
        self.manager = ChromeGroupManager()
        
        # Keep track of active profile IDs and workers
        self.running_profiles = set()
        self.checked_profiles = {}
        self.active_profile_ips = {}
        self.current_batch_worker = None
        
        # Grid Layout: Row 0 Header, Row 1 Body (2 Columns: 60% Left / 40% Right)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_header()
        self.setup_main_body()
        
        # Load initial profiles from file
        self.refresh_profiles_list()
        
        # Subscribe to logger updates
        logger.add_listener(self.append_log_message)
        
        # Make sure browsers close on window exit
        self.protocol("WM_DELETE_WINDOW", self.on_close_app)

    def setup_header(self):
        """Builds top header bar."""
        header_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_BG, height=55, corner_radius=0)
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
            text="Playwright & CustomTkinter Dashboard", 
            font=FONT_TEXT, 
            text_color=COLOR_TEXT_MUTED
        )
        subtitle_lbl.grid(row=0, column=1, padx=20, pady=10, sticky="e")

    def setup_main_body(self):
        """Creates the 2-Column Split Body Layout (Column 0: 60% Left, Column 1: 40% Right)."""
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        # 60% Left / 40% Right Column Weights (Fixed Lock with uniform)
        body_frame.grid_columnconfigure(0, weight=6, uniform="body_cols")
        body_frame.grid_columnconfigure(1, weight=4, uniform="body_cols")
        body_frame.grid_rowconfigure(0, weight=1)
        
        # --- LEFT COLUMN (60% Width) ---
        self.left_frame = ctk.CTkFrame(body_frame, fg_color=COLOR_PANEL_BG, corner_radius=10)
        self.left_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)
        
        self.setup_left_panel(self.left_frame)
        
        # --- RIGHT COLUMN (40% Width) ---
        self.right_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=6, uniform="right_rows")  # Top Card 60% Height
        self.right_frame.grid_rowconfigure(1, weight=4, uniform="right_rows")  # Log Card 40% Height
        
        self.setup_right_panel(self.right_frame)

    def setup_left_panel(self, parent):
        """Builds Left Panel: Profile Toolbar, Launch Options, Batch Controls, and Profile Table."""
        toolbar_container = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar_container.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        toolbar_container.grid_columnconfigure(0, weight=1)
        
        # Row 0: Add Profile & Group Launch/Stop Action Buttons
        top_row_frame = ctk.CTkFrame(toolbar_container, fg_color="transparent")
        top_row_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_row_frame.grid_columnconfigure(1, weight=1)
        
        add_profile_btn = ctk.CTkButton(
            top_row_frame, 
            text="➕ Add Profile", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_PRIMARY,
            hover_color="#5B85DB",
            text_color=COLOR_BG,
            width=120,
            command=self.on_add_profile_clicked
        )
        add_profile_btn.grid(row=0, column=0, sticky="w")
        
        bulk_add_btn = ctk.CTkButton(
            top_row_frame, 
            text="📦 Bulk Add Profiles", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_SECONDARY,
            hover_color="#A37DF2",
            text_color=COLOR_BG,
            width=150,
            command=self.on_bulk_add_profiles_clicked
        )
        bulk_add_btn.grid(row=0, column=1, padx=(6, 0), sticky="w")
        
        group_btns_frame = ctk.CTkFrame(top_row_frame, fg_color="transparent")
        group_btns_frame.grid(row=0, column=2, sticky="e")
        
        btn_start_selected = ctk.CTkButton(
            group_btns_frame, 
            text="▶️ Launch Checked", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_PRIMARY,
            hover_color="#5B85DB",
            text_color=COLOR_BG,
            width=125,
            command=self.on_launch_checked_clicked
        )
        btn_start_selected.grid(row=0, column=0, padx=4)
        
        btn_stop_selected = ctk.CTkButton(
            group_btns_frame, 
            text="⏹️ Stop Checked", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_DANGER,
            hover_color="#D85C73",
            text_color=COLOR_BG,
            width=125,
            command=self.on_stop_checked_clicked
        )
        btn_stop_selected.grid(row=0, column=1, padx=4)
        
        # Row 1: Launch Options Frame (Delay, Batch Controls, Window Flags)
        opts_card = ctk.CTkFrame(toolbar_container, fg_color=COLOR_CARD_BG, corner_radius=8)
        opts_card.grid(row=1, column=0, sticky="ew")
        
        settings = load_settings()
        
        raw_delay = settings.get("global_delay", DEFAULT_DELAY_SEC)
        try:
            d_val = float(raw_delay)
            init_delay = str(int(d_val)) if d_val.is_integer() else str(d_val)
        except Exception:
            init_delay = str(DEFAULT_DELAY_SEC)
            
        init_batch_size = str(settings.get("batch_size", 5))
        
        raw_rest = settings.get("batch_rest", 15)
        try:
            r_val = float(raw_rest)
            init_batch_rest = str(int(r_val)) if r_val.is_integer() else str(r_val)
        except Exception:
            init_batch_rest = "15"

        raw_watch = settings.get("watch_time", 10)
        try:
            w_val = float(raw_watch)
            init_watch_time = str(int(w_val)) if w_val.is_integer() else str(w_val)
        except Exception:
            init_watch_time = "10"
        
        # Row 1 Options: Mass Automation & Timing Controls (Flow Order)
        delay_lbl = ctk.CTkLabel(opts_card, text="Delay (sec):", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        delay_lbl.grid(row=0, column=0, padx=(10, 2), pady=(6, 3), sticky="w")
        
        self.delay_entry = ctk.CTkEntry(
            opts_card, width=42, placeholder_text=init_delay, font=FONT_TEXT,
            fg_color=COLOR_BG, text_color=COLOR_TEXT_MAIN, border_color=COLOR_PANEL_BG
        )
        self.delay_entry.insert(0, init_delay)
        self.delay_entry.grid(row=0, column=1, padx=(0, 10), pady=(6, 3), sticky="w")
        self.delay_entry.bind("<KeyRelease>", lambda event: self.save_current_automation_state())
        
        batch_lbl = ctk.CTkLabel(opts_card, text="Batch Size:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        batch_lbl.grid(row=0, column=2, padx=(5, 2), pady=(6, 3), sticky="w")
        
        self.batch_size_entry = ctk.CTkEntry(
            opts_card, width=42, placeholder_text="5", font=FONT_TEXT,
            fg_color=COLOR_BG, text_color=COLOR_TEXT_MAIN, border_color=COLOR_PANEL_BG
        )
        self.batch_size_entry.insert(0, init_batch_size)
        self.batch_size_entry.grid(row=0, column=3, padx=(0, 10), pady=(6, 3), sticky="w")
        self.batch_size_entry.bind("<KeyRelease>", lambda event: self.save_current_automation_state())
        
        rest_lbl = ctk.CTkLabel(opts_card, text="Batch Rest (s):", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        rest_lbl.grid(row=0, column=4, padx=(5, 2), pady=(6, 3), sticky="w")
        
        self.batch_rest_entry = ctk.CTkEntry(
            opts_card, width=42, placeholder_text="15", font=FONT_TEXT,
            fg_color=COLOR_BG, text_color=COLOR_TEXT_MAIN, border_color=COLOR_PANEL_BG
        )
        self.batch_rest_entry.insert(0, init_batch_rest)
        self.batch_rest_entry.grid(row=0, column=5, padx=(0, 10), pady=(6, 3), sticky="w")
        self.batch_rest_entry.bind("<KeyRelease>", lambda event: self.save_current_automation_state())
        
        watch_lbl = ctk.CTkLabel(opts_card, text="Watch Video (s):", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        watch_lbl.grid(row=0, column=6, padx=(5, 2), pady=(6, 3), sticky="w")
        
        self.watch_time_entry = ctk.CTkEntry(
            opts_card, width=42, placeholder_text="10", font=FONT_TEXT,
            fg_color=COLOR_BG, text_color=COLOR_TEXT_MAIN, border_color=COLOR_PANEL_BG
        )
        self.watch_time_entry.insert(0, init_watch_time)
        self.watch_time_entry.grid(row=0, column=7, padx=(0, 10), pady=(6, 3), sticky="w")
        self.watch_time_entry.bind("<KeyRelease>", lambda event: self.save_current_automation_state())
        
        # Row 2 Options: Window Layout & Device Emulation Toggles
        self.tile_on_launch_var = ctk.StringVar(value="off")
        tile_cb = ctk.CTkCheckBox(
            opts_card, text="Tile Windows", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN,
            variable=self.tile_on_launch_var, onvalue="on", offvalue="off"
        )
        tile_cb.grid(row=1, column=0, columnspan=2, padx=(10, 8), pady=(2, 6), sticky="w")
        
        self.small_window_var = ctk.StringVar(value="off")
        small_cb = ctk.CTkCheckBox(
            opts_card, text="Small Window", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN,
            variable=self.small_window_var, onvalue="on", offvalue="off"
        )
        small_cb.grid(row=1, column=2, columnspan=2, padx=(5, 8), pady=(2, 6), sticky="w")
        
        self.mobile_mode_var = ctk.StringVar(value="off")
        mobile_cb = ctk.CTkCheckBox(
            opts_card, text="Emulate Mobile", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN,
            variable=self.mobile_mode_var, onvalue="on", offvalue="off"
        )
        mobile_cb.grid(row=1, column=4, columnspan=3, padx=(5, 8), pady=(2, 6), sticky="w")
        
        # Row 1: Profile Table Container
        table_container = ctk.CTkFrame(parent, fg_color="transparent")
        table_container.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)
        
        # Table Header
        header_row = ctk.CTkFrame(table_container, fg_color=COLOR_CARD_BG, corner_radius=6, height=36)
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        header_row.grid_columnconfigure(1, weight=3)
        header_row.grid_columnconfigure(2, weight=2)
        header_row.grid_columnconfigure(3, weight=1)
        header_row.grid_columnconfigure(4, weight=2)
        
        self.select_all_var = ctk.StringVar(value="off")
        select_all_cb = ctk.CTkCheckBox(
            header_row, 
            text="", 
            width=24,
            variable=self.select_all_var,
            onvalue="on",
            offvalue="off",
            command=self.on_select_all_toggled
        )
        select_all_cb.grid(row=0, column=0, padx=(10, 0), pady=6)
        
        ctk.CTkLabel(header_row, text="Profile Name", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN, anchor="w").grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header_row, text="Proxy / IP & Geolocation", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN, anchor="w").grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(header_row, text="Status", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN, anchor="w").grid(row=0, column=3, padx=10, sticky="w")
        ctk.CTkLabel(header_row, text="Actions", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN).grid(row=0, column=4, padx=10)
        
        # Scrollable rows list
        self.scrollable_frame = ctk.CTkScrollableFrame(
            table_container, 
            fg_color="transparent", 
            scrollbar_button_color=COLOR_TEXT_MUTED,
            scrollbar_button_hover_color=COLOR_PRIMARY
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(1, weight=3)
        self.scrollable_frame.grid_columnconfigure(2, weight=2)
        self.scrollable_frame.grid_columnconfigure(3, weight=1)
        self.scrollable_frame.grid_columnconfigure(4, weight=2)

    def setup_right_panel(self, parent):
        """Builds Right Panel: Unified Multi-Action Automation Panel, Progress Bar, & System Log Card."""
        # Row 0: Unified Automation Panel
        controls_card = ctk.CTkFrame(parent, fg_color=COLOR_PANEL_BG, corner_radius=10)
        controls_card.grid(row=0, column=0, padx=0, pady=(0, 5), sticky="nsew")
        controls_card.grid_columnconfigure(0, weight=1)
        
        card_title = ctk.CTkLabel(
            controls_card, 
            text="⚙️ Facebook Multi-Action Automation", 
            font=FONT_SUBTITLE, 
            text_color=COLOR_PRIMARY
        )
        card_title.grid(row=0, column=0, padx=15, pady=(10, 4), sticky="w")
        
        # Target Link Input
        link_lbl = ctk.CTkLabel(controls_card, text="Target URL (Post / Page / Profile Link):", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN)
        link_lbl.grid(row=1, column=0, padx=15, pady=(2, 2), sticky="w")
        
        settings = load_settings()
        saved_url = settings.get("target_url", "")
        
        self.target_url_entry = ctk.CTkEntry(
            controls_card, 
            placeholder_text="Paste Facebook Post, Page, or Profile URL...", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_CARD_BG
        )
        if saved_url:
            self.target_url_entry.insert(0, saved_url)
        self.target_url_entry.grid(row=2, column=0, padx=15, pady=(0, 6), sticky="ew")
        self.target_url_entry.bind("<KeyRelease>", lambda event: self.save_current_automation_state())
        
        # Checkboxes Bar (Auto Follow, Auto Like, Auto Comment, Auto Share)
        cb_bar = ctk.CTkFrame(controls_card, fg_color=COLOR_CARD_BG, corner_radius=8)
        cb_bar.grid(row=3, column=0, padx=15, pady=4, sticky="ew")
        cb_bar.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.chk_follow_var = ctk.StringVar(value="off")
        self.chk_like_var = ctk.StringVar(value="off")
        self.chk_comment_var = ctk.StringVar(value="off")
        self.chk_share_var = ctk.StringVar(value="off")
        
        chk_follow = ctk.CTkCheckBox(
            cb_bar, text="Auto Follow", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN,
            variable=self.chk_follow_var, onvalue="on", offvalue="off",
            command=self.on_follow_checkbox_toggled
        )
        chk_follow.grid(row=0, column=0, padx=8, pady=8)
        
        chk_like = ctk.CTkCheckBox(
            cb_bar, text="Auto Like", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN,
            variable=self.chk_like_var, onvalue="on", offvalue="off",
            command=self.on_combination_checkbox_toggled
        )
        chk_like.grid(row=0, column=1, padx=8, pady=8)
        
        chk_comment = ctk.CTkCheckBox(
            cb_bar, text="Auto Comment", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN,
            variable=self.chk_comment_var, onvalue="on", offvalue="off",
            command=self.on_combination_checkbox_toggled
        )
        chk_comment.grid(row=0, column=2, padx=8, pady=8)
        
        chk_share = ctk.CTkCheckBox(
            cb_bar, text="Auto Share", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN,
            variable=self.chk_share_var, onvalue="on", offvalue="off",
            command=self.on_combination_checkbox_toggled
        )
        chk_share.grid(row=0, column=3, padx=8, pady=8)
        
        # Details Container Frame for dynamic sub-options
        self.details_container = ctk.CTkFrame(controls_card, fg_color="transparent")
        self.details_container.grid(row=4, column=0, padx=15, pady=4, sticky="ew")
        self.details_container.grid_columnconfigure(0, weight=1)
        
        # Build Option Sub-Frames (Follow, Like, Comment, Share)
        self.setup_detail_frames(self.details_container)
        
        # Action Buttons Container (Start Automation & Quick Open Link)
        btns_frame = ctk.CTkFrame(controls_card, fg_color="transparent")
        btns_frame.grid(row=5, column=0, padx=15, pady=(6, 8), sticky="ew")
        btns_frame.grid_columnconfigure(0, weight=1)
        btns_frame.grid_columnconfigure(1, weight=1)
        
        btn_open_link = ctk.CTkButton(
            btns_frame, 
            text="🔗 Open Link Only", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_CARD_BG,
            hover_color="#2F354F",
            text_color=COLOR_TEXT_MAIN,
            height=34,
            command=self.on_open_link_clicked
        )
        btn_open_link.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        
        btn_start_task = ctk.CTkButton(
            btns_frame, 
            text="▶️ Start Multi-Automation Task", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_SUCCESS,
            hover_color="#82B350",
            text_color=COLOR_BG,
            height=34,
            command=self.on_start_multi_automation_clicked
        )
        btn_start_task.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # Progress Bar Container
        prog_frame = ctk.CTkFrame(controls_card, fg_color="transparent")
        prog_frame.grid(row=6, column=0, padx=15, pady=(0, 10), sticky="ew")
        prog_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_lbl = ctk.CTkLabel(prog_frame, text="Progress: Ready (0 / 0 Profiles)", font=FONT_TEXT, text_color=COLOR_TEXT_MUTED)
        self.progress_lbl.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        self.progress_bar = ctk.CTkProgressBar(prog_frame, height=8, fg_color=COLOR_CARD_BG, progress_color=COLOR_PRIMARY)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, sticky="ew")

        # Row 1: System Activity Log Card
        log_card = ctk.CTkFrame(parent, fg_color=COLOR_PANEL_BG, corner_radius=10)
        log_card.grid(row=1, column=0, padx=0, pady=(5, 0), sticky="nsew")
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)
        
        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.grid(row=0, column=0, padx=15, pady=(8, 4), sticky="ew")
        log_header.grid_columnconfigure(0, weight=1)
        
        log_title = ctk.CTkLabel(log_header, text="📜 System Activity Logs", font=FONT_SUBTITLE, text_color=COLOR_PRIMARY)
        log_title.grid(row=0, column=0, sticky="w")
        
        clear_logs_btn = ctk.CTkButton(
            log_header, 
            text="🧹 Clear Logs", 
            font=FONT_TEXT,
            fg_color="transparent",
            hover_color=COLOR_CARD_BG,
            text_color=COLOR_TEXT_MUTED,
            border_width=1,
            border_color=COLOR_TEXT_MUTED,
            width=90,
            height=24,
            command=self.on_clear_logs_clicked
        )
        clear_logs_btn.grid(row=0, column=1, sticky="e")
        
        self.log_textbox = ctk.CTkTextbox(
            log_card, 
            fg_color=COLOR_BG, 
            text_color=COLOR_TEXT_MAIN, 
            font=FONT_CODE, 
            corner_radius=6
        )
        self.log_textbox.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="nsew")
        self.log_textbox.configure(state="disabled")

    def setup_detail_frames(self, parent):
        """Builds detail option frames for Follow, Like, Comment, and Share with high-contrast styling."""
        # 1. Follow Details Frame
        self.frame_follow_opts = ctk.CTkFrame(parent, fg_color=COLOR_SUB_CARD_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BG)
        self.frame_follow_opts.grid_columnconfigure(4, weight=1)
        
        self.follow_target_type_var = ctk.StringVar(value="USER")
        rb_user = ctk.CTkRadioButton(self.frame_follow_opts, text="Follow User", value="USER", variable=self.follow_target_type_var, font=FONT_TEXT_BOLD, text_color=COLOR_RADIO_TEXT)
        rb_user.grid(row=0, column=0, padx=8, pady=6)
        rb_page = ctk.CTkRadioButton(self.frame_follow_opts, text="Follow Page", value="PAGE", variable=self.follow_target_type_var, font=FONT_TEXT_BOLD, text_color=COLOR_RADIO_TEXT)
        rb_page.grid(row=0, column=1, padx=8, pady=6)
        
        self.chk_favorites_var = ctk.StringVar(value="on")
        chk_fav = ctk.CTkCheckBox(self.frame_follow_opts, text="Set Favorites", font=FONT_TEXT_BOLD, text_color=COLOR_RADIO_TEXT, variable=self.chk_favorites_var, onvalue="on", offvalue="off")
        chk_fav.grid(row=0, column=2, padx=8, pady=6)
        
        limit_lbl = ctk.CTkLabel(self.frame_follow_opts, text="Max/Day:", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN)
        limit_lbl.grid(row=0, column=3, padx=(10, 4), pady=6)
        self.max_follow_entry = ctk.CTkEntry(self.frame_follow_opts, width=45, placeholder_text="20", font=FONT_TEXT, fg_color=COLOR_BG, text_color=COLOR_TEXT_MAIN)
        self.max_follow_entry.insert(0, "20")
        self.max_follow_entry.grid(row=0, column=4, padx=4, pady=6, sticky="w")
        
        # 2. Like Details Frame
        self.frame_like_opts = ctk.CTkFrame(parent, fg_color=COLOR_SUB_CARD_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BG)
        self.frame_like_opts.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.frame_like_opts, text="Reactions Pool:", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN).grid(row=0, column=0, padx=(8, 4), pady=6, sticky="w")
        
        react_box_frame = ctk.CTkFrame(self.frame_like_opts, fg_color="transparent")
        react_box_frame.grid(row=0, column=1, padx=4, pady=4, sticky="w")
        
        self.react_cb_vars = {
            "LIKE": ctk.StringVar(value="on"),
            "LOVE": ctk.StringVar(value="on"),
            "HAHA": ctk.StringVar(value="on"),
            "WOW": ctk.StringVar(value="on"),
            "SAD": ctk.StringVar(value="off"),
            "ANGRY": ctk.StringVar(value="off")
        }
        
        labels_map = [("LIKE", "👍"), ("LOVE", "❤️"), ("HAHA", "😂"), ("WOW", "😮"), ("SAD", "😢"), ("ANGRY", "😡")]
        for idx, (r_key, r_emoji) in enumerate(labels_map):
            cb = ctk.CTkCheckBox(
                react_box_frame, text=r_emoji, font=FONT_EMOJI_REACTION, text_color=COLOR_RADIO_TEXT,
                variable=self.react_cb_vars[r_key], onvalue="on", offvalue="off", width=42
            )
            cb.grid(row=0, column=idx, padx=3)
            
        self.random_react_var = ctk.StringVar(value="on")
        rand_cb = ctk.CTkCheckBox(self.frame_like_opts, text="Random Reaction", font=FONT_TEXT_BOLD, text_color=COLOR_RADIO_TEXT, variable=self.random_react_var, onvalue="on", offvalue="off")
        rand_cb.grid(row=0, column=2, padx=8, pady=6)
        
        # 3. Comment Details Frame
        self.frame_comment_opts = ctk.CTkFrame(parent, fg_color=COLOR_SUB_CARD_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BG)
        self.frame_comment_opts.grid_columnconfigure(0, weight=1)
        
        cmt_hdr = ctk.CTkFrame(self.frame_comment_opts, fg_color="transparent")
        cmt_hdr.grid(row=0, column=0, padx=8, pady=(4, 2), sticky="ew")
        cmt_hdr.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(cmt_hdr, text="Comment Pool List:", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN).grid(row=0, column=0, sticky="w")
        
        import_txt_btn = ctk.CTkButton(
            cmt_hdr, text="📁 Import .txt", font=FONT_TEXT_BOLD, fg_color=COLOR_CARD_BG,
            hover_color="#2F354F", text_color=COLOR_PRIMARY, height=24, width=95,
            command=self.on_import_comments_txt_clicked
        )
        import_txt_btn.grid(row=0, column=1, padx=2, sticky="e")
        
        paste_btn = ctk.CTkButton(
            cmt_hdr, text="📋 Paste", font=FONT_TEXT_BOLD, fg_color=COLOR_CARD_BG,
            hover_color="#2F354F", text_color=COLOR_SUCCESS, height=24, width=70,
            command=self.on_paste_clipboard_clicked
        )
        paste_btn.grid(row=0, column=2, padx=2, sticky="e")
        
        sep_lbl = ctk.CTkLabel(cmt_hdr, text="Splitter:", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN)
        sep_lbl.grid(row=0, column=3, padx=(4, 2), sticky="e")
        
        settings = load_settings()
        saved_comments = settings.get("comments_text", "Great post!\nAwesome content!\nNice info!")
        saved_sep = settings.get("comment_separator", "\\n")
        saved_emoji = "on" if settings.get("add_emoji", True) else "off"

        self.comment_separator_entry = ctk.CTkEntry(
            cmt_hdr, width=45, placeholder_text="\\n", font=FONT_TEXT,
            fg_color=COLOR_BG, text_color=COLOR_TEXT_MAIN, border_color=COLOR_CARD_BG
        )
        self.comment_separator_entry.insert(0, saved_sep)
        self.comment_separator_entry.grid(row=0, column=4, padx=(0, 4), sticky="e")
        self.comment_separator_entry.bind("<KeyRelease>", lambda event: self.save_current_automation_state())
        
        self.comment_emoji_var = ctk.StringVar(value=saved_emoji)
        emoji_cb = ctk.CTkCheckBox(cmt_hdr, text="Add Emoji", font=FONT_TEXT_BOLD, text_color=COLOR_RADIO_TEXT, variable=self.comment_emoji_var, onvalue="on", offvalue="off", command=self.save_current_automation_state)
        emoji_cb.grid(row=0, column=5, sticky="e")
        
        self.comment_textbox = ctk.CTkTextbox(self.frame_comment_opts, height=95, fg_color=COLOR_BG, text_color=COLOR_TEXT_MAIN, font=FONT_TEXT)
        self.comment_textbox.insert("1.0", saved_comments)
        self.comment_textbox.grid(row=1, column=0, padx=8, pady=(0, 6), sticky="ew")
        self.comment_textbox.bind("<KeyRelease>", lambda event: self.save_current_automation_state())
        self.comment_textbox.bind("<Control-v>", self.on_paste_clipboard_clicked)
        self.comment_textbox.bind("<Control-V>", self.on_paste_clipboard_clicked)
        self.comment_textbox.bind("<<Paste>>", self.on_paste_clipboard_clicked)
        
        # 4. Share Details Frame
        self.frame_share_opts = ctk.CTkFrame(parent, fg_color=COLOR_SUB_CARD_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BG)
        
        ctk.CTkLabel(self.frame_share_opts, text="Share Target:", font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN).grid(row=0, column=0, padx=(8, 4), pady=6, sticky="w")
        self.share_dest_var = ctk.StringVar(value="PUBLIC")
        rb_pub = ctk.CTkRadioButton(self.frame_share_opts, text="Public Feed", value="PUBLIC", variable=self.share_dest_var, font=FONT_TEXT_BOLD, text_color=COLOR_RADIO_TEXT)
        rb_pub.grid(row=0, column=1, padx=8, pady=6)
        rb_grp = ctk.CTkRadioButton(self.frame_share_opts, text="Group", value="GROUP", variable=self.share_dest_var, font=FONT_TEXT_BOLD, text_color=COLOR_RADIO_TEXT)
        rb_grp.grid(row=0, column=2, padx=8, pady=6)
        rb_sty = ctk.CTkRadioButton(self.frame_share_opts, text="Story", value="STORY", variable=self.share_dest_var, font=FONT_TEXT_BOLD, text_color=COLOR_RADIO_TEXT)
        rb_sty.grid(row=0, column=3, padx=8, pady=6)

    # --- CHECKBOX TOGGLE LOGIC ---
    
    def on_follow_checkbox_toggled(self):
        """If Auto Follow is checked, automatically uncheck Like, Comment, Share."""
        if self.chk_follow_var.get() == "on":
            self.chk_like_var.set("off")
            self.chk_comment_var.set("off")
            self.chk_share_var.set("off")
        self.update_automation_detail_frames()

    def on_combination_checkbox_toggled(self):
        """If Like, Comment, or Share is checked, automatically uncheck Auto Follow."""
        if any([self.chk_like_var.get() == "on", self.chk_comment_var.get() == "on", self.chk_share_var.get() == "on"]):
            self.chk_follow_var.set("off")
        self.update_automation_detail_frames()

    def update_automation_detail_frames(self):
        """Shows or hides detail option frames based on checkbox states."""
        self.frame_follow_opts.grid_forget()
        self.frame_like_opts.grid_forget()
        self.frame_comment_opts.grid_forget()
        self.frame_share_opts.grid_forget()
        
        row_idx = 0
        if self.chk_follow_var.get() == "on":
            self.frame_follow_opts.grid(row=row_idx, column=0, padx=0, pady=3, sticky="ew")
            row_idx += 1
            
        if self.chk_like_var.get() == "on":
            self.frame_like_opts.grid(row=row_idx, column=0, padx=0, pady=3, sticky="ew")
            row_idx += 1
            
        if self.chk_comment_var.get() == "on":
            self.frame_comment_opts.grid(row=row_idx, column=0, padx=0, pady=3, sticky="ew")
            row_idx += 1
            
        if self.chk_share_var.get() == "on":
            self.frame_share_opts.grid(row=row_idx, column=0, padx=0, pady=3, sticky="ew")
            row_idx += 1

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
                text="No profiles added yet. Click '➕ Add Chrome Profile' above.", 
                font=FONT_TEXT, 
                text_color=COLOR_TEXT_MUTED
            )
            empty_lbl.grid(row=0, column=0, columnspan=5, padx=20, pady=40)
            return

        for index, profile in enumerate(profiles):
            profile_id = profile["id"]
            name = profile["name"]
            proxy_val = profile.get("proxy") or "No Proxy (Local IP)"
            lat = profile.get("latitude")
            lng = profile.get("longitude")
            is_running = profile_id in self.running_profiles
            
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=COLOR_CARD_BG, corner_radius=6)
            row_frame.grid(row=index, column=0, columnspan=5, sticky="ew", pady=3)
            row_frame.grid_columnconfigure(1, weight=3)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=1)
            row_frame.grid_columnconfigure(4, weight=2)
            
            cb_var = ctk.StringVar(value="off")
            self.checked_profiles[profile_id] = cb_var
            cb = ctk.CTkCheckBox(row_frame, text="", width=24, variable=cb_var, onvalue="on", offvalue="off")
            cb.grid(row=0, column=0, padx=(10, 0), pady=6)
            
            name_lbl = ctk.CTkLabel(row_frame, text=name, font=FONT_TEXT_BOLD, text_color=COLOR_TEXT_MAIN, anchor="w")
            name_lbl.grid(row=0, column=1, padx=10, sticky="w")
            
            proxy_display = proxy_val
            if lat is not None and lng is not None:
                proxy_display += f"\n📍 {lat}, {lng}"
                
            proxy_lbl = ctk.CTkLabel(row_frame, text=proxy_display, font=FONT_TEXT, text_color=COLOR_TEXT_MUTED, anchor="w", justify="left")
            proxy_lbl.grid(row=0, column=2, padx=10, sticky="w")
            
            active_ip = self.active_profile_ips.get(profile_id, "")
            if is_running:
                status_text = f"● Running\nIP: {active_ip}" if active_ip else "● Running"
            else:
                status_text = "○ Stopped"
                
            status_color = COLOR_SUCCESS if is_running else COLOR_TEXT_MUTED
            status_lbl = ctk.CTkLabel(row_frame, text=status_text, font=FONT_TEXT_BOLD, text_color=status_color, anchor="w", justify="left")
            status_lbl.grid(row=0, column=3, padx=10, sticky="w")
            
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=4, padx=8, pady=4)
            
            if is_running:
                action_btn = ctk.CTkButton(
                    actions_frame, 
                    text="Stop", 
                    width=54, 
                    height=26,
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
                    width=54, 
                    height=26,
                    fg_color=COLOR_PRIMARY,
                    hover_color="#5B85DB",
                    text_color=COLOR_BG,
                    font=FONT_TEXT_BOLD,
                    command=lambda pid=profile_id: self.toggle_profile_run(pid)
                )
            action_btn.grid(row=0, column=0, padx=2)
            
            edit_btn = ctk.CTkButton(
                actions_frame, 
                text="✏️", 
                width=32, 
                height=26,
                fg_color="transparent",
                hover_color="#2D324A",
                text_color=COLOR_PRIMARY,
                font=FONT_TEXT,
                command=lambda prof=profile: self.on_edit_profile_clicked(prof)
            )
            edit_btn.grid(row=0, column=1, padx=2)
            
            delete_btn = ctk.CTkButton(
                actions_frame, 
                text="🗑️", 
                width=32, 
                height=26,
                fg_color="transparent",
                hover_color="#3A2A35",
                text_color=COLOR_DANGER,
                font=FONT_TEXT,
                command=lambda pid=profile_id: self.on_delete_profile_clicked(pid)
            )
            delete_btn.grid(row=0, column=2, padx=2)

    # --- Threads & Status Callbacks ---

    def on_browser_status_changed(self, profile_id: str, is_running: bool = False):
        """Thread-safe callback to register browser status and update GUI list."""
        def update_gui():
            if is_running:
                self.running_profiles.add(profile_id)
                def fetch_ip():
                    import time
                    time.sleep(1.0)
                    inst = self.manager.active_instances.get(profile_id)
                    if inst:
                        ip = inst.fetch_active_ip()
                        if ip:
                            self.active_profile_ips[profile_id] = ip
                            self.after(0, self.refresh_profiles_list)
                threading.Thread(target=fetch_ip, daemon=True).start()
            else:
                if profile_id in self.running_profiles:
                    self.running_profiles.remove(profile_id)
                    self.active_profile_ips.pop(profile_id, None)
                    settings = load_settings()
                    p_name = next((p["name"] for p in settings.get("profiles", []) if p["id"] == profile_id), "Unknown")
                    logger.log(f"Browser window '{p_name}' closed.")
            self.refresh_profiles_list()

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

    def on_bulk_add_profiles_clicked(self):
        """Opens popup dialog to bulk create multiple profiles."""
        BulkAddProfilesDialog(self, self.save_bulk_profiles)

    def save_bulk_profiles(self, new_profiles_list: list):
        """Callback from BulkAddProfilesDialog to save all newly created profiles."""
        created_count = 0
        for pdata in new_profiles_list:
            add_profile(pdata)
            created_count += 1
        logger.log(f"Successfully bulk created {created_count} profiles with auto Cambodia GPS!")
        self.refresh_profiles_list()

    def on_edit_profile_clicked(self, profile_data: dict):
        """Opens popup dialog to edit an existing profile."""
        if profile_data["id"] in self.running_profiles:
            logger.log("Warning: Profile is currently running. Changes will take effect on next launch.")
        EditProfileDialog(self, profile_data, lambda updated_data: self.save_edited_profile(profile_data["id"], updated_data))

    def save_edited_profile(self, profile_id: str, updated_data: dict):
        """Callback from EditProfileDialog to save profile updates."""
        updated = update_profile(profile_id, updated_data)
        if updated:
            logger.log(f"Profile '{updated['name']}' updated.")
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
                
                screen_w = self.winfo_screenwidth()
                screen_h = self.winfo_screenheight()
                
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
        """Stops all checked browser instances and any running mass automation worker."""
        if self.current_batch_worker and self.current_batch_worker.is_alive():
            logger.log("Stopping active Mass Automation task...")
            self.current_batch_worker.stop()

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
        link = self.target_url_entry.get().strip()
        if not link:
            logger.log("Error: Please enter a valid Target URL first!")
            return
            
        active_instances = self.get_checked_active_instances()
        if not active_instances:
            return
            
        delay = self.get_delay_seconds()
        logger.log(f"Starting background NavigationWorker to open URL: {link}...")
        
        NavigationWorker(
            active_instances=active_instances,
            url=link,
            delay_sec=delay
        ).start()

    def save_current_automation_state(self):
        """Saves current automation panel settings and comment pool to settings.json."""
        try:
            settings = load_settings()
            settings["target_url"] = self.target_url_entry.get().strip()
            settings["comments_text"] = self.comment_textbox.get("1.0", "end-1c")
            settings["comment_separator"] = self.comment_separator_entry.get().strip()
            settings["add_emoji"] = (self.comment_emoji_var.get() == "on")
            w_val = self.get_watch_time_seconds()
            settings["watch_time"] = int(w_val) if w_val.is_integer() else w_val
            
            settings["batch_size"] = self.get_batch_size()
            
            r_val = self.get_batch_rest_seconds()
            settings["batch_rest"] = int(r_val) if r_val.is_integer() else r_val
            
            d_val = self.get_delay_seconds()
            settings["global_delay"] = int(d_val) if d_val.is_integer() else d_val
            
            save_settings(settings)
        except Exception as e:
            logger.log(f"Error saving automation settings: {e}")

    def on_import_comments_txt_clicked(self):
        """Opens file dialog to import comment text from a .txt file."""
        file_path = filedialog.askopenfilename(
            title="Select Comments Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.comment_textbox.delete("1.0", "end")
                self.comment_textbox.insert("1.0", content)
                self.save_current_automation_state()
                logger.log(f"Successfully imported comment pool from: {file_path}")
            except Exception as e:
                logger.log(f"Error importing .txt file: {e}")

    def on_paste_clipboard_clicked(self, event=None):
        """Pastes Unicode text from Windows clipboard cleanly into comment textbox."""
        try:
            text = None
            try:
                text = self.clipboard_get()
            except Exception:
                try:
                    text = self.clipboard_get(type="UTF8_STRING")
                except Exception:
                    pass
            if text:
                try:
                    self.comment_textbox.delete("sel.first", "sel.last")
                except Exception:
                    pass
                self.comment_textbox.insert("insert", text)
                self.save_current_automation_state()
                logger.log("Successfully pasted Khmer / Unicode comments from clipboard.")
                return "break"
        except Exception as e:
            logger.log(f"Error pasting from clipboard: {e}")

    # --- UNIFIED MULTI-AUTOMATION HANDLER (WITH BATCHING ENGINE) ---

    def on_start_multi_automation_clicked(self):
        self.save_current_automation_state()
        url = self.target_url_entry.get().strip()
        if not url:
            logger.log("Error: Please enter a Target URL before starting automation task.")
            return
            
        # Collect checked tasks list
        tasks_list = []
        if self.chk_follow_var.get() == "on":
            tasks_list.append("FOLLOW")
        if self.chk_like_var.get() == "on":
            tasks_list.append("LIKE")
        if self.chk_comment_var.get() == "on":
            tasks_list.append("COMMENT")
        if self.chk_share_var.get() == "on":
            tasks_list.append("SHARE")
            
        if not tasks_list:
            logger.log("Warning: Please check at least one automation action (Follow, Like, Comment, or Share).")
            return
            
        delay = self.get_delay_seconds()
        
        # Extract selective reactions pool
        allowed_reactions = [r_key for r_key, var in self.react_cb_vars.items() if var.get() == "on"]
        if not allowed_reactions:
            allowed_reactions = ["LIKE"]
        reaction = allowed_reactions[0]
        random_react = self.random_react_var.get() == "on"
        
        target_type = self.follow_target_type_var.get()
        set_favorites = self.chk_favorites_var.get() == "on"
        
        # Parse comment pool list with custom separator sign
        sep_sign = self.comment_separator_entry.get().strip()
        raw_text = self.comment_textbox.get("1.0", "end").strip()
        if sep_sign and sep_sign != "\\n" and sep_sign in raw_text:
            comments = [c.strip() for c in raw_text.split(sep_sign) if c.strip()]
        else:
            comments = [c.strip() for c in raw_text.splitlines() if c.strip()]
            
        enable_emoji = self.comment_emoji_var.get() == "on"
        destination = self.share_dest_var.get()
        watch_time = self.get_watch_time_seconds()
        
        options = {
            "reaction": reaction,
            "random_reaction": random_react,
            "allowed_reactions": allowed_reactions,
            "target_type": target_type,
            "set_favorites": set_favorites,
            "comment_list": comments,
            "enable_emoji": enable_emoji,
            "destination": destination,
            "watch_time": watch_time,
            "small_window": self.small_window_var.get() == "on",
            "mobile_mode": self.mobile_mode_var.get() == "on",
            "tile": self.tile_on_launch_var.get() == "on",
            "screen_w": self.winfo_screenwidth(),
            "screen_h": self.winfo_screenheight()
        }
        
        # Check if worker is already running
        if self.current_batch_worker and self.current_batch_worker.is_alive():
            logger.log("Warning: A Mass Automation task is already running! Stopping previous task first...")
            self.current_batch_worker.stop()
            time.sleep(1.0)
            
        # Get selected profiles (either checked checkboxes or all loaded profiles)
        checked_ids = [pid for pid, var in self.checked_profiles.items() if var.get() == "on"]
        settings = load_settings()
        all_profiles = settings.get("profiles", [])
        
        if checked_ids:
            selected_profiles = [p for p in all_profiles if p["id"] in checked_ids]
        else:
            selected_profiles = all_profiles
            
        if not selected_profiles:
            logger.log("Warning: No profiles available. Please add Chrome profiles first!")
            return

        batch_size = self.get_batch_size()
        batch_rest = self.get_batch_rest_seconds()
        
        def update_progress(completed, total):
            ratio = completed / total if total > 0 else 0
            self.after(0, lambda: self.progress_bar.set(ratio))
            self.after(0, lambda: self.progress_lbl.configure(text=f"Progress: {completed} / {total} Profiles ({ratio*100:.1f}%)"))

        logger.log(f"Dispatching BatchAutomationWorker for {len(selected_profiles)} profile(s)...")
        self.current_batch_worker = BatchAutomationWorker(
            selected_profiles=selected_profiles,
            tasks_list=tasks_list,
            target_url=url,
            manager=self.manager,
            batch_size=batch_size,
            batch_rest_delay=batch_rest,
            delay_sec=delay,
            options=options,
            progress_callback=update_progress
        )
        self.current_batch_worker.start()

    def get_checked_active_instances(self) -> list:
        checked_ids = [pid for pid, var in self.checked_profiles.items() if var.get() == "on"]
        active_instances = [self.manager.active_instances[pid] for pid in checked_ids if pid in self.manager.active_instances]
        
        if not active_instances:
            running_instances = [inst for pid, inst in self.manager.active_instances.items() if pid in self.running_profiles]
            if running_instances:
                logger.log(f"Auto-targeting {len(running_instances)} active running browser(s)...")
                return running_instances
            else:
                logger.log("Warning: No browser profiles are currently running. Please click 'Run' or 'Launch Checked' first!")
                return []
        return active_instances

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

    def get_batch_size(self) -> int:
        """Retrieves batch size entry, defaults to 5 on error."""
        try:
            val = int(self.batch_size_entry.get().strip())
            return val if val >= 1 else 5
        except Exception:
            return 5

    def get_batch_rest_seconds(self) -> float:
        """Retrieves batch rest seconds entry, defaults to 15.0 on error."""
        try:
            val = float(self.batch_rest_entry.get().strip())
            return val if val >= 0 else 15.0
        except Exception:
            return 15.0

    def get_watch_time_seconds(self) -> float:
        """Retrieves watch time seconds entry, defaults to 10.0 on error."""
        try:
            val = float(self.watch_time_entry.get().strip())
            return val if val >= 0 else 10.0
        except Exception:
            return 10.0

    def on_close_app(self):
        """Cleans up and closes all browsers before exiting."""
        logger.log("Saving automation state and closing all browsers before exit...")
        if self.current_batch_worker and self.current_batch_worker.is_alive():
            self.current_batch_worker.stop()

        self.save_current_automation_state()
        self.manager.close_all()
        
        start_time = time.time()
        while self.manager.active_instances and (time.time() - start_time) < 3.0:
            self.update()
            time.sleep(0.1)
            
        self.destroy()
