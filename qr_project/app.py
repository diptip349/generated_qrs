import os
import qrcode
from datetime import datetime
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw

# Initialize Flask application
app = Flask(__name__)

# Folders to store uploaded logos and generated QR codes
UPLOAD_FOLDER = 'logos'
QR_FOLDER = 'generated_qrs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create logos folder if it doesn't exist
os.makedirs(QR_FOLDER, exist_ok=True)  # Create QR folder if it doesn't exist

# Function to generate a customizable QR code with different shapes
def generate_shape_qr_code(data, fill_color, back_color, shape):
    # Create a QRCode object with higher error correction (25% of the data can be recovered)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,  # Increased error correction to 25%
        box_size=10,
        border=4,
    )

    # Add data to the QR code
    qr.add_data(data)
    qr.make(fit=True)

    # Get the QR code matrix (2D array)
    qr_matrix = qr.modules
    size = len(qr_matrix) * 10  # Size of the QR code image
    img = Image.new("RGB", (size, size), back_color)  # Create an empty image with background color
    draw = ImageDraw.Draw(img)  # Create a drawing context to draw on the image

    # Loop through each module (square) in the QR code matrix and draw it based on the selected shape
    for row_idx, row in enumerate(qr_matrix):
        for col_idx, module in enumerate(row):
            if module:  # Only draw filled modules
                x0, y0 = col_idx * 10, row_idx * 10  # Top-left corner of the module
                x1, y1 = x0 + 10, y0 + 10  # Bottom-right corner of the module

                # Draw the selected shape based on user input
                if shape == "circle":
                    draw.ellipse([x0, y0, x1, y1], fill=fill_color)  # Draw a circle
                elif shape == "rounded":
                    draw.rounded_rectangle([x0, y0, x1, y1], radius=2, fill=fill_color)  # Draw a rounded rectangle
                elif shape == "triangle":
                    draw.polygon([(x0 + 5, y0), (x1, y1), (x0, y1)], fill=fill_color)  # Draw a triangle
                elif shape == "diamond":
                    draw.polygon([(x0 + 5, y0), (x1, y0 + 5), (x0 + 5, y1), (x0, y0 + 5)], fill=fill_color)  # Draw a diamond
                else:
                    draw.rectangle([x0, y0, x1, y1], fill=fill_color)  # Default to square

    return img  # Return the generated QR code image


# Function to add a logo to the center of the QR code image
def add_logo(qr_img, logo_path):
    try:
        # Open the logo image and convert to RGBA (to support transparency)
        logo = Image.open(logo_path).convert("RGBA")
        
        # Get the size of the QR code image
        qr_width, qr_height = qr_img.size
        logo_size = qr_width // 4  # Set logo size to be 1/4th the size of the QR code
        
        # Resize the logo while keeping its aspect ratio
        logo.thumbnail((logo_size, logo_size))

        # Create a white background to place the logo
        box_size = (logo.width + 20, logo.height + 20)
        white_box = Image.new("RGBA", box_size, (255, 255, 255, 255))  # White box around the logo
        pos = ((qr_width - box_size[0]) // 2, (qr_height - box_size[1]) // 2)  # Position of the logo
        logo_pos = (pos[0] + 10, pos[1] + 10)  # Add some padding for better visual appearance

        # Convert QR code to RGBA mode to support transparency when pasting the logo
        qr_img = qr_img.convert("RGBA")
        
        # Paste the white background and the logo on top of the QR code
        qr_img.paste(white_box, pos, white_box)
        qr_img.paste(logo, logo_pos, mask=logo)  # Use logo mask to keep transparency

    except Exception as e:
        print(f"Could not add logo: {e}")  # If an error occurs, print it
    return qr_img  # Return the updated QR code with the logo


# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')  # Render the index HTML page


# Route to handle QR code generation
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        # Get form data
        data = request.form['data']
        fill_color = request.form['fill_color']
        back_color = request.form['back_color']
        shape = request.form['shape']
        logo_file = request.files.get('logo')

        # Generate the QR code with the specified options
        qr_img = generate_shape_qr_code(data, fill_color, back_color, shape)

        # If a logo is provided, add it to the QR code
        if logo_file and logo_file.filename != '':
            logo_path = os.path.join(UPLOAD_FOLDER, logo_file.filename)
            logo_file.save(logo_path)
            qr_img = add_logo(qr_img, logo_path)

        # Get the format for saving the file (PNG or JPG)
        format_choice = request.args.get('format', 'png')

        # Create a unique filename based on the current timestamp
        filename = f"qr_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format_choice}"
        qr_path = os.path.abspath(os.path.join(QR_FOLDER, filename))  # Full path to save the file

        # Save the QR code in the selected format (either PNG or JPG)
        if format_choice == 'jpg':
            qr_img = qr_img.convert("RGB")  # Convert to RGB mode for JPG format
            qr_img.save(qr_path, format="JPEG")
        else:
            qr_img.save(qr_path, format="PNG")  # Save as PNG by default

        # If the file was not saved, raise an error
        if not os.path.exists(qr_path):
            raise FileNotFoundError(f"QR code image was not saved: {qr_path}")

        # Return the generated QR code file as a response
        return send_file(qr_path, mimetype=f'image/{format_choice}')

    except Exception as e:
        print(f"❌ Error generating QR: {e}")
        return f"Error generating QR: {e}", 500  # Return error message if an exception occurs


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)  # Start the app in debug mode for development
