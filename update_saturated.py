#!/usr/bin/env python3

# Read the new saturated base64 data URL
with open('/home/prab/Downloads/saturated_data_url.txt', 'r') as f:
    new_image_data = f.read().strip()

# Read the current index.html
with open('index.html', 'r') as f:
    content = f.read()

# Find and replace the old image data URL
import re
old_pattern = r'src="data:image/jpeg;base64,[^"]*"'
new_src = f'src="{new_image_data}"'
updated_content = re.sub(old_pattern, new_src, content)

# Write the updated content back
with open('index.html', 'w') as f:
    f.write(updated_content)

print("✓ Updated index.html with new saturated image") 