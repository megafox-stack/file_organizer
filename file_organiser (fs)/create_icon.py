from PIL import Image, ImageDraw
import os

def create_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        # Create image
        image = Image.new('RGBA', (size, size), (0, 120, 215, 255))  # Blue background
        draw = ImageDraw.Draw(image)

        # Scale elements based on size
        scale = size / 256
        folder_left = int(50 * scale)
        folder_top = int(100 * scale)
        folder_right = int(200 * scale)
        folder_bottom = int(200 * scale)
        tab_left = int(60 * scale)
        tab_top = int(80 * scale)
        tab_right = int(140 * scale)
        tab_bottom = int(100 * scale)
        text_x = int(100 * scale)
        text_y = int(140 * scale)
        font_size = max(10, int(40 * scale))  # Minimum font size

        # Draw folder base
        draw.rectangle([folder_left, folder_top, folder_right, folder_bottom],
                      fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        # Draw folder tab
        draw.rectangle([tab_left, tab_top, tab_right, tab_bottom],
                      fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))

        # Add text "FO"
        try:
            # Try to use a better font if available
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = None
        draw.text((text_x, text_y), "FO", fill=(0, 120, 215, 255), font=font)

        images.append(image)

    # Save as ICO with multiple sizes
    icon_path = os.path.join(os.getcwd(), 'file_organizer_icon.ico')
    images[0].save(icon_path, format='ICO', sizes=[(img.size[0], img.size[0]) for img in images])
    print(f"Icon created at: {icon_path}")
    print(f"Includes sizes: {[img.size[0] for img in images]}")

if __name__ == "__main__":
    create_icon()