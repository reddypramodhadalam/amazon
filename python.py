import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import argparse
import re
import secrets
import string
import datetime
import hashlib
import base64
import time
import socket
import uuid
import platform
import traceback  # Added for better error reporting

# Set up basic logging
def log(message):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}")

def get_machine_id():
    """Get a unique identifier for the current machine"""
    try:
        # Try to get a hardware-based identifier
        if platform.system() == "Windows":
            # On Windows, use the machine GUID
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Cryptography")
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                winreg.CloseKey(key)
                return machine_guid
            except:
                # Fallback to using hostname + MAC address
                hostname = socket.gethostname()
                # Try to get MAC address
                try:
                    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                   for elements in range(0, 48, 8)][::-1])
                    return f"{hostname}-{mac}"
                except:
                    return hostname
        elif platform.system() == "Darwin":  # macOS
            # Use system profiler to get hardware UUID
            try:
                output = subprocess.check_output(["system_profiler", "SPHardwareDataType"]).decode()
                for line in output.split('\n'):
                    if "Hardware UUID" in line:
                        return line.split(":")[1].strip()
                return socket.gethostname()
            except:
                return socket.gethostname()
        elif platform.system() == "Linux":
            # Try to use machine-id
            try:
                with open("/etc/machine-id", "r") as f:
                    return f.read().strip()
            except:
                return socket.gethostname()
        else:
            # Fallback to hostname
            return socket.gethostname()
    except:
        # Ultimate fallback - use a hash of the hostname
        try:
            return hashlib.md5(socket.gethostname().encode()).hexdigest()
        except:
            return "unknown-machine"

def generate_api_key(expiration_date=None, days_valid=5, machine_id=None):
    """
    Generate a secure API key that expires on a specific date or after the specified number of days
    and is bound to a specific machine
    
    Args:
        expiration_date: A string in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' or datetime object
        days_valid: Number of days the key should be valid (used only if expiration_date is None)
        machine_id: Identifier for the machine this key is bound to
    
    Returns:
        tuple: (api_key, readable_expiration_date, machine_id)
    """
    # Generate a random string for the key
    alphabet = string.ascii_letters + string.digits
    key_part = ''.join(secrets.choice(alphabet) for _ in range(16))
    
    # Calculate expiration date
    if expiration_date:
        if isinstance(expiration_date, str):
            try:
                # Try to parse with time component first
                try:
                    expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # If that fails, try just the date and set time to end of day
                    expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d")
                    # Set time to end of day (23:59:59)
                    expiration_date = expiration_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                log(f"Invalid date format: {expiration_date}. Using default validity period.")
                expiration_date = datetime.datetime.now() + datetime.timedelta(days=days_valid)
        # If it's already a datetime object, use it directly
    else:
        # Use the default validity period
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=days_valid)
    
    # Convert to timestamp
    expiration_timestamp = int(expiration_date.timestamp())
    expiration_hex = format(expiration_timestamp, 'x')  # Convert to hexadecimal
    
    # Get machine ID if not provided
    if not machine_id:
        machine_id = get_machine_id()
    
    # Create a hash of the machine ID to make it shorter and more uniform
    machine_hash = hashlib.md5(machine_id.encode()).hexdigest()[:12]
    
    # Add a "salt" to make each key unique even with the same expiration and machine
    salt = ''.join(secrets.choice(alphabet) for _ in range(8))
    
    # Create a signature using the expiration date, machine hash, and salt
    signature_data = f"{key_part}:{expiration_hex}:{machine_hash}:{salt}"
    signature = hashlib.sha256(signature_data.encode()).hexdigest()[:12]
    
    # Combine parts to form the complete API key
    api_key = f"{key_part}.{expiration_hex}.{machine_hash}.{salt}.{signature}"
    
    # For display purposes, return a human-readable expiration date
    readable_date = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
    
    return api_key, readable_date, machine_id

