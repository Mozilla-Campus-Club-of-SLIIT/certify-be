from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64

# Category-based style configuration
def get_certificate_style(category_code: str):
    """Return styling options based on category code.
    Extend this mapping to add new designs.
    Each style supports keys:
      title: override main certificate title
      gradient_start / gradient_end: RGB tuples for top/bottom border gradient
      background: base background color (RGB or hex)
      seal_color: fill color for the circular seal
      subtitle_color: color for subtitle text
      accent: optional accent color (unused currently)
    """
    styles = {
        "HOLAMOZILLA2025": {
            # Title can still be overridden by style; fallback is dynamic categoryName-based
            "title": None,
            "gradient_start": (138, 43, 226),  # purple
            "gradient_end": (255, 165, 0),     # orange
            "background": (255, 255, 255),
            "seal_color": (255, 193, 7),
            "subtitle_color": (0, 0, 255),
            # Layout / size overrides (zoomed out)
            "width": 900,
            "height": 600,
            "element_spacing": 60,
            "sig_img_size": (100, 42),
            # Reduced extra padding above event description (was 50)
            "event_extra_padding": 20,
            # Added extra bottom margin after event paragraph before signatures
            "event_bottom_spacing": 80
        },
        "PART": {
            "title": None,
            "gradient_start": (138, 43, 226),  # purple
            "gradient_end": (255, 165, 0),     # orange
            "background": (255, 255, 255),
            "seal_color": (255, 193, 7),
            "subtitle_color": (0, 0, 255),
            "width": 900,
            "height": 600,
            "element_spacing": 60,
            "sig_img_size": (100, 42),
            "event_extra_padding": 20,
            "event_bottom_spacing": 80
        },
        "ACHV": {
            "title": None,
            "gradient_start": (0, 90, 170),
            "gradient_end": (0, 200, 255),
            "background": (245, 250, 255),
            "seal_color": (240, 180, 0),
            "subtitle_color": (10, 90, 160),
            "width": 900,
            "height": 600,
            "element_spacing": 60,
            "sig_img_size": (100, 42),
            "event_extra_padding": 20,
            "event_bottom_spacing": 80
        },
        "MERIT": {
            "title": None,
            "gradient_start": (50, 50, 50),
            "gradient_end": (180, 180, 180),
            "background": (255, 255, 255),
            "seal_color": (212, 175, 55),  # metallic gold tone
            "subtitle_color": (80, 80, 80),
            "width": 900,
            "height": 600,
            "element_spacing": 60,
            "sig_img_size": (100, 42),
            "event_extra_padding": 20,
            "event_bottom_spacing": 80
        },
        "EXCEL": {
            "title": None,
            "gradient_start": (76, 0, 130),
            "gradient_end": (238, 130, 238),
            "background": (252, 248, 255),
            "seal_color": (180, 60, 200),
            "subtitle_color": (120, 40, 160),
            "width": 900,
            "height": 600,
            "element_spacing": 60,
            "sig_img_size": (100, 42),
            "event_extra_padding": 20,
            "event_bottom_spacing": 80
        }
    }
    # Set new default to HOLAMOZILLA2025 if not matched
    default_style = styles.get("HOLAMOZILLA2025")
    return styles.get(category_code.upper(), default_style)

