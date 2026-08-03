import os
import json
import uuid
import shutil
from app.config import SETTINGS_FILE, PROFILES_DIR

def load_settings() -> dict:
    """Loads settings from settings.json. Creates default structure if it doesn't exist."""
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "profiles": [],
            "global_delay": 5
        }
        save_settings(default_settings)
        return default_settings
    
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "profiles" not in data:
                data["profiles"] = []
            if "global_delay" not in data:
                data["global_delay"] = 5
            return data
    except Exception:
        return {"profiles": [], "global_delay": 5}

def save_settings(settings: dict) -> None:
    """Saves settings dictionary to settings.json."""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def get_profile_dir(profile_id: str) -> str:
    """Returns the absolute path to a profile's User Data Directory."""
    return os.path.join(PROFILES_DIR, profile_id)

def add_profile(profile_data: dict) -> dict:
    """Creates a profile entry with a unique ID and appends it to settings.json."""
    settings = load_settings()
    
    # Generate unique ID and directory
    profile_id = str(uuid.uuid4())[:8]
    new_profile = {
        "id": profile_id,
        "name": profile_data["name"],
        "proxy": profile_data.get("proxy"),
        "proxy_user": profile_data.get("proxy_user"),
        "proxy_pass": profile_data.get("proxy_pass"),
        "user_data_dir": get_profile_dir(profile_id)
    }
    
    settings["profiles"].append(new_profile)
    save_settings(settings)
    
    # Pre-create the directory path
    os.makedirs(new_profile["user_data_dir"], exist_ok=True)
    return new_profile

def delete_profile(profile_id: str) -> None:
    """Removes a profile entry and cleans up its directory."""
    settings = load_settings()
    
    # Find profile and remove it
    profile_to_delete = None
    for p in settings["profiles"]:
        if p["id"] == profile_id:
            profile_to_delete = p
            break
            
    if profile_to_delete:
        settings["profiles"].remove(profile_to_delete)
        save_settings(settings)
        
        # Clean up files
        path = profile_to_delete["user_data_dir"]
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:
                pass  # Ignore file lock errors
