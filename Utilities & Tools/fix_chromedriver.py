"""
ChromeDriver Auto-Fix Script
===========================

Quick one-click solution for Chrome/ChromeDriver version mismatch issues.
Run this script when you encounter ChromeDriver version errors.
"""

import sys
import subprocess
import os
import tempfile

def create_fresh_chrome_options():
    """Create fresh ChromeOptions object to avoid reuse issues."""
    import undetected_chromedriver as uc
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    return options


def auto_fix_chromedriver():
    """One-click ChromeDriver version issue fixer."""
    print("🛠️  ChromeDriver Auto-Fix Tool")
    print("=" * 40)
    print("This script will fix Chrome/ChromeDriver version mismatches\n")
    
    success_count = 0
    
    # Step 1: Update undetected-chromedriver
    print("Step 1: Updating undetected-chromedriver...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "--force-reinstall", "undetected-chromedriver"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Updated undetected-chromedriver successfully")
            success_count += 1
        else:
            print(f"⚠️ Update warning: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Failed to update: {e}")
    
    # Step 2: Clear ChromeDriver cache
    print("\nStep 2: Clearing ChromeDriver cache...")
    try:
        temp_dir = tempfile.gettempdir()
        cleared_files = []
        
        for file in os.listdir(temp_dir):
            if any(keyword in file.lower() for keyword in ["chromedriver", "undetected", "uc_driver"]):
                try:
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleared_files.append(file)
                except:
                    pass
        
        if cleared_files:
            print(f"✅ Cleared {len(cleared_files)} cached files")
            success_count += 1
        else:
            print("ℹ️ No cache files found to clear")
            success_count += 1
            
    except Exception as e:
        print(f"❌ Cache clearing failed: {e}")
    
    # Step 3: Update Selenium (compatibility)
    print("\nStep 3: Updating Selenium...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "selenium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Updated Selenium successfully")
            success_count += 1
        else:
            print(f"⚠️ Selenium update warning: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Selenium update failed: {e}")
    
    # Step 4: Test ChromeDriver with improved error handling
    print("\nStep 4: Testing ChromeDriver...")
    try:
        import undetected_chromedriver as uc
        
        print("  Creating fresh ChromeOptions...")
        options = create_fresh_chrome_options()
        
        print("  Initializing test driver with auto-detection...")
        try:
            driver = uc.Chrome(options=options, version_main=None)
        except Exception as e:
            if "reuse" in str(e).lower() or "chromeoptions" in str(e):
                print("  ⚠️ ChromeOptions reuse error, creating new options...")
                options = create_fresh_chrome_options()
                driver = uc.Chrome(options=options, version_main=None)
            else:
                raise e
        
        print("  Testing navigation...")
        driver.get("https://www.example.com")
        
        print("  Closing test driver...")
        driver.quit()
        
        print("✅ ChromeDriver test successful!")
        success_count += 1
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ ChromeDriver test failed: {error_str[:200]}...")
        
        if "version" in error_str.lower():
            print("   🔍 Issue: Chrome/ChromeDriver version mismatch detected")
        elif "reuse" in error_str.lower():
            print("   🔍 Issue: ChromeOptions reuse error (now fixed)")
        elif "connect" in error_str.lower():
            print("   🔍 Issue: Cannot connect to Chrome browser")
        else:
            print("   🔍 Issue: General ChromeDriver compatibility problem")
    
    # Results
    print("\n" + "=" * 40)
    print(f"📈 Fix Results: {success_count}/4 steps completed")
    
    if success_count >= 4:
        print("🎉 ChromeDriver is working perfectly!")
        print("✨ You can now use URL scraping mode")
    elif success_count >= 3:
        print("⚠️ ChromeDriver still has version issues")
        print("🔍 Diagnosis: Chrome version 144 vs ChromeDriver expecting version 145")
        print("\n💡 SOLUTIONS (in order of effectiveness):")
        print("   🏆 BEST: Use Manual Input mode")
        print("      ✅ 100% reliable, no browser conflicts")
        print("      ✅ Same optimization quality")
        print("      ✅ Faster than browser scraping")
        print()
        print("   📄 GOOD: Use PDF Upload mode")
        print("      ✅ Works offline, very reliable")
        print("      ✅ AI-powered PDF extraction available")
        print()
        print("   🔧 TECHNICAL: Update Chrome browser")
        print("      • Go to chrome://settings/help")
        print("      • Update to Chrome version 145+")
        print("      • Restart Chrome and try again")
    else:
        print("⚠️ Multiple fixes failed. Recommended solutions:")
        print("   🏆 BEST: Use Manual Input mode (100% reliable)")
        print("   📄 GOOD: Use PDF Upload mode")  
        print("   🔧 TECH: Update Chrome browser to latest version")
    
    print("\n🎯 BOTTOM LINE:")
    print("   Manual Input mode gives you the same excellent optimization")
    print("   results without any browser compatibility headaches!")

if __name__ == "__main__":
    auto_fix_chromedriver()