#!/usr/bin/env python3

def fix_image():
    """Update HTML to use smaller image and add debugging"""
    
    with open('index.html', 'r') as f:
        content = f.read()
    
    # Replace the image reference
    old_img = '<img src="profile.jpg" alt="Profile" width="80" height="80">'
    new_img = '<img src="profile_small.jpg" alt="Profile" width="80" height="80" onerror="console.log(\'Image failed to load\')" onload="console.log(\'Image loaded successfully\')">'
    
    content = content.replace(old_img, new_img)
    
    with open('index.html', 'w') as f:
        f.write(content)
    
    print("✅ Updated to use profile_small.jpg (20K instead of 248K)")
    print("✅ Added debugging to check if image loads")
    print("📁 New file size:", len(content), "bytes")

if __name__ == "__main__":
    fix_image() 