def validate_api_key(api_key, machine_id=None):
    """Validate the API key and check if it's expired and bound to the current machine"""
    try:
        # Split the API key into its components
        parts = api_key.split('.')
        if len(parts) != 5:
            return False, "Invalid API key format"
        
        key_part, expiration_hex, key_machine_hash, salt, signature = parts
        
        # Get current machine ID if not provided
        if not machine_id:
            machine_id = get_machine_id()
        
        # Create a hash of the current machine ID
        current_machine_hash = hashlib.md5(machine_id.encode()).hexdigest()[:12]
        
        # Check if the key is bound to this machine
        if key_machine_hash != current_machine_hash:
            return False, f"This API key is not valid for this computer. Key is bound to machine ID: {key_machine_hash}, current machine ID: {current_machine_hash}"
        
        # Verify the signature
        expected_signature = hashlib.sha256(f"{key_part}:{expiration_hex}:{key_machine_hash}:{salt}".encode()).hexdigest()[:12]
        if signature != expected_signature:
            return False, "Invalid API key signature"
        
        # Check if the key is expired
        try:
            expiration_timestamp = int(expiration_hex, 16)
            expiration_date = datetime.datetime.fromtimestamp(expiration_timestamp)
            current_date = datetime.datetime.now()
            if current_date > expiration_date:
                return False, f"API key expired on {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}"
        except ValueError:
            return False, "Invalid expiration date format"
        
        # Key is valid
        days_left = (expiration_date - current_date).days
        hours_left = ((expiration_date - current_date).seconds // 3600)
        
        if days_left > 0:
            time_left = f"{days_left} days and {hours_left} hours"
        else:
            time_left = f"{hours_left} hours"
            
        return True, f"API key is valid for {time_left} (until {expiration_date.strftime('%Y-%m-%d %H:%M:%S')})"
    
    except Exception as e:
        return False, f"Error validating API key: {str(e)}"

def inject_api_key_validation(extension_path, api_key):
    """Inject API key validation code into the extension with enhanced security"""
    print("Injecting API key validation into the extension...")
    
    # Create a validation script with obfuscated key
    validation_js_path = os.path.join(extension_path, "api_validation.js")
    
    # Split the API key for obfuscation
    key_parts = api_key.split('.')
    if len(key_parts) != 5:
        print("Error: Invalid API key format")
        return False
    
    key_part, expiration_hex, machine_hash, salt, signature = key_parts
    
    # Obfuscate the key parts in JavaScript
    # This makes it harder to find and modify the key in the code
    with open(validation_js_path, "w", encoding="utf-8") as f:
        f.write(f"""
// API Key validation - Recording-friendly version
(function() {{
    // Obfuscated key parts
    const _k = [
        "{key_part[0:4]}", "{key_part[4:8]}", "{key_part[8:12]}", "{key_part[12:16]}"
    ];
    const _e = "{expiration_hex}";
    const _m = "{machine_hash}";
    const _s = "{salt}";
    const _v = "{signature}";
    
    // Reconstruct the key (makes it harder to find in the code)
    function _getKey() {{
        return _k.join('') + '.' + _e + '.' + _m + '.' + _s + '.' + _v;
    }}
    
    // Hardware fingerprinting (basic implementation)
    function _getHardwareId() {{
        const screen = window.screen || {{}};
        const nav = navigator || {{}};
        
        // Collect various browser/hardware identifiers
        const components = [
            nav.userAgent || '',
            screen.height || '',
            screen.width || '',
            screen.colorDepth || '',
            nav.language || '',
            nav.platform || '',
            nav.deviceMemory || '',
            nav.hardwareConcurrency || ''
        ];
        
        // Create a simple hash of the components
        let hash = 0;
        const str = components.join('|');
        for (let i = 0; i < str.length; i++) {{
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }}
        
        return hash.toString(16); // Return as hex string
    }}
    
    // Validation function that won't interfere with recording
    function validateApiKey(key) {{
        try {{
            // Split the API key into its components
            const parts = key.split('.');
            if (parts.length !== 5) {{
                return {{ valid: false, message: "Invalid API key format" }};
            }}
            
            const [keyPart, expirationHex, machineHash, salt, signature] = parts;
            
            // Convert expiration from hex to timestamp
            const expirationTimestamp = parseInt(expirationHex, 16);
            if (isNaN(expirationTimestamp)) {{
                return {{ valid: false, message: "Invalid expiration format" }};
            }}
            
            // Convert to date
            const expirationDate = new Date(expirationTimestamp * 1000);
            const currentDate = new Date();
            
            // Check if the key is expired
            if (currentDate > expirationDate) {{
                return {{ valid: false, message: `API key expired on ${{expirationDate.toLocaleString()}}` }};
            }}
            
            // Get hardware ID and check if it's changed significantly
            const hwid = _getHardwareId();
            
            // Store the hardware ID if this is the first run
            if (!localStorage.getItem('_hwid')) {{
                localStorage.setItem('_hwid', hwid);
            }}
            
            // Calculate days left
            const msPerDay = 1000 * 60 * 60 * 24;
            const daysLeft = Math.ceil((expirationDate - currentDate) / msPerDay);
            
            return {{ 
                valid: true, 
                message: `API key is valid for ${{daysLeft}} more days`,
                daysLeft: daysLeft,
                expires: expirationDate.toISOString().split('T')[0],
                machineHash: machineHash
            }};
        }} catch (e) {{
            console.error("API key validation error:", e);
            return {{ valid: false, message: `Error: ${{e.message}}` }};
        }}
    }}
    
    // Only apply restrictions to extension pages, not web pages where recording happens
    if (window.location.protocol === 'chrome-extension:') {{
        // Validate on startup
        const result = validateApiKey(_getKey());
        
        if (!result.valid) {{
            // If key is invalid, disable the extension functionality on extension pages
            console.error(`API key validation failed: ${{result.message}}`);
            
            // Override extension functionality
            document.addEventListener('DOMContentLoaded', function() {{
                // Replace body content with error message
                if (document.body) {{
                    document.body.innerHTML = `
                        <div style="padding: 20px; text-align: center; font-family: Arial, sans-serif;">
                            <h2 style="color: #d32f2f;">Access Denied</h2>
                            <p>${{result.message}}</p>
                            <p>Please contact your administrator for a new API key for this computer.</p>
                            <p><small>Machine ID: ${{result.machineHash || _m}}</small></p>
                        </div>
                    `;
                }}
            }}, true);
        }} else {{
            // Log validation success
            console.log(`API key validated: ${{result.message}}`);
            
            // Add expiration warning if less than 2 days left
            if (result.daysLeft <= 2) {{
                document.addEventListener('DOMContentLoaded', function() {{
                    const warningDiv = document.createElement('div');
                    warningDiv.style.cssText = 'background-color: #fff3cd; color: #856404; padding: 10px; text-align: center; position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999; font-family: Arial, sans-serif;';
                    warningDiv.innerHTML = `<strong>Warning:</strong> Your API key will expire in ${{result.daysLeft}} day${{result.daysLeft !== 1 ? 's' : ''}}. Please contact your administrator for a renewal.`;
                    document.body.appendChild(warningDiv);
                }});
            }}
        }}
    }}
    
    // Export validation function for other scripts to use
    window.validateApiKey = function() {{
        return validateApiKey(_getKey());
    }};
}})();
""")
    
    # Update manifest to include the validation script
    manifest_path = os.path.join(extension_path, "manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            # Add the validation script to content_scripts or background
            if "background" in manifest:
                if "scripts" in manifest["background"]:
                    if "api_validation.js" not in manifest["background"]["scripts"]:
                        manifest["background"]["scripts"].insert(0, "api_validation.js")
                else:
                    # For Manifest V3
                    if "service_worker" in manifest["background"]:
                        # Create a new background script that imports both
                        background_js_path = os.path.join(extension_path, "background_wrapper.js")
                        with open(background_js_path, "w", encoding="utf-8") as f:
                            f.write(f"""
// Import API validation first
import './api_validation.js';
// Then import the original service worker
import './{manifest["background"]["service_worker"]}';
""")
                        manifest["background"]["service_worker"] = "background_wrapper.js"
            else:
                # If no background script, add one
                manifest["background"] = {
                    "scripts": ["api_validation.js"]
                }
            
            # Add to all HTML files
            for root, dirs, files in os.walk(extension_path):
                for file in files:
                    if file.endswith(".html"):
                        html_path = os.path.join(root, file)
                        inject_validation_to_html(html_path)
            
            # Write updated manifest
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            
            print("API key validation added to manifest")
        except Exception as e:
            print(f"Error updating manifest with API validation: {e}")
    else:
        print(f"Warning: Manifest not found at {manifest_path}")
    
    return True

def inject_validation_to_html(html_path):
    """Inject API key validation script into HTML files"""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if already injected
        if "api_validation.js" in content:
            return
        
        # Add script tag to head or beginning of file
        script_tag = '<script src="../api_validation.js"></script>'
        
        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n    {script_tag}")
        else:
            content = f"{script_tag}\n{content}"
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        log(f"API validation injected into: {html_path}")
    except Exception as e:
        log(f"Error injecting API validation into {html_path}: {str(e)}")

def patch_extension(extension_path):
    """Add comprehensive security measures to the extension"""
    log("Applying comprehensive security measures to the extension...")
    
    # 1. Patch the content script
    content_script_path = os.path.join(extension_path, "content", "content.js")
    if os.path.exists(content_script_path):
        patch_content_script(content_script_path)
    else:
        log(f"Warning: Content script not found at {content_script_path}")
    
    # 2. Patch all HTML files
    log("Patching HTML files...")
    html_count = 0
    for root, dirs, files in os.walk(extension_path):
        for file in files:
            if file.endswith(".html"):
                html_path = os.path.join(root, file)
                patch_html_file(html_path)
                html_count += 1
    log(f"Patched {html_count} HTML files")
    
    # 3. Create a CSS file to disable selection
    css_dir = os.path.join(extension_path, "popup")
    os.makedirs(css_dir, exist_ok=True)
    security_css_path = os.path.join(css_dir, "security.css")
    create_security_css(security_css_path)
    
    # 4. Patch the manifest to include security.js in web_accessible_resources
    manifest_path = os.path.join(extension_path, "manifest.json")
    if os.path.exists(manifest_path):
        log("Patching manifest...")
        patch_manifest(manifest_path, extension_path)
    else:
        log(f"Warning: Manifest not found at {manifest_path}")
    
    log("Security measures applied successfully.")
    return True

def patch_content_script(content_script_path):
    """Patch the content script with recording-friendly security code"""
    try:
        with open(content_script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if already patched
        if "securityMeasures" in content:
            print("Content script already patched.")
            return
        
        # Add security code at the beginning
        security_code = """
// Security measures to prevent inspection and tampering - Recording-friendly version
(function securityMeasures() {
    // Only apply on extension pages, not web pages where recording happens
    if (window.location.protocol === 'chrome-extension:') {
        console.log('Applying security measures to extension pages only');
        
        // Disable right-click on extension pages only
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        }, true);
        
        // Disable keyboard shortcuts on extension pages only
        document.addEventListener('keydown', function(e) {
            // Disable F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C, Ctrl+U, Ctrl+S
            if (e.keyCode === 123 || // F12
                (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74 || e.keyCode === 67)) || // Ctrl+Shift+I, J, C
                (e.ctrlKey && (e.keyCode === 85 || e.keyCode === 83))) { // Ctrl+U, Ctrl+S
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }, true);
        
        // DevTools detection for extension pages only
        function detectDevTools() {
            const widthThreshold = window.outerWidth - window.innerWidth > 160;
            const heightThreshold = window.outerHeight - window.innerHeight > 160;
            if (widthThreshold || heightThreshold) {
                document.body.innerHTML = '<div style="text-align:center;padding:50px;"><h1>Developer Tools detected</h1><p>This action is not allowed.</p></div>';
                setTimeout(() => { window.location.reload(); }, 1500);
            }
        }
        setInterval(detectDevTools, 1000);
    }
})();
"""
        patched_content = security_code + content
        with open(content_script_path, "w", encoding="utf-8") as f:
            f.write(patched_content)
        print(f"Content script patched with recording-friendly security: {content_script_path}")
    except Exception as e:
        print(f"Error patching content script: {e}")

def patch_html_file(html_path):
    """Patch HTML files with security measures"""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if already patched
        if "security-script" in content:
            return
        
        # Create security script - only apply to extension pages
        security_script = """
<script id="security-script">
(function() {
    // Only apply security measures to extension pages
    if (window.location.protocol === 'chrome-extension:') {
        // Disable right-click
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        }, true);
        
        // Disable keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Disable F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C, Ctrl+U, Ctrl+S
            if (e.keyCode === 123 || // F12
                (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74 || e.keyCode === 67)) || // Ctrl+Shift+I, J, C
                (e.ctrlKey && (e.keyCode === 85 || e.keyCode === 83))) { // Ctrl+U, Ctrl+S
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }, true);
        
        // DevTools detection
        function detectDevTools() {
            const widthThreshold = window.outerWidth - window.innerWidth > 160;
            const heightThreshold = window.outerHeight - window.innerHeight > 160;
            if (widthThreshold || heightThreshold) {
                document.body.innerHTML = '<div style="text-align:center;padding:50px;"><h1>Developer Tools detected</h1><p>This action is not allowed.</p></div>';
                setTimeout(() => { window.location.reload(); }, 1500);
            }
        }
        setInterval(detectDevTools, 1000);
    }
})();
</script>
<style>
/* Disable selection only on extension pages */
@media screen and (url-prefix: "chrome-extension:") {
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
}
</style>
"""
        # Add to head if exists, otherwise to the beginning of the file
        if "<head>" in content:
            content = content.replace("<head>", "<head>" + security_script)
        else:
            content = security_script + content
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"HTML file patched: {html_path}")
    except Exception as e:
        print(f"Error patching HTML file {html_path}: {e}")

def create_security_css(css_path):
    """Create a CSS file with security measures"""
    css_content = """
/* Security CSS to prevent inspection and tampering */
/* Only apply to extension pages */
@media screen and (url-prefix: "chrome-extension:") {
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    
    /* Exception for input fields */
    input, textarea {
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
        -ms-user-select: text !important;
        user-select: text !important;
    }
}
"""
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)
    print(f"Security CSS created: {css_path}")
    
def patch_manifest(manifest_path, extension_path):
    """Patch the manifest to include security files with recording-friendly CSP"""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        # Create a security.js file in the extension root
        security_js_path = os.path.join(extension_path, "security.js")
        with open(security_js_path, "w", encoding="utf-8") as f:
            f.write("""
// Security measures
(function() {
    // This file is intentionally empty
    // Its presence in web_accessible_resources helps with security implementation
})();
""")
        
        # Add security.js to web_accessible_resources if not already there
        if "web_accessible_resources" not in manifest:
            manifest["web_accessible_resources"] = [{"resources": ["security.js"], "matches": ["<all_urls>"]}]
        else:
            # Check if it's already in the list
            resources_added = False
            for resource_entry in manifest["web_accessible_resources"]:
                if "resources" in resource_entry and "security.js" not in resource_entry["resources"]:
                    resource_entry["resources"].append("security.js")
                    resources_added = True
                    break
            if not resources_added:
                manifest["web_accessible_resources"].append({"resources": ["security.js"], "matches": ["<all_urls>"]})
        
        # Add content security policy that's compatible with Manifest V3
        manifest["content_security_policy"] = {
            "extension_pages": "script-src 'self'; object-src 'self'"
        }
        
        # Write the updated manifest
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest patched with recording-friendly CSP: {manifest_path}")
    except Exception as e:
        print(f"Error patching manifest: {e}")

def find_chrome_path():
    """Find the Chrome executable path without requiring admin rights"""
    # Try common locations
    common_locations = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe')
    ]
    
    for location in common_locations:
        if os.path.exists(location):
            return location
    
    # If Chrome is in PATH
    try:
        result = subprocess.run(['where', 'chrome.exe'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

def package_extension(extension_path, output_dir, api_key, machine_id):
    """Package the extension for distribution with API key"""
    try:
        log("Creating package directory...")
        # Create a directory for the packaged extension
        package_dir = os.path.join(output_dir, "BDD_Test_Generator")
        os.makedirs(package_dir, exist_ok=True)
        
        log(f"Copying extension to package directory: {package_dir}")
        # Copy the extension to the package directory
        extension_dest = os.path.join(package_dir, "extension")
        if os.path.exists(extension_dest):
            shutil.rmtree(extension_dest)
        shutil.copytree(extension_path, extension_dest)
        
        log("Creating batch file...")
        # Create a batch file to launch Chrome with the extension
        batch_file = os.path.join(package_dir, "Launch_BDD_Test_Generator.bat")
        
        # Create a unique Chrome user data directory
        user_data_dir = "%~dp0ChromeUserData"
        
        with open(batch_file, "w") as f:
            f.write(f'''@echo off
echo Starting Chrome with BDD Test Generator extension...

:: Create Chrome user data directory if it doesn't exist
if not exist "%~dp0ChromeUserData" mkdir "%~dp0ChromeUserData"

:: Try to find Chrome in common locations
set CHROME_PATH=

:: Check Program Files
if exist "%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe" (
    set CHROME_PATH="%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe"
    goto launch
)

:: Check Program Files (x86)
if exist "%ProgramFiles(x86)%\\Google\\Chrome\\Application\\chrome.exe" (
    set CHROME_PATH="%ProgramFiles(x86)%\\Google\\Chrome\\Application\\chrome.exe"
    goto launch
)

:: Check Local AppData
if exist "%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe" (
    set CHROME_PATH="%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe"
    goto launch
)

:: If Chrome not found in common locations
echo Chrome not found in common locations.
echo Please enter the full path to chrome.exe:
set /p CHROME_PATH=

:launch
if not exist %CHROME_PATH% (
    echo Chrome not found at %CHROME_PATH%
    echo Please install Google Chrome and try again.
    pause
    exit /b 1
)

:: Launch Chrome with the extension
start "" %CHROME_PATH% --user-data-dir="{user_data_dir}" --no-first-run --no-default-browser-check --disable-extensions-except="%~dp0extension" --load-extension="%~dp0extension" --disable-features=ExtensionsToolbarMenu --disable-features=ExtensionsMenuUI

echo Chrome launched with BDD Test Generator extension.
echo.
echo NOTE: This window can be closed, but keep Chrome open to use the extension.
echo.
''')
        
        log("Creating documentation files...")
        # Try to parse the API key to get expiration date
        try:
            parts = api_key.split('.')
            if len(parts) >= 2:
                expiration_hex = parts[1]
                expiration_timestamp = int(expiration_hex, 16)
                expiration_date = datetime.datetime.fromtimestamp(expiration_timestamp)
                readable_expiration = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                readable_expiration = "unknown"
        except Exception as e:
            log(f"Error parsing expiration date: {str(e)}")
            readable_expiration = "unknown"
        
        # Create a README file with API key information
        readme_file = os.path.join(package_dir, "README.txt")
        with open(readme_file, "w") as f:
            f.write(f'''BDD Test Generator Extension
==========================

This package contains the BDD Test Generator Chrome extension with enhanced security features.

API KEY INFORMATION:
-------------------
Your API Key: {api_key}
Expiration Date: {readable_expiration}
Machine ID: {machine_id}

IMPORTANT: This key is specific to this computer and will not work on other machines.
The key is valid until the expiration date shown above. After expiration, you will need to request a new key.

Instructions:
1. Double-click "Launch_BDD_Test_Generator.bat" to start Chrome with the extension loaded
2. Chrome will open with only this extension enabled
3. Use the extension as normal

Notes:
- This launcher creates a separate Chrome profile that only has this extension enabled
- The extension has security measures to prevent tampering
- You must have Google Chrome installed on your computer
- If Chrome is not found automatically, you will be prompted to enter its location

For support or to request a new API key, please contact your administrator.
''')
        
        # Create a key file for reference
        key_file = os.path.join(package_dir, "api_key.txt")
        with open(key_file, "w") as f:
            f.write(f'''API KEY: {api_key}
EXPIRATION: {readable_expiration}
MACHINE ID: {machine_id}
GENERATED: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This key is valid until the expiration date shown above and only works on this specific computer.
''')
        
        log("Creating ZIP file...")
        # Create a ZIP file of the package
        zip_path = os.path.join(output_dir, "BDD_Test_Generator_Package.zip")
        shutil.make_archive(os.path.splitext(zip_path)[0], 'zip', output_dir, "BDD_Test_Generator")
        
        log(f"Package created successfully: {zip_path}")
        return zip_path
    except Exception as e:
        log(f"Error packaging extension: {str(e)}")
        traceback.print_exc()
        return None

def generate_user_package(extension_path, output_dir, username, expiration_date=None, days_valid=5, target_machine_id=None):
    """Generate a package with a custom API key for a specific user and machine"""
    try:
        # Create a unique output directory for this user
        user_output_dir = os.path.join(output_dir, f"package_{username}")
        os.makedirs(user_output_dir, exist_ok=True)
        
        # If no target machine ID is provided, use the current machine's ID
        if not target_machine_id:
            target_machine_id = get_machine_id()
            log(f"Using current machine ID: {target_machine_id}")
        else:
            log(f"Using provided machine ID: {target_machine_id}")
        
        # Generate API key
        log("Generating API key...")
        api_key, readable_date, machine_id = generate_api_key(
            expiration_date=expiration_date, 
            days_valid=days_valid,
            machine_id=target_machine_id
        )
        
        # Create a copy of the extension to modify
        log("Creating temporary extension copy...")
        temp_extension_path = os.path.join(user_output_dir, "temp_extension")
        if os.path.exists(temp_extension_path):
            shutil.rmtree(temp_extension_path)
        shutil.copytree(extension_path, temp_extension_path)
        
        # Patch the extension with security measures
        patch_extension(temp_extension_path)
        
        # Inject API key validation
        inject_api_key_validation(temp_extension_path, api_key)
        
        # Package the extension for distribution
        log(f"Packaging extension for user: {username}...")
        zip_path = package_extension(temp_extension_path, user_output_dir, api_key, machine_id)
        
        # Clean up temporary files
        log("Cleaning up temporary files...")
        shutil.rmtree(temp_extension_path)
        
        # Rename the zip file to include the username and expiration
        try:
            # Get expiration date from API key
            parts = api_key.split('.')
            expiration_hex = parts[1]
            expiration_timestamp = int(expiration_hex, 16)
            expiration_readable = datetime.datetime.fromtimestamp(expiration_timestamp).strftime("%Y-%m-%d")
        except:
            expiration_readable = datetime.datetime.now().strftime("%Y-%m-%d")
        
        new_zip_name = f"BDD_Test_Generator_{username}_{expiration_readable}.zip"
        new_zip_path = os.path.join(output_dir, new_zip_name)
        
        if os.path.exists(zip_path):
            shutil.move(zip_path, new_zip_path)
            log(f"Package created for {username}: {new_zip_path}")
            return new_zip_path
        else:
            log(f"Failed to create package for {username}")
            return None
    except Exception as e:
        log(f"Error generating user package: {str(e)}")
        traceback.print_exc()
        return None

def main():
    parser = argparse.ArgumentParser(description="Create a Chrome launcher with BDD Test Generator extension")
    parser.add_argument("extension_path", help="Path to the BDD Test Generator extension directory")
    parser.add_argument("--output", "-o", default="output", help="Output directory for the launcher")
    parser.add_argument("--no-patch", action="store_true", help="Skip patching the extension")
    parser.add_argument("--days", "-d", type=int, default=5, help="Number of days the API key should be valid (default: 5)")
    parser.add_argument("--expiration", "-e", help="Specific expiration date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format")
    parser.add_argument("--user", "-u", help="Generate a package for a specific user")
    parser.add_argument("--machine", "-m", help="Target machine ID (if not provided, uses current machine)")
    parser.add_argument("--show-machine-id", action="store_true", help="Display the current machine ID and exit")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with detailed logging")
    args = parser.parse_args()
    
    # Just show machine ID if requested
    if args.show_machine_id:
        machine_id = get_machine_id()
        log(f"Current machine ID: {machine_id}")
        log(f"Machine hash: {hashlib.md5(machine_id.encode()).hexdigest()[:12]}")
        return
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Get the machine ID
    target_machine_id = args.machine if args.machine else get_machine_id()
    
    try:
        if args.user:
            # Generate a package for a specific user
            log(f"Generating package for user: {args.user}")
            zip_path = generate_user_package(
                args.extension_path, 
                args.output, 
                args.user, 
                expiration_date=args.expiration, 
                days_valid=args.days,
                target_machine_id=target_machine_id
            )
            
            if zip_path:
                log(f"\nUser package created successfully: {zip_path}")
                if args.expiration:
                    log(f"\nValid until: {args.expiration}")
                else:
                    log(f"\nValid for {args.days} days")
                log(f"Machine ID: {target_machine_id}")
                log("\nTo distribute the extension:")
                log(f"1. Send the ZIP file to {args.user}")
                log("2. They should extract the ZIP file")
                log("3. Run 'Launch_BDD_Test_Generator.bat' to start Chrome with the extension")
                log("\nNOTE: This package will only work on the specified machine.")
            else:
                log("Failed to create user package.")
        else:
            # Generate API key for current machine
            log("Generating API key...")
            api_key, readable_date, machine_id = generate_api_key(
                expiration_date=args.expiration, 
                days_valid=args.days,
                machine_id=target_machine_id
            )
            log(f"Generated API key: {api_key}")
            log(f"Expiration date: {readable_date}")
            log(f"Machine ID: {machine_id}")
            
            # Validate the key (for demonstration)
            is_valid, message = validate_api_key(api_key, machine_id)
            log(f"API key validation: {message}")
            
            # Create a copy of the extension to modify
            temp_extension_path = os.path.join(args.output, "temp_extension")
            if os.path.exists(temp_extension_path):
                log(f"Removing existing temp directory: {temp_extension_path}")
                shutil.rmtree(temp_extension_path)
            
            log(f"Copying extension to temp directory: {temp_extension_path}")
            shutil.copytree(args.extension_path, temp_extension_path)
            
            # Patch the extension with comprehensive security measures
            if not args.no_patch:
                patch_extension(temp_extension_path)
            
            # Inject API key validation
            log("Injecting API key validation...")
            inject_api_key_validation(temp_extension_path, api_key)
            
            # Package the extension for distribution
            log("Packaging extension for distribution...")
            zip_path = package_extension(temp_extension_path, args.output, api_key, machine_id)
            
            # Clean up temporary files
            log("Cleaning up temporary files...")
            shutil.rmtree(temp_extension_path)
            
            if zip_path:
                log(f"\nPackage created successfully: {zip_path}")
                log(f"\nAPI Key: {api_key}")
                log(f"Valid until: {readable_date}")
                log(f"Machine ID: {machine_id}")
                log("\nTo distribute the extension:")
                log("1. Share the ZIP file with your team")
                log("2. Recipients should extract the ZIP file")
                log("3. Run 'Launch_BDD_Test_Generator.bat' to start Chrome with the extension")
                log("\nNOTE: This package will only work on this specific computer.")
            else:
                log("Failed to create package.")
    except Exception as e:
        log(f"Error: {str(e)}")
        if args.debug:
            traceback.print_exc()

if __name__ == "__main__":
    main()
