"""
Script to create a simple icon for the application
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create a simple icon for the application"""
    
    # Create a 256x256 image with transparent background
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle background
    circle_color = (33, 150, 243, 255)  # Blue color
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], fill=circle_color)
    
    # Draw a mouse cursor icon
    cursor_color = (255, 255, 255, 255)  # White
    
    # Simple mouse cursor shape
    cursor_points = [
        (size//2 - 30, size//2 - 40),
        (size//2 - 30, size//2 + 20),
        (size//2 - 15, size//2 + 5),
        (size//2 - 5, size//2 + 30),
        (size//2 + 5, size//2 + 25),
        (size//2 - 5, size//2),
        (size//2 + 15, size//2 - 10),
    ]
    
    draw.polygon(cursor_points, fill=cursor_color)
    
    # Add click effect (small circles)
    for i in range(3):
        radius = 8 + i * 4
        alpha = 150 - i * 50
        click_color = (255, 255, 255, alpha)
        center_x, center_y = size//2 + 20, size//2 + 20
        
        # Create a separate image for the click effect
        click_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        click_draw = ImageDraw.Draw(click_img)
        click_draw.ellipse([center_x - radius, center_y - radius, 
                           center_x + radius, center_y + radius], 
                          outline=click_color, width=2)
        
        # Composite the click effect
        image = Image.alpha_composite(image, click_img)
    
    # Save as ICO file
    icon_path = 'icon.ico'
    image.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    
    print(f"Icon created: {icon_path}")
    return icon_path

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("PIL (Pillow) is required to create the icon.")
        print("The build will proceed without a custom icon.")
    except Exception as e:
        print(f"Error creating icon: {e}")
        print("The build will proceed without a custom icon.")
