"""
Chrome/ChromeDriver Compatibility Checker & Auto-Fixer
====================================================

Advanced tool to check Chrome/ChromeDriver compatibility and auto-fix issues.
"""

def get_chrome_version():
    """Get the installed Chrome browser version."""
    import subprocess
    import os
    import re
    
    chrome_version = None
    
    try:
        # Windows Chrome version check
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    chrome_version = result.stdout.strip()
                    # Extract version number
                    version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', chrome_version)
                    if version_match:
                        return version_match.group(1)
                    break
    except Exception:
        pass
    
    return chrome_version

def fix_chromedriver_version():
    """Attempt to fix ChromeDriver version mismatch."""
    print("🔧 Attempting to fix ChromeDriver version mismatch...")
    
    try:
        import subprocess
        import sys
        
        # Update undetected-chromedriver
        print("📦 Updating undetected-chromedriver...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "undetected-chromedriver"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ undetected-chromedriver updated successfully")
        else:
            print(f"⚠️ Update warning: {result.stderr}")
        
        # Clear ChromeDriver cache
        import os
        import tempfile
        print("🗑️ Clearing ChromeDriver cache...")
        
        temp_dir = tempfile.gettempdir()
        cleared_count = 0
        for file in os.listdir(temp_dir):
            if "chromedriver" in file.lower() or "undetected" in file.lower():
                try:
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleared_count += 1
                except:
                    pass
        
        if cleared_count > 0:
            print(f"✅ Cleared {cleared_count} cached ChromeDriver files")
        
        return True
        
    except Exception as e:
        print(f"❌ Fix attempt failed: {e}")
        return False

def test_chromedriver():
    """Test if ChromeDriver works after fixes."""
    try:
        print("🧪 Testing ChromeDriver initialization...")
        
        import undetected_chromedriver as uc
        
        # Create fresh options to avoid reuse issues
        def create_test_options():
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            return options
        
        options = create_test_options()
        
        try:
            driver = uc.Chrome(options=options, version_main=None)
        except Exception as e:
            if "reuse" in str(e).lower() or "chromeoptions" in str(e):
                print("  ⚠️ ChromeOptions reuse detected, creating fresh options...")
                options = create_test_options()
                driver = uc.Chrome(options=options, version_main=None)
            else:
                raise e
        
        driver.get("https://www.google.com")
        driver.quit()
        
        print("✅ ChromeDriver test successful!")
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver test failed: {e}")
        return False

def check_chrome_compatibility():
    """Check Chrome and ChromeDriver compatibility with auto-fix."""
    print("🔍 Chrome/ChromeDriver Compatibility Checker & Auto-Fixer")
    print("=" * 60)
    
    try:
        # Get Chrome version
        chrome_version = get_chrome_version()
        if chrome_version:
            print(f"✅ Chrome found: {chrome_version}")
        else:
            print("❌ Chrome not found in standard locations")
            print("   Please install Google Chrome from: https://www.google.com/chrome/")
            return
        
        # Check undetected-chromedriver
        try:
            import undetected_chromedriver as uc
            print("📦 undetected-chromedriver package: Available")
            
            # Test ChromeDriver initialization
            if test_chromedriver():
                print("🎉 ChromeDriver is working perfectly!")
                return
            else:
                print("⚠️ ChromeDriver has issues, attempting to fix...")
                
                # Attempt auto-fix
                if fix_chromedriver_version():
                    print("🔄 Retesting ChromeDriver after fixes...")
                    if test_chromedriver():
                        print("🎉 ChromeDriver fixed successfully!")
                        return
                    else:
                        print("❌ Auto-fix unsuccessful")
                        
        except ImportError:
            print("❌ undetected-chromedriver not installed")
            print("   Install with: pip install undetected-chromedriver")
            return
            
    except Exception as e:
        print(f"❌ Compatibility check failed: {e}")
    
    # If we reach here, there are still issues
    print("\n" + "=" * 60)
    print("💡 SOLUTIONS:")
    print("1. 🏆 RECOMMENDED: Use Manual Input mode")
    print("   ✅ No browser issues, same great results, faster setup")
    print()
    print("2. 🔧 Fix ChromeDriver manually:")
    print("   • Update Chrome: chrome://settings/help")
    print("   • Update ChromeDriver: pip install --upgrade undetected-chromedriver")
    print("   • Clear cache: Delete temp ChromeDriver files")
    print()
    print("3. 📄 Use PDF Upload mode instead of URL scraping")
    print("   ✅ More reliable, works offline, no version conflicts")

if __name__ == "__main__":
    check_chrome_compatibility()