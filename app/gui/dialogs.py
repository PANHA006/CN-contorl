import customtkinter as ctk
from app.gui.styles import *

class AddProfileDialog(ctk.CTkToplevel):
    """Popup window to add a new Chrome profile with custom name and optional proxy."""
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("➕ Add Chrome Profile")
        self.geometry("400x380")
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
        
        x = parent_x + (parent_width // 2) - (400 // 2)
        y = parent_y + (parent_height // 2) - (380 // 2)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Header Title
        title_lbl = ctk.CTkLabel(
            self, 
            text="Add New Profile", 
            font=FONT_SUBTITLE, 
            text_color=COLOR_PRIMARY
        )
        title_lbl.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")

        # Profile Name Input
        name_lbl = ctk.CTkLabel(self, text="Profile Name:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        name_lbl.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. ch1 - Personal", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.name_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        # Proxy IP Input
        proxy_lbl = ctk.CTkLabel(self, text="Proxy Host/IP:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        proxy_lbl.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.proxy_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. 192.168.1.1:8080 (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.proxy_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        # Proxy User Input
        user_lbl = ctk.CTkLabel(self, text="Proxy User:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        user_lbl.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.user_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Username (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.user_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        # Proxy Pass Input
        pass_lbl = ctk.CTkLabel(self, text="Proxy Pass:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        pass_lbl.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.pass_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Password (optional)", 
            show="*", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.pass_entry.grid(row=4, column=1, padx=20, pady=10, sticky="ew")

        # Error label (hidden by default)
        self.error_lbl = ctk.CTkLabel(self, text="", text_color=COLOR_DANGER, font=FONT_TEXT)
        self.error_lbl.grid(row=5, column=0, columnspan=2, padx=20, pady=5)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=15, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_TEXT_MUTED, 
            hover_color="#3E445E",
            text_color=COLOR_TEXT_MAIN,
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        save_btn = ctk.CTkButton(
            btn_frame, 
            text="Save Profile", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_PRIMARY, 
            hover_color="#5B85DB",
            text_color=COLOR_BG,
            command=self.on_submit
        )
        save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def on_submit(self):
        name = self.name_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()

        if not name:
            self.error_lbl.configure(text="Profile Name is required!")
            return

        profile_data = {
            "name": name,
            "proxy": proxy if proxy else None,
            "proxy_user": user if user else None,
            "proxy_pass": pwd if pwd else None
        }

        self.on_save(profile_data)
        self.destroy()
