import customtkinter as ctk
from app.gui.styles import *

class AddProfileDialog(ctk.CTkToplevel):
    """Popup window to add a new Chrome profile with custom name, proxy, and GPS geolocation."""
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("➕ Add Chrome Profile")
        self.geometry("420x470")
        self.resizable(False, False)
        
        self.on_save = on_save_callback
        
        # Color styling
        self.configure(fg_color=COLOR_PANEL_BG)
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Layout configurations
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        
        self.setup_ui()
        
        # Center the window relative to parent
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (420 // 2)
        y = parent_y + (parent_height // 2) - (470 // 2)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Header Title
        title_lbl = ctk.CTkLabel(
            self, 
            text="Add New Profile", 
            font=FONT_SUBTITLE, 
            text_color=COLOR_PRIMARY
        )
        title_lbl.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")

        # Profile Name Input
        name_lbl = ctk.CTkLabel(self, text="Profile Name:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        name_lbl.grid(row=1, column=0, padx=20, pady=6, sticky="w")
        self.name_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. ch1 - Personal", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.name_entry.grid(row=1, column=1, padx=20, pady=6, sticky="ew")

        # Proxy IP Input
        proxy_lbl = ctk.CTkLabel(self, text="Proxy Host/IP:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        proxy_lbl.grid(row=2, column=0, padx=20, pady=6, sticky="w")
        self.proxy_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. 192.168.1.1:8080 (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.proxy_entry.grid(row=2, column=1, padx=20, pady=6, sticky="ew")

        # Proxy User Input
        user_lbl = ctk.CTkLabel(self, text="Proxy User:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        user_lbl.grid(row=3, column=0, padx=20, pady=6, sticky="w")
        self.user_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Username (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.user_entry.grid(row=3, column=1, padx=20, pady=6, sticky="ew")

        # Proxy Pass Input
        pass_lbl = ctk.CTkLabel(self, text="Proxy Pass:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        pass_lbl.grid(row=4, column=0, padx=20, pady=6, sticky="w")
        self.pass_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Password (optional)", 
            show="*", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.pass_entry.grid(row=4, column=1, padx=20, pady=6, sticky="ew")

        # Latitude Input
        lat_lbl = ctk.CTkLabel(self, text="GPS Latitude:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        lat_lbl.grid(row=5, column=0, padx=20, pady=6, sticky="w")
        self.lat_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. 40.7128 (New York)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.lat_entry.grid(row=5, column=1, padx=20, pady=6, sticky="ew")

        # Longitude Input
        lng_lbl = ctk.CTkLabel(self, text="GPS Longitude:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        lng_lbl.grid(row=6, column=0, padx=20, pady=6, sticky="w")
        self.lng_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. -74.0060 (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.lng_entry.grid(row=6, column=1, padx=20, pady=6, sticky="ew")

        # Error label (hidden by default)
        self.error_lbl = ctk.CTkLabel(self, text="", text_color=COLOR_DANGER, font=FONT_TEXT)
        self.error_lbl.grid(row=7, column=0, columnspan=2, padx=20, pady=2)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=8, column=0, columnspan=2, padx=20, pady=(10, 15), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        cancel_btn = ctk.CTkButton(
            self, 
            text="Cancel", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_TEXT_MUTED, 
            hover_color="#3E445E",
            text_color=COLOR_TEXT_MAIN,
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=0, in_=btn_frame, padx=5, pady=5, sticky="ew")

        save_btn = ctk.CTkButton(
            self, 
            text="Save Profile", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_PRIMARY, 
            hover_color="#5B85DB",
            text_color=COLOR_BG,
            command=self.on_save_clicked
        )
        save_btn.grid(row=0, column=1, in_=btn_frame, padx=5, pady=5, sticky="ew")

    def on_save_clicked(self):
        name = self.name_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        lat_str = self.lat_entry.get().strip()
        lng_str = self.lng_entry.get().strip()

        if not name:
            self.error_lbl.configure(text="Profile Name is required!")
            return

        profile_data = {
            "name": name,
            "proxy": proxy if proxy else None,
            "proxy_user": user if user else None,
            "proxy_pass": password if password else None,
            "latitude": float(lat_str) if lat_str else None,
            "longitude": float(lng_str) if lng_str else None
        }

        self.on_save(profile_data)
        self.destroy()


class EditProfileDialog(ctk.CTkToplevel):
    """Popup window to edit an existing Chrome profile's name, proxy configuration, and GPS geolocation."""
    def __init__(self, parent, profile_data: dict, on_save_callback):
        super().__init__(parent)
        self.title("✏️ Edit Chrome Profile")
        self.geometry("420x470")
        self.resizable(False, False)
        
        self.profile_data = profile_data
        self.on_save = on_save_callback
        
        # Color styling
        self.configure(fg_color=COLOR_PANEL_BG)
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Layout configurations
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        
        self.setup_ui()
        self.populate_existing_data()
        
        # Center the window relative to parent
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (420 // 2)
        y = parent_y + (parent_height // 2) - (470 // 2)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Header Title
        title_lbl = ctk.CTkLabel(
            self, 
            text="Edit Profile Details", 
            font=FONT_SUBTITLE, 
            text_color=COLOR_PRIMARY
        )
        title_lbl.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")

        # Profile Name Input
        name_lbl = ctk.CTkLabel(self, text="Profile Name:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        name_lbl.grid(row=1, column=0, padx=20, pady=6, sticky="w")
        self.name_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. ch1 - Personal", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.name_entry.grid(row=1, column=1, padx=20, pady=6, sticky="ew")

        # Proxy IP Input
        proxy_lbl = ctk.CTkLabel(self, text="Proxy Host/IP:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        proxy_lbl.grid(row=2, column=0, padx=20, pady=6, sticky="w")
        self.proxy_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. 192.168.1.1:8080 (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.proxy_entry.grid(row=2, column=1, padx=20, pady=6, sticky="ew")

        # Proxy User Input
        user_lbl = ctk.CTkLabel(self, text="Proxy User:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        user_lbl.grid(row=3, column=0, padx=20, pady=6, sticky="w")
        self.user_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Username (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.user_entry.grid(row=3, column=1, padx=20, pady=6, sticky="ew")

        # Proxy Pass Input
        pass_lbl = ctk.CTkLabel(self, text="Proxy Pass:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        pass_lbl.grid(row=4, column=0, padx=20, pady=6, sticky="w")
        self.pass_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Password (optional)", 
            show="*", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.pass_entry.grid(row=4, column=1, padx=20, pady=6, sticky="ew")

        # Latitude Input
        lat_lbl = ctk.CTkLabel(self, text="GPS Latitude:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        lat_lbl.grid(row=5, column=0, padx=20, pady=6, sticky="w")
        self.lat_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. 40.7128 (New York)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.lat_entry.grid(row=5, column=1, padx=20, pady=6, sticky="ew")

        # Longitude Input
        lng_lbl = ctk.CTkLabel(self, text="GPS Longitude:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        lng_lbl.grid(row=6, column=0, padx=20, pady=6, sticky="w")
        self.lng_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. -74.0060 (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.lng_entry.grid(row=6, column=1, padx=20, pady=6, sticky="ew")

        # Error label (hidden by default)
        self.error_lbl = ctk.CTkLabel(self, text="", text_color=COLOR_DANGER, font=FONT_TEXT)
        self.error_lbl.grid(row=7, column=0, columnspan=2, padx=20, pady=2)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=8, column=0, columnspan=2, padx=20, pady=(10, 15), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        cancel_btn = ctk.CTkButton(
            self, 
            text="Cancel", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_TEXT_MUTED, 
            hover_color="#3E445E",
            text_color=COLOR_TEXT_MAIN,
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=0, in_=btn_frame, padx=5, pady=5, sticky="ew")

        save_btn = ctk.CTkButton(
            self, 
            text="Save Changes", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_PRIMARY, 
            hover_color="#5B85DB",
            text_color=COLOR_BG,
            command=self.on_save_clicked
        )
        save_btn.grid(row=0, column=1, in_=btn_frame, padx=5, pady=5, sticky="ew")

    def populate_existing_data(self):
        """Populates the dialog entries with current profile details."""
        if not self.profile_data:
            return
            
        self.name_entry.insert(0, self.profile_data.get("name", ""))
        
        if self.profile_data.get("proxy"):
            self.proxy_entry.insert(0, self.profile_data.get("proxy", ""))
        if self.profile_data.get("proxy_user"):
            self.user_entry.insert(0, self.profile_data.get("proxy_user", ""))
        if self.profile_data.get("proxy_pass"):
            self.pass_entry.insert(0, self.profile_data.get("proxy_pass", ""))
        if self.profile_data.get("latitude") is not None:
            self.lat_entry.insert(0, str(self.profile_data.get("latitude")))
        if self.profile_data.get("longitude") is not None:
            self.lng_entry.insert(0, str(self.profile_data.get("longitude")))

    def on_save_clicked(self):
        name = self.name_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        lat_str = self.lat_entry.get().strip()
        lng_str = self.lng_entry.get().strip()

        if not name:
            self.error_lbl.configure(text="Profile Name is required!")
            return

        updated_data = {
            "name": name,
            "proxy": proxy if proxy else None,
            "proxy_user": user if user else None,
            "proxy_pass": password if password else None,
            "latitude": float(lat_str) if lat_str else None,
            "longitude": float(lng_str) if lng_str else None
        }

        self.on_save(updated_data)
        self.destroy()
