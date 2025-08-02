#!/usr/bin/env python3

def try_png():
    """Update HTML to use PNG version of the image"""
    
    with open('index.html', 'r') as f:
        content = f.read()
    
    # Replace the image reference
    old_img = '<img src="profile_small.jpg" alt="Profile" width="80" height="80" onerror="console.log(\'Image failed to load\')" onload="console.log(\'Image loaded successfully\')">'
    new_img = '<img src="profile.png" alt="Profile" width="80" height="80" onerror="console.log(\'Image failed to load\')" onload="console.log(\'Image loaded successfully\')">'
    
    content = content.replace(old_img, new_img)
    
    with open('index.html', 'w') as f:
        f.write(content)
    
    print("✅ Updated to use profile.png")
    print("📁 File size:", len(content), "bytes")

if __name__ == "__main__":
    try_png() 