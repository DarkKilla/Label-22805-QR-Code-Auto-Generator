import qrcode
from PIL import Image, ImageDraw, ImageFont
import random
import string
import os
import logging

# --- Configuration ---
NUM_CODES = 24
STRING_LENGTH = 5
OUTPUT_DIR = "qr_codes_with_titles"
IMAGE_FORMAT = "PNG" # e.g., PNG, JPEG

# QR Code settings
QR_BOX_SIZE = 10 # Size of each "box" in the QR code grid
QR_BORDER = 4    # Thickness of the border (usually 4 is good)

# Image settings
PADDING = 20      # White space around the QR code and text
TEXT_PADDING_TOP = 10 # Space between QR code and text
FONT_SIZE = 25
BACKGROUND_COLOR = "white"
TEXT_COLOR = "black"

# Font selection (adjust path if needed, or use default)
try:
    # Try a common system font (adjust path for your OS if necessary)
    # Windows: "arial.ttf"
    # MacOS: "/Library/Fonts/Arial.ttf"
    # Linux: often in /usr/share/fonts/truetype/... e.g., "DejaVuSans.ttf"
    FONT = ImageFont.truetype("arial.ttf", FONT_SIZE)
except IOError:
    print(f"Warning: Default font 'arial.ttf' not found. Using Pillow's default font.")
    try:
        FONT = ImageFont.load_default()
    except Exception as e:
        logging.error(f"Could not load even the default PIL font: {e}")
        print("Error: Could not load any font. Please install a font or check Pillow installation.")
        exit() # Exit if no font is available

# --- Helper Functions ---
def generate_random_string(length):
    """Generates a random alphanumeric string."""
    characters = string.ascii_uppercase + string.digits # Use uppercase letters and digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_qr_with_title(data_string, filename):
    """Generates a QR code image and adds the data_string as text below."""
    try:
        # 1. Generate the QR code itself
        qr = qrcode.QRCode(
            version=1, # Automatically determined if None, set manually if needed
            error_correction=qrcode.constants.ERROR_CORRECT_L, # L=Low, M, Q, H=High
            box_size=QR_BOX_SIZE,
            border=QR_BORDER,
        )
        qr.add_data(data_string)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=TEXT_COLOR, back_color=BACKGROUND_COLOR).convert('RGB')

        # 2. Prepare the canvas for the final image (QR + Text)
        qr_width, qr_height = qr_img.size

        # Calculate text size accurately
        draw_temp = ImageDraw.Draw(Image.new('RGB', (1,1))) # Temp draw object
        # Use textbbox for more accurate bounding box dimensions
        try:
             text_bbox = draw_temp.textbbox((0, 0), data_string, font=FONT)
             text_width = text_bbox[2] - text_bbox[0]
             text_height = text_bbox[3] - text_bbox[1]
        except AttributeError: # Fallback for older Pillow versions
            print("Using older textsize method (might be less accurate)")
            text_width, text_height = draw_temp.textsize(data_string, font=FONT)


        # Calculate final image dimensions
        total_width = max(qr_width, text_width) + 2 * PADDING
        total_height = qr_height + TEXT_PADDING_TOP + text_height + 2 * PADDING

        # 3. Create the final image canvas
        final_img = Image.new('RGB', (total_width, total_height), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(final_img)

        # 4. Paste the QR code onto the canvas
        qr_x = (total_width - qr_width) // 2
        qr_y = PADDING
        final_img.paste(qr_img, (qr_x, qr_y))

        # 5. Draw the text onto the canvas
        text_x = (total_width - text_width) // 2
        text_y = qr_y + qr_height + TEXT_PADDING_TOP
        draw.text((text_x, text_y), data_string, fill=TEXT_COLOR, font=FONT)

        # 6. Save the final image
        final_img.save(filename, IMAGE_FORMAT)
        print(f"Successfully created: {filename}")

    except Exception as e:
        logging.error(f"Failed to create QR code for '{data_string}': {e}")
        print(f"Error processing '{data_string}': {e}")


# --- Main Execution ---
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating {NUM_CODES} QR codes in directory '{OUTPUT_DIR}'...")

    generated_strings = set() # Keep track to avoid duplicates (optional but good)

    while len(generated_strings) < NUM_CODES:
        random_str = generate_random_string(STRING_LENGTH)
        if random_str not in generated_strings:
            generated_strings.add(random_str)
            # Sanitize filename slightly (though alphanumeric is usually safe)
            safe_filename = "".join(c if c.isalnum() else "_" for c in random_str)
            output_path = os.path.join(OUTPUT_DIR, f"{safe_filename}.{IMAGE_FORMAT.lower()}")
            create_qr_with_title(random_str, output_path)
        # Safety break in case string generation somehow gets stuck (highly unlikely)
        if len(generated_strings) > NUM_CODES * 2 and len(generated_strings) < NUM_CODES :
             print("Warning: Difficulty generating unique strings. Stopping.")
             break


    print(f"\nFinished generating {len(generated_strings)} QR codes.")
