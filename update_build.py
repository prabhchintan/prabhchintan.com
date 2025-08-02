#!/usr/bin/env python3

def update_copy_assets():
    """Update the copy_assets method to include profile images"""
    
    with open('build.py', 'r') as f:
        content = f.read()
    
    # Find the copy_assets method
    old_method = '''    def copy_assets(self):
        """Copy CSS and other assets to site directory"""
        # Copy global CSS
        shutil.copy2(self.styles_dir / 'global.css', self.site_dir / 'global.css')
        
        # Copy fonts directory if it exists
        fonts_dir = Path('fonts/')
        if fonts_dir.exists():
            site_fonts_dir = self.site_dir / 'fonts'
            site_fonts_dir.mkdir(exist_ok=True)
            for font_file in fonts_dir.glob('*.ttf'):
                shutil.copy2(font_file, site_fonts_dir / font_file.name)
        
        print("✓ Copied assets to site/")'''
    
    new_method = '''    def copy_assets(self):
        """Copy CSS and other assets to site directory"""
        # Copy global CSS
        shutil.copy2(self.styles_dir / 'global.css', self.site_dir / 'global.css')
        
        # Copy fonts directory if it exists
        fonts_dir = Path('fonts/')
        if fonts_dir.exists():
            site_fonts_dir = self.site_dir / 'fonts'
            site_fonts_dir.mkdir(exist_ok=True)
            for font_file in fonts_dir.glob('*.ttf'):
                shutil.copy2(font_file, site_fonts_dir / font_file.name)
        
        # Copy profile images
        for img_file in ['profile.png', 'profile.jpg', 'profile_small.jpg']:
            if Path(img_file).exists():
                shutil.copy2(img_file, self.site_dir / img_file)
        
        print("✓ Copied assets to site/")'''
    
    content = content.replace(old_method, new_method)
    
    with open('build.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated build.py to copy profile images")

if __name__ == "__main__":
    update_copy_assets() 