def generate_certificate_image(cert):
    import os
    # Style selection based on categoryCode
    style = get_certificate_style(getattr(cert, 'categoryCode', 'PART'))
    # Create a blank themed image using style-provided dimensions if available
    width = style.get("width", 900)
    height = style.get("height", 600)
    image = Image.new("RGB", (width, height), style.get("background", (255, 255, 255)))
    draw = ImageDraw.Draw(image)
    
    # Add colorful gradient borders (top and bottom) - based on style gradient
    border_height = 15
    gs = style["gradient_start"]
    ge = style["gradient_end"]
    # Top border gradient
    for i in range(border_height):
        ratio = i / border_height
        r = int(gs[0] + (ge[0] - gs[0]) * ratio)
        g = int(gs[1] + (ge[1] - gs[1]) * ratio)
        b = int(gs[2] + (ge[2] - gs[2]) * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b), width=1)
    
    # Bottom border - same gradient
    for i in range(border_height):
        ratio = i / border_height
        r = int(gs[0] + (ge[0] - gs[0]) * ratio)
        g = int(gs[1] + (ge[1] - gs[1]) * ratio)
        b = int(gs[2] + (ge[2] - gs[2]) * ratio)
        draw.line([(0, height - border_height + i), (width, height - border_height + i)], fill=(r, g, b), width=1)

    # Define consistent spacing (style can override)
    element_spacing = style.get("element_spacing", 80)
    
    # Load and paste logo
    logo_path = os.path.join(os.path.dirname(__file__), "../assets/sliitmozilla-logo.png")
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_width = 140
        logo_height = int(logo.size[1] * (logo_width / logo.size[0]))
        logo = logo.resize((logo_width, logo_height), Image.LANCZOS)
        logo_top = 60  # vertical starting point for logo
        title_top_padding = 30  # extra space between logo bottom and title text
        image.paste(logo, (width // 2 - logo_width // 2, logo_top), logo)
        title_y = logo_top + logo_height + title_top_padding
    except Exception as e:
        print("Logo not found or error loading logo:", e)
        # fallback title position if logo missing
        title_y = 100  # include assumed padding

    # Load fonts robustly: try arial.ttf, then bundled DejaVuSans, then default
    font_dir = os.path.join(os.path.dirname(__file__), "../assets/fonts")
    import logging
    font_logger = logging.getLogger("certify.font")
    def load_font(font_name, size, label=None):
        try:
            font_logger.info(f"Trying to load font '{font_name}' for {label or font_name} at size {size}")
            f = ImageFont.truetype(font_name, size)
            font_logger.info(f"Loaded font '{font_name}' for {label or font_name}")
            return f
        except IOError:
            try:
                bundled = os.path.join(font_dir, "DejaVuSans.ttf")
                font_logger.warning(f"Font '{font_name}' not found for {label or font_name}, trying fallback '{bundled}'")
                f = ImageFont.truetype(bundled, size)
                font_logger.info(f"Loaded fallback font '{bundled}' for {label or font_name}")
                return f
            except IOError:
                font_logger.error(f"Font not found: {font_name} and fallback '{bundled}' failed for {label or font_name}, using default.")
                return ImageFont.load_default()

    font_title = load_font("arial.ttf", 28, "title")
    font_subtitle = load_font("arial.ttf", 12, "subtitle")
    font_name = load_font("arial.ttf", 40, "name")
    font_body = load_font("arial.ttf", 13, "body")
    font_sig_name = load_font("arial.ttf", 11, "signature name")
    font_sig_post = load_font("arial.ttf", 10, "signature post")

    # Draw certificate title - "CERTIFICATE OF PARTICIPATION"
    # Dynamic title: if style provides explicit title use that, else derive from categoryName or fallback
    dynamic_title = f"{getattr(cert, 'categoryName', getattr(cert, 'categoryCode', 'PARTICIPATION')).upper()}"
    title_text = style.get("title") or dynamic_title
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = width // 2 - title_width // 2
    draw.text((title_x, title_y), title_text, font=font_title, fill="black")

    # Draw subtitle - "We are proudly present this to"
    subtitle_y = title_y + element_spacing
    # Static subtitle per request (issuer ignored)
    subtitle_text = "We are proudly presenting this to"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_subtitle)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    # Force subtitle color to black (request override ignoring style color)
    subtitle_color = (0, 0, 0)
    draw.text((width // 2 - subtitle_width // 2, subtitle_y), subtitle_text, font=font_subtitle, fill=subtitle_color)

    # Draw recipient name (larger, bold style)
    name_y = subtitle_y + element_spacing
    name_bbox = draw.textbbox((0, 0), cert.name, font=font_name)
    name_width = name_bbox[2] - name_bbox[0]
    draw.text((width // 2 - name_width // 2, name_y), cert.name, font=font_name, fill="black")

    # Draw event description - with red highlight for event name
    # Add extra padding above event text for better visual separation from the name
    # Extra vertical space between recipient name and event description
    # Reduced from 50 -> 20 (can be overridden per style via 'event_extra_padding')
    event_extra_padding = style.get("event_extra_padding", 20)
    event_y = name_y + element_spacing + event_extra_padding
    # Dynamic event sentence; allow for future templating
    course = getattr(cert, 'course', 'the event')
    event_text = f"This is to certify that {cert.name} {course}."
    # Wrap text if too long
    event_bbox = draw.textbbox((0, 0), event_text, font=font_body)
    event_width = event_bbox[2] - event_bbox[0]
    if event_width > width - 300:
        # Simple text wrapping
        words = event_text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_bbox = draw.textbbox((0, 0), test_line, font=font_body)
            if test_bbox[2] - test_bbox[0] < width - 300:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        y_offset = event_y
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=font_body)
            line_width = line_bbox[2] - line_bbox[0]
            draw.text((width // 2 - line_width // 2, y_offset), line, font=font_body, fill="black")
            y_offset += 20
    else:
        draw.text((width // 2 - event_width // 2, event_y), event_text, font=font_body, fill="black")

    # Measure baseline metrics for later vertical balancing
    date_str = str(cert.dateIssued)
    date_bbox_tmp = draw.textbbox((0, 0), date_str, font=font_body)
    date_height = date_bbox_tmp[3] - date_bbox_tmp[1]
    sig_name_h = draw.textbbox((0, 0), "Ag", font=font_sig_name)[3] - draw.textbbox((0, 0), "Ag", font=font_sig_name)[1]
    sig_post_h = draw.textbbox((0, 0), "Ag", font=font_sig_post)[3] - draw.textbbox((0, 0), "Ag", font=font_sig_post)[1]

    # Draw signatures (base64 images) with debug logging - equal spacing from event text
    import logging
    logger = logging.getLogger("certify.signature")
    signatures = getattr(cert, 'signatures', [])
    logger.info(f"Signature count: {len(signatures)}")
    # Position signatures with consistent spacing below event text
    # Allow a larger adjustable gap below the event description before signatures
    event_bottom_spacing = style.get("event_bottom_spacing", element_spacing + 40)  # default adds extra 40px
    sig_y = event_y + event_bottom_spacing
    sig_x_left = 120
    sig_x_right = width - 220
    # Signature image size (style can override)
    sig_img_size = style.get("sig_img_size", (100, 42))
    seal_radius = 22
    seal_center_x = width // 2

    # Estimate total height of the lower block (signatures + seal section) to balance vertically
    # Signature block height approximation (signature image + spacing + line + spacing + name + spacing + post)
    signature_block_h = sig_img_size[1] + 5 + 1 + 5 + sig_name_h + 5 + sig_post_h
    seal_block_h = seal_radius * 2 + 12 + date_height  # seal + space + date
    lower_block_total = signature_block_h + element_spacing + seal_block_h

    # Compute approximate bottom after drawing at initial sig_y
    projected_bottom = sig_y + lower_block_total
    desired_bottom_margin = 140
    extra_space = (height - projected_bottom) - desired_bottom_margin
    if extra_space > 0:
        # Shift signatures & seal downward by half of the excess for better visual centering
        shift = extra_space // 2
        sig_y += shift

    # Now that sig_y potentially shifted, compute seal_y: align seal CENTER with signature images row
    seal_y = sig_y + sig_img_size[1] // 2  # center vertically in the signature image row

    def fix_base64_padding(b64_string):
        return b64_string + '=' * (-len(b64_string) % 4)
    
    def strip_data_uri(b64_string):
        """Remove data URI prefix like 'data:image/png;base64,' from base64 string"""
        if ',' in b64_string and b64_string.startswith('data:'):
            return b64_string.split(',', 1)[1]
        return b64_string

    # Draw yellow circular seal (after potential shift) centered between signatures in the SAME ROW
    seal_color = style.get("seal_color", (255, 193, 7))
    outline_color = (
        max(0, seal_color[0]-35),
        max(0, seal_color[1]-35),
        max(0, seal_color[2]-35)
    )
    draw.ellipse(
        [seal_center_x - seal_radius, seal_y - seal_radius,
         seal_center_x + seal_radius, seal_y + seal_radius],
        fill=seal_color,
        outline=outline_color,
        width=2
    )
    # We'll draw the date later below the entire signature block for cleaner hierarchy
    left_post_bottom = sig_y + sig_img_size[1]  # will update once left signature extras drawn
    right_post_bottom = sig_y + sig_img_size[1]

    if len(signatures) > 0:
        logger.info(f"Left signature: {signatures[0].name}, has image: {bool(signatures[0].image_b64)}")
        logger.info(f"Left signature base64 starts: {signatures[0].image_b64[:30]}")
        try:
            import base64
            from io import BytesIO
            clean_b64 = strip_data_uri(signatures[0].image_b64)
            sig_img_data = base64.b64decode(fix_base64_padding(clean_b64))
            sig_img = Image.open(BytesIO(sig_img_data)).convert("RGBA").resize(sig_img_size, Image.LANCZOS)
            image.paste(sig_img, (sig_x_left, sig_y), sig_img)
        except Exception as e:
            logger.error(f"Error loading left signature image: {e}")
        # Draw line below signature
        line_y = sig_y + sig_img_size[1] + 5
        draw.line([(sig_x_left, line_y), (sig_x_left + sig_img_size[0], line_y)], fill="black", width=1)
        # Centered name and post below line
        left_name = signatures[0].name
        name_bbox = draw.textbbox((0,0), left_name, font=font_sig_name)
        name_w = name_bbox[2] - name_bbox[0]
        name_x = sig_x_left + (sig_img_size[0] - name_w) // 2
        draw.text((name_x, line_y + 5), left_name, font=font_sig_name, fill="black")
        left_post = signatures[0].post
        post_text_bbox = draw.textbbox((0,0), left_post, font=font_sig_post)
        post_w = post_text_bbox[2] - post_text_bbox[0]
        post_x = sig_x_left + (sig_img_size[0] - post_w) // 2
        draw.text((post_x, line_y + 23), left_post, font=font_sig_post, fill="black")
        left_post_bottom = line_y + 23 + (post_text_bbox[3]-post_text_bbox[1])

    if len(signatures) > 1:
        logger.info(f"Right signature: {signatures[1].name}, has image: {bool(signatures[1].image_b64)}")
        logger.info(f"Right signature base64 starts: {signatures[1].image_b64[:30]}")
        try:
            clean_b64 = strip_data_uri(signatures[1].image_b64)
            sig_img_data = base64.b64decode(fix_base64_padding(clean_b64))
            sig_img = Image.open(BytesIO(sig_img_data)).convert("RGBA").resize(sig_img_size, Image.LANCZOS)
            image.paste(sig_img, (sig_x_right, sig_y), sig_img)
        except Exception as e:
            logger.error(f"Error loading right signature image: {e}")
        # Draw line below signature
        line_y = sig_y + sig_img_size[1] + 5
        draw.line([(sig_x_right, line_y), (sig_x_right + sig_img_size[0], line_y)], fill="black", width=1)
        # Centered name and post below line
        right_name = signatures[1].name
        r_name_bbox = draw.textbbox((0,0), right_name, font=font_sig_name)
        r_name_w = r_name_bbox[2] - r_name_bbox[0]
        r_name_x = sig_x_right + (sig_img_size[0] - r_name_w) // 2
        draw.text((r_name_x, line_y + 5), right_name, font=font_sig_name, fill="black")
        right_post = signatures[1].post
        post_text_bbox_r = draw.textbbox((0,0), right_post, font=font_sig_post)
        r_post_w = post_text_bbox_r[2] - post_text_bbox_r[0]
        r_post_x = sig_x_right + (sig_img_size[0] - r_post_w) // 2
        draw.text((r_post_x, line_y + 23), right_post, font=font_sig_post, fill="black")
        right_post_bottom = line_y + 23 + (post_text_bbox_r[3]-post_text_bbox_r[1])

    # Draw date centered below the lowest signature text (or below seal if no signatures)
    lowest = max(left_post_bottom, right_post_bottom)
    date_top_padding = 28
    date_y = lowest + date_top_padding
    date_bbox_final = draw.textbbox((0, 0), date_str, font=font_body)
    date_width = date_bbox_final[2] - date_bbox_final[0]
    draw.text((seal_center_x - date_width // 2, date_y), date_str, font=font_body, fill="black")

    # Save image to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    img_b64 = base64.b64encode(img_bytes.read()).decode("utf-8")
    return img_b64
