"""
Language configuration utilities for handling image paths based on language settings
"""
import json
import os
from typing import Optional, Dict, Any


class LanguageConfig:
    """Class to handle language configuration and image path management"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.current_language = self.config.get("language", "en")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ Config file {self.config_file} not found, using default settings")
                return self._get_default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "language": "en",
            "languages": {
                "vi": {
                    "name": "Vietnamese",
                    "image_path_prefix": "vi/",
                    "description": "Bản tiếng Việt - sử dụng ảnh trong thư mục vi/"
                },
                "en": {
                    "name": "English",
                    "image_path_prefix": "en/",
                    "description": "Bản tiếng Anh - sử dụng ảnh trong thư mục en/"
                }
            },
            "default_settings": {
                "auto_detect_language": False,
                "fallback_to_vi": True
            }
        }
    
    def set_language(self, language: str) -> bool:
        """Set current language"""
        if language in self.config.get("languages", {}):
            self.current_language = language
            self.config["language"] = language
            self._save_config()
            print(f"✅ Language changed to: {self.get_language_name()}")
            return True
        else:
            print(f"❌ Language '{language}' not supported")
            return False
    
    def get_language_name(self) -> str:
        """Get current language name"""
        return self.config["languages"][self.current_language]["name"]
    
    def get_image_path(self, base_path: str) -> str:
        """
        Get the correct image path based on current language setting
        
        Args:
            base_path: Base image path (e.g., "buttons/attack", "open_resource/more")
            
        Returns:
            Full image path with language prefix if needed
        """
        try:
            # Get language prefix
            language_config = self.config["languages"][self.current_language]
            prefix = language_config.get("image_path_prefix", "")
            
            # Construct full path
            if prefix:
                full_path = f"images/{prefix}{base_path}"
            else:
                full_path = f"images/{base_path}"
            
            # Check if file exists, if not try fallback
            if not self._check_image_exists(full_path):
                if self.config.get("default_settings", {}).get("fallback_to_vi", True):
                    # Try Vietnamese version as fallback
                    vi_path = f"images/vi/{base_path}"
                    if self._check_image_exists(vi_path):
                        print(f"⚠️ Image not found in {self.current_language} ({full_path}), using Vietnamese fallback: {vi_path}")
                        return vi_path
                    else:
                        print(f"❌ Image not found in both {self.current_language} ({full_path}) and Vietnamese ({vi_path})")
                        return full_path  # Return original path anyway
                else:
                    print(f"❌ Image not found: {full_path}")
                    return full_path
            else:
                return full_path
                
        except Exception as e:
            print(f"❌ Error getting image path: {e}")
            return f"images/{base_path}"  # Fallback to original path
    
    def _check_image_exists(self, path: str) -> bool:
        """Check if image file exists with common extensions"""
        extensions = ['.JPG', '.jpg', '.PNG', '.png', '.JPEG', '.jpeg']
        for ext in extensions:
            if os.path.exists(f"{path}{ext}"):
                return True
        return False
    
    def _save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages"""
        return {lang: info["name"] for lang, info in self.config["languages"].items()}
    
    def is_english_mode(self) -> bool:
        """Check if currently in English mode"""
        return self.current_language == "en"
    
    def is_vietnamese_mode(self) -> bool:
        """Check if currently in Vietnamese mode"""
        return self.current_language == "vi"


# Global instance
language_config = LanguageConfig()


def get_image_path(base_path: str) -> str:
    """
    Convenience function to get image path with current language settings
    
    Args:
        base_path: Base image path (e.g., "buttons/attack", "open_resource/more")
        
    Returns:
        Full image path with language prefix if needed
    """
    return language_config.get_image_path(base_path)


def set_language(language: str) -> bool:
    """
    Convenience function to set language
    
    Args:
        language: Language code ("vi" or "en")
        
    Returns:
        True if successful, False otherwise
    """
    return language_config.set_language(language)


def get_current_language() -> str:
    """Get current language code"""
    return language_config.current_language


def is_english_mode() -> bool:
    """Check if currently in English mode"""
    return language_config.is_english_mode()


def is_vietnamese_mode() -> bool:
    """Check if currently in Vietnamese mode"""
    return language_config.is_vietnamese_mode()


def get_available_languages() -> Dict[str, str]:
    """Get list of available languages"""
    return language_config.get_available_languages()


# Example usage and testing
if __name__ == "__main__":
    print("=== Language Configuration Test ===")
    
    # Test current settings
    print(f"Current language: {get_current_language()}")
    print(f"Available languages: {language_config.get_available_languages()}")
    
    # Test image path generation
    test_paths = [
        "buttons/attack",
        "open_resource/more", 
        "buttons/cancel",
        "open_resource/items/1"
    ]
    
    print("\n=== Image Path Tests ===")
    for path in test_paths:
        full_path = get_image_path(path)
        print(f"Base: {path} -> Full: {full_path}")
    
    # Test language switching
    print("\n=== Language Switching Test ===")
    print("Switching to English...")
    set_language("en")
    for path in test_paths:
        full_path = get_image_path(path)
        print(f"Base: {path} -> Full: {full_path}")
    
    print("\nSwitching back to Vietnamese...")
    set_language("vi")
    for path in test_paths:
        full_path = get_image_path(path)
        print(f"Base: {path} -> Full: {full_path}")
