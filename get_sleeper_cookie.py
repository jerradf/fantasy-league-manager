#!/usr/bin/env python3
"""
Sleeper Cookie Grabber
Uses browser automation to get session cookie for write operations
"""

import sys
import os
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright not installed!")
    print("   Installing now...")
    os.system("pip3 install playwright")
    os.system("playwright install chromium")
    print("✅ Playwright installed! Run script again.")
    sys.exit(1)


def get_sleeper_cookie():
    """
    Automate browser to get Sleeper session cookie
    
    Returns: cookie string
    """
    print("🌐 Opening Sleeper login page...")
    print("📝 Please log in manually when the browser opens")
    print("")
    
    with sync_playwright() as p:
        # Launch browser in headed mode so user can log in
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        page = context.new_page()
        
        # Go to Sleeper
        print("🔗 Navigating to Sleeper...")
        page.goto("https://sleeper.com/login")
        
        print("")
        print("=" * 60)
        print("👆 PLEASE LOG IN TO SLEEPER IN THE BROWSER WINDOW")
        print("=" * 60)
        print("")
        print("Waiting for you to log in...")
        print("(Script will detect when you're logged in)")
        print("")
        
        # Wait for user to log in (check for navigation to dashboard/leagues)
        max_wait = 300  # 5 minutes
        start_time = time.time()
        logged_in = False
        
        while time.time() - start_time < max_wait:
            current_url = page.url
            
            # Check if logged in (URL changed from login page)
            if "login" not in current_url and "sleeper.com" in current_url:
                logged_in = True
                break
            
            time.sleep(2)
        
        if not logged_in:
            print("❌ Timed out waiting for login")
            browser.close()
            return None
        
        print("✅ Detected successful login!")
        print("")
        
        # Get cookies
        cookies = context.cookies()
        
        # Find Sleeper session cookie
        cookie_string = ""
        for cookie in cookies:
            cookie_string += f"{cookie['name']}={cookie['value']}; "
        
        cookie_string = cookie_string.strip()
        
        print("✅ Got session cookie!")
        print("")
        
        browser.close()
        
        return cookie_string


def save_cookie_to_env(cookie: str):
    """Save cookie to ~/.zshrc"""
    
    zshrc_path = Path.home() / ".zshrc"
    
    # Read existing content
    if zshrc_path.exists():
        with open(zshrc_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Remove old SLEEPER_COOKIE if exists
    lines = content.split('\n')
    new_lines = [line for line in lines if 'SLEEPER_COOKIE=' not in line]
    
    # Add new cookie
    new_lines.append(f'\n# Sleeper API Cookie (auto-generated {time.strftime("%Y-%m-%d %H:%M")})')
    new_lines.append(f'export SLEEPER_COOKIE="{cookie}"')
    
    # Write back
    with open(zshrc_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Saved to {zshrc_path}")
    print("")
    print("🔄 Reload with: source ~/.zshrc")


def main():
    print("=" * 60)
    print("  🏈 SLEEPER COOKIE GRABBER - AUTOMATION MODE 🏈")
    print("=" * 60)
    print("")
    
    cookie = get_sleeper_cookie()
    
    if cookie:
        print("=" * 60)
        print("✅ SUCCESS! Got your Sleeper session cookie")
        print("=" * 60)
        print("")
        
        # Offer to save
        print("Save to ~/.zshrc?")
        choice = input("(y/n): ").strip().lower()
        
        if choice == 'y':
            save_cookie_to_env(cookie)
            print("")
            print("=" * 60)
            print("🎉 ALL SET! Cookie saved to environment")
            print("=" * 60)
            print("")
            print("Next steps:")
            print("1. Reload: source ~/.zshrc")
            print("2. Run: ~/Desktop/RUN_LEAGUE_MANAGER.sh")
            print("")
            print("The system will now be able to:")
            print("✅ Auto-accept/reject trades")
            print("✅ Auto-execute waiver moves")
            print("✅ Auto-drop underperforming players")
            print("")
        else:
            print("")
            print("Cookie (save this manually):")
            print(cookie)
            print("")
    else:
        print("❌ Failed to get cookie")
        sys.exit(1)


if __name__ == "__main__":
    main()
