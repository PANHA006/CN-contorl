import random
import customtkinter as ctk
from app.gui.styles import *

CAMBODIA_CITIES_GPS = [
    {"name": "Phnom Penh", "lat": 11.5564, "lng": 104.9282},
    {"name": "Siem Reap", "lat": 13.3671, "lng": 103.8448},
    {"name": "Battambang", "lat": 13.0957, "lng": 103.2022},
    {"name": "Sihanoukville", "lat": 10.6253, "lng": 103.5234},
    {"name": "Kampong Cham", "lat": 11.9924, "lng": 105.4645},
    {"name": "Kandal", "lat": 11.4552, "lng": 104.9546},
    {"name": "Kampot", "lat": 10.6104, "lng": 104.1815},
    {"name": "Kep", "lat": 10.4829, "lng": 104.3167},
    {"name": "Koh Kong", "lat": 11.6153, "lng": 102.9838},
    {"name": "Kratie", "lat": 12.4881, "lng": 106.0188},
    {"name": "Mondulkiri", "lat": 12.4558, "lng": 107.1881},
    {"name": "Ratanakiri", "lat": 13.7394, "lng": 106.9873},
    {"name": "Stung Treng", "lat": 13.5259, "lng": 105.9683},
    {"name": "Preah Vihear", "lat": 13.8073, "lng": 104.9804},
    {"name": "Oddar Meanchey", "lat": 14.1818, "lng": 103.5176},
    {"name": "Banteay Meanchey", "lat": 13.5859, "lng": 102.9737},
    {"name": "Pailin", "lat": 12.8489, "lng": 102.6093},
    {"name": "Pursat", "lat": 12.5388, "lng": 103.9192},
    {"name": "Kampong Chhnang", "lat": 12.2500, "lng": 104.6667},
    {"name": "Kampong Speu", "lat": 11.4533, "lng": 104.5209},
    {"name": "Takeo", "lat": 10.9908, "lng": 104.7850},
    {"name": "Prey Veng", "lat": 11.4868, "lng": 105.3253},
    {"name": "Svay Rieng", "lat": 11.0879, "lng": 105.7994},
    {"name": "Tboung Khmum", "lat": 11.8891, "lng": 105.8760},
    {"name": "Kampong Thom", "lat": 12.7111, "lng": 104.8887}
]

def get_random_cambodia_gps(city_name=None):
    if city_name and "Random" not in city_name:
        city = next((c for c in CAMBODIA_CITIES_GPS if c["name"].lower() in city_name.lower()), None)
        if not city:
            city = random.choice(CAMBODIA_CITIES_GPS)
    else:
        city = random.choice(CAMBODIA_CITIES_GPS)
        
    lat_offset = random.uniform(-0.02, 0.02)
    lng_offset = random.uniform(-0.02, 0.02)
    
    lat = round(city["lat"] + lat_offset, 4)
    lng = round(city["lng"] + lng_offset, 4)
    return lat, lng, city["name"]


