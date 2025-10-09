#!/usr/bin/env python3
"""
Script to change language configuration easily
"""
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.language_utils import (
    set_language, 
    get_current_language,
    get_available_languages,
    language_config
)


def show_current_status():
    """Show current language status"""
    print("=" * 50)
    print("🌐 CURRENT LANGUAGE CONFIGURATION")
    print("=" * 50)
    print(f"Current language: {get_current_language()}")
    print(f"Available languages: {get_available_languages()}")
    print(f"Language name: {language_config.get_language_name()}")


def change_language_interactive():
    """Interactive language changer"""
    show_current_status()
    
    print("\n" + "=" * 50)
    print("🔄 CHANGE LANGUAGE")
    print("=" * 50)
    
    available_langs = get_available_languages()
    
    print("\nAvailable languages:")
    for i, (code, name) in enumerate(available_langs.items(), 1):
        current_marker = " (CURRENT)" if code == get_current_language() else ""
        print(f"  {i}. {name} ({code}){current_marker}")
    
    try:
        choice = input(f"\nSelect language (1-{len(available_langs)}) or enter language code: ").strip()
        
        # Try to parse as number
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_langs):
                lang_codes = list(available_langs.keys())
                selected_lang = lang_codes[choice_num - 1]
            else:
                print("❌ Invalid choice number")
                return False
        else:
            # Treat as language code
            selected_lang = choice.lower()
        
        # Change language
        if set_language(selected_lang):
            print(f"✅ Successfully changed to {language_config.get_language_name()}")
            show_current_status()
            return True
        else:
            print(f"❌ Failed to change to {selected_lang}")
            return False
            
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Operation cancelled")
        return False


def change_language_direct(language_code):
    """Change language directly"""
    if set_language(language_code):
        print(f"✅ Successfully changed to {language_config.get_language_name()}")
        show_current_status()
        return True
    else:
        print(f"❌ Failed to change to {language_code}")
        return False


def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Direct language change
        language_code = sys.argv[1].lower()
        change_language_direct(language_code)
    else:
        # Interactive mode
        change_language_interactive()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
