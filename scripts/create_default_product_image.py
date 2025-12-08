"""
Create a default product image in standard size
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_default_product_image():
    """Create a default product placeholder image"""
    # Standard product image size (common e-commerce size: 800x800)
    width = 800
    height = 800
    
    # Create image with light gray background
    img = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    border_color = '#dee2e6'
    draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=3)
    
    # Draw icon/placeholder (simple box)
    box_size = 180
    box_x = (width - box_size) // 2
    box_y = (height - box_size) // 2 - 40
    
    # Draw placeholder box with accent color
    draw.rectangle([box_x, box_y, box_x + box_size, box_y + box_size], 
                   fill='#e9ecef', outline='#b19777', width=4)
    
    # Draw inner icon (simple image icon)
    icon_size = 80
    icon_x = box_x + (box_size - icon_size) // 2
    icon_y = box_y + (box_size - icon_size) // 2
    draw.rectangle([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], 
                   fill='#b19777', outline='#001f3f', width=2)
    
    # Try to use a font
    try:
        font_large = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    except:
        try:
            font_large = ImageFont.truetype("arial.ttf", 36)
            font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Draw text
    text = "No Image"
    text_bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = box_y + box_size + 25
    draw.text((text_x, text_y), text, fill='#6c757d', font=font_large)
    
    # Save image
    output_path = os.path.join('img', 'default-product.jpg')
    os.makedirs('img', exist_ok=True)
    img.save(output_path, 'JPEG', quality=90)
    print(f"Default product image created: {output_path}")
    print(f"Size: {width}x{height} pixels")

if __name__ == '__main__':
    create_default_product_image()