class AddProfileDialog(ctk.CTkToplevel):
    """Popup window to add a new Chrome profile with custom name, proxy, and GPS geolocation."""
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("➕ Add Chrome Profile")
        self.geometry("430x550")
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
        
        x = parent_x + (parent_width // 2) - (430 // 2)
        y = parent_y + (parent_height // 2) - (550 // 2)
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
            placeholder_text="e.g. 11.5564 (Phnom Penh)", 
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
            placeholder_text="e.g. 104.9282 (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.lng_entry.grid(row=6, column=1, padx=20, pady=6, sticky="ew")

        # Cambodia City Selector Dropdown
        city_lbl = ctk.CTkLabel(self, text="Cambodia City:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        city_lbl.grid(row=7, column=0, padx=20, pady=6, sticky="w")
        
        city_options = ["🎲 Random City"] + [c["name"] for c in CAMBODIA_CITIES_GPS]
        self.city_option_menu = ctk.CTkOptionMenu(
            self,
            values=city_options,
            font=FONT_TEXT_BOLD,
            dropdown_font=FONT_TEXT,
            fg_color=COLOR_CARD_BG,
            button_color=COLOR_PRIMARY,
            button_hover_color="#5B85DB",
            text_color=COLOR_TEXT_MAIN,
            command=self.on_city_selected
        )
        self.city_option_menu.set("🎲 Random City")
        self.city_option_menu.grid(row=7, column=1, padx=20, pady=6, sticky="ew")

        # Generate Cambodia GPS Button
        gen_gps_btn = ctk.CTkButton(
            self,
            text="🎲 Auto Generate GPS",
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_SECONDARY,
            hover_color="#A37DF2",
            text_color=COLOR_BG,
            height=30,
            command=self.on_generate_gps_clicked
        )
        gen_gps_btn.grid(row=8, column=0, columnspan=2, padx=20, pady=(4, 4), sticky="ew")

        # Error / Status label
        self.error_lbl = ctk.CTkLabel(self, text="", text_color=COLOR_DANGER, font=FONT_TEXT)
        self.error_lbl.grid(row=9, column=0, columnspan=2, padx=20, pady=2)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=10, column=0, columnspan=2, padx=20, pady=(8, 15), sticky="ew")
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

    def on_city_selected(self, selected_city):
        """Fires when user chooses a specific city from dropdown."""
        self.on_generate_gps_clicked()

    def on_generate_gps_clicked(self):
        """Generates random Cambodia GPS coordinates and populates entries."""
        selected_city = self.city_option_menu.get()
        lat, lng, city = get_random_cambodia_gps(selected_city)
        self.lat_entry.delete(0, "end")
        self.lat_entry.insert(0, str(lat))
        self.lng_entry.delete(0, "end")
        self.lng_entry.insert(0, str(lng))
        self.error_lbl.configure(text=f"Generated GPS ({city}): {lat}, {lng}", text_color=COLOR_SUCCESS)

    def on_save_clicked(self):
        name = self.name_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        lat_str = self.lat_entry.get().strip()
        lng_str = self.lng_entry.get().strip()

        if not name:
            self.error_lbl.configure(text="Profile Name is required!", text_color=COLOR_DANGER)
            return

        lat_val = None
        if lat_str:
            try:
                lat_val = float(lat_str)
            except ValueError:
                self.error_lbl.configure(text="GPS Latitude must be a valid number!", text_color=COLOR_DANGER)
                return

        lng_val = None
        if lng_str:
            try:
                lng_val = float(lng_str)
            except ValueError:
                self.error_lbl.configure(text="GPS Longitude must be a valid number!", text_color=COLOR_DANGER)
                return

        profile_data = {
            "name": name,
            "proxy": proxy if proxy else None,
            "proxy_user": user if user else None,
            "proxy_pass": password if password else None,
            "latitude": lat_val,
            "longitude": lng_val
        }

        self.on_save(profile_data)
        self.destroy()


class EditProfileDialog(ctk.CTkToplevel):
    """Popup window to edit an existing Chrome profile's name, proxy configuration, and GPS geolocation."""
    def __init__(self, parent, profile_data: dict, on_save_callback):
        super().__init__(parent)
        self.title("✏️ Edit Chrome Profile")
        self.geometry("430x550")
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
        
        x = parent_x + (parent_width // 2) - (430 // 2)
        y = parent_y + (parent_height // 2) - (550 // 2)
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
            placeholder_text="e.g. 11.5564 (Phnom Penh)", 
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
            placeholder_text="e.g. 104.9282 (optional)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.lng_entry.grid(row=6, column=1, padx=20, pady=6, sticky="ew")

        # Cambodia City Selector Dropdown
        city_lbl = ctk.CTkLabel(self, text="Cambodia City:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        city_lbl.grid(row=7, column=0, padx=20, pady=6, sticky="w")
        
        city_options = ["🎲 Random City"] + [c["name"] for c in CAMBODIA_CITIES_GPS]
        self.city_option_menu = ctk.CTkOptionMenu(
            self,
            values=city_options,
            font=FONT_TEXT_BOLD,
            dropdown_font=FONT_TEXT,
            fg_color=COLOR_CARD_BG,
            button_color=COLOR_PRIMARY,
            button_hover_color="#5B85DB",
            text_color=COLOR_TEXT_MAIN,
            command=self.on_city_selected
        )
        self.city_option_menu.set("🎲 Random City")
        self.city_option_menu.grid(row=7, column=1, padx=20, pady=6, sticky="ew")

        # Generate Cambodia GPS Button
        gen_gps_btn = ctk.CTkButton(
            self,
            text="🎲 Auto Generate GPS",
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_SECONDARY,
            hover_color="#A37DF2",
            text_color=COLOR_BG,
            height=30,
            command=self.on_generate_gps_clicked
        )
        gen_gps_btn.grid(row=8, column=0, columnspan=2, padx=20, pady=(4, 4), sticky="ew")

        # Error / Status label
        self.error_lbl = ctk.CTkLabel(self, text="", text_color=COLOR_DANGER, font=FONT_TEXT)
        self.error_lbl.grid(row=9, column=0, columnspan=2, padx=20, pady=2)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=10, column=0, columnspan=2, padx=20, pady=(8, 15), sticky="ew")
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

    def on_city_selected(self, selected_city):
        """Fires when user chooses a specific city from dropdown."""
        self.on_generate_gps_clicked()

    def on_generate_gps_clicked(self):
        """Generates random Cambodia GPS coordinates and populates entries."""
        selected_city = self.city_option_menu.get()
        lat, lng, city = get_random_cambodia_gps(selected_city)
        self.lat_entry.delete(0, "end")
        self.lat_entry.insert(0, str(lat))
        self.lng_entry.delete(0, "end")
        self.lng_entry.insert(0, str(lng))
        self.error_lbl.configure(text=f"Generated GPS ({city}): {lat}, {lng}", text_color=COLOR_SUCCESS)

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
            self.error_lbl.configure(text="Profile Name is required!", text_color=COLOR_DANGER)
            return

        lat_val = None
        if lat_str:
            try:
                lat_val = float(lat_str)
            except ValueError:
                self.error_lbl.configure(text="GPS Latitude must be a valid number!", text_color=COLOR_DANGER)
                return

        lng_val = None
        if lng_str:
            try:
                lng_val = float(lng_str)
            except ValueError:
                self.error_lbl.configure(text="GPS Longitude must be a valid number!", text_color=COLOR_DANGER)
                return

        updated_data = {
            "name": name,
            "proxy": proxy if proxy else None,
            "proxy_user": user if user else None,
            "proxy_pass": password if password else None,
            "latitude": lat_val,
            "longitude": lng_val
        }

        self.on_save(updated_data)
        self.destroy()


class BulkAddProfilesDialog(ctk.CTkToplevel):
    """Popup modal dialog to bulk create multiple Chrome profiles with auto Cambodia GPS coordinates."""
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("📦 Bulk Add Chrome Profiles (Cambodia GPS)")
        self.geometry("460x560")
        self.resizable(False, False)
        
        self.on_save = on_save_callback
        
        # Color styling
        self.configure(fg_color=COLOR_PANEL_BG)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        
        self.setup_ui()
        
        # Center dialog
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (460 // 2)
        y = parent_y + (parent_height // 2) - (560 // 2)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Title
        title_lbl = ctk.CTkLabel(
            self, 
            text="📦 Bulk Create Profiles (Auto Cambodia GPS)", 
            font=FONT_SUBTITLE, 
            text_color=COLOR_PRIMARY
        )
        title_lbl.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")

        # Number of Profiles
        count_lbl = ctk.CTkLabel(self, text="Profile Quantity:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        count_lbl.grid(row=1, column=0, padx=20, pady=6, sticky="w")
        self.count_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. 10 (or 50, 100)", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.count_entry.insert(0, "10")
        self.count_entry.grid(row=1, column=1, padx=20, pady=6, sticky="ew")

        # Profile Prefix
        prefix_lbl = ctk.CTkLabel(self, text="Name Prefix:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        prefix_lbl.grid(row=2, column=0, padx=20, pady=6, sticky="w")
        self.prefix_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. Account, FB_Profile", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.prefix_entry.insert(0, "Account")
        self.prefix_entry.grid(row=2, column=1, padx=20, pady=6, sticky="ew")

        # Start Index
        start_lbl = ctk.CTkLabel(self, text="Start Number:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        start_lbl.grid(row=3, column=0, padx=20, pady=6, sticky="w")
        self.start_entry = ctk.CTkEntry(
            self, 
            placeholder_text="e.g. 1", 
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.start_entry.insert(0, "1")
        self.start_entry.grid(row=3, column=1, padx=20, pady=6, sticky="ew")

        # Cambodia Region Dropdown
        region_lbl = ctk.CTkLabel(self, text="Cambodia Region:", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        region_lbl.grid(row=4, column=0, padx=20, pady=6, sticky="w")
        
        city_options = ["🎲 Random City (All Cambodia)"] + [c["name"] for c in CAMBODIA_CITIES_GPS]
        self.city_option_menu = ctk.CTkOptionMenu(
            self,
            values=city_options,
            font=FONT_TEXT_BOLD,
            dropdown_font=FONT_TEXT,
            fg_color=COLOR_CARD_BG,
            button_color=COLOR_PRIMARY,
            button_hover_color="#5B85DB",
            text_color=COLOR_TEXT_MAIN
        )
        self.city_option_menu.set("🎲 Random City (All Cambodia)")
        self.city_option_menu.grid(row=4, column=1, padx=20, pady=6, sticky="ew")

        # Optional Proxies Input
        proxy_lbl = ctk.CTkLabel(self, text="Proxies (Optional):", font=FONT_TEXT, text_color=COLOR_TEXT_MAIN)
        proxy_lbl.grid(row=5, column=0, padx=20, pady=6, sticky="nw")
        
        self.proxies_textbox = ctk.CTkTextbox(
            self,
            height=100,
            font=FONT_TEXT,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_TEXT_MUTED
        )
        self.proxies_textbox.grid(row=5, column=1, padx=20, pady=6, sticky="ew")
        
        # Status Label
        self.error_lbl = ctk.CTkLabel(self, text="Paste 1 proxy per line (host:port or host:port:user:pass)", text_color=COLOR_TEXT_MUTED, font=FONT_TEXT)
        self.error_lbl.grid(row=6, column=0, columnspan=2, padx=20, pady=4)

        # Buttons Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=(10, 15), sticky="ew")
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

        create_btn = ctk.CTkButton(
            self, 
            text="🚀 Create All Profiles", 
            font=FONT_TEXT_BOLD,
            fg_color=COLOR_PRIMARY, 
            hover_color="#5B85DB",
            text_color=COLOR_BG,
            command=self.on_create_clicked
        )
        create_btn.grid(row=0, column=1, in_=btn_frame, padx=5, pady=5, sticky="ew")

    def on_create_clicked(self):
        count_str = self.count_entry.get().strip()
        prefix = self.prefix_entry.get().strip() or "Profile"
        start_str = self.start_entry.get().strip() or "1"
        selected_city = self.city_option_menu.get()

        try:
            count = int(count_str)
            if count <= 0 or count > 500:
                raise ValueError()
        except ValueError:
            self.error_lbl.configure(text="Quantity must be a number between 1 and 500!", text_color=COLOR_DANGER)
            return

        try:
            start_num = int(start_str)
        except ValueError:
            start_num = 1

        raw_proxies = [p.strip() for p in self.proxies_textbox.get("1.0", "end").splitlines() if p.strip()]
        
        new_profiles = []
        for i in range(count):
            p_name = f"{prefix} {start_num + i}"
            lat, lng, cname = get_random_cambodia_gps(selected_city)
            
            # Parse proxy if available
            p_host, p_user, p_pass = None, None, None
            if i < len(raw_proxies):
                parts = raw_proxies[i].split(":")
                if len(parts) >= 2:
                    p_host = f"{parts[0]}:{parts[1]}"
                if len(parts) >= 4:
                    p_user = parts[2]
                    p_pass = parts[3]
            
            new_profiles.append({
                "name": p_name,
                "proxy": p_host,
                "proxy_user": p_user,
                "proxy_pass": p_pass,
                "latitude": lat,
                "longitude": lng
            })

        self.on_save(new_profiles)
        self.destroy()
