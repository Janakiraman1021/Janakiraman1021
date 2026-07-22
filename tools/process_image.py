"""
Process the anime character image:
1. Remove white background (make transparent)
2. Save as PNG
3. Output base64 string for SVG embedding
"""
from PIL import Image
import base64
import io
import sys

def remove_white_bg(input_path, output_path, threshold=230):
    """Remove white/near-white background and make transparent."""
    img = Image.open(input_path).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        r, g, b, a = item
        # If pixel is white or near-white, make transparent
        if r > threshold and g > threshold and b > threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    
    img.putdata(new_data)
    
    # Crop to content (remove transparent borders)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    
    # Resize to reasonable size for embedding (max height 600px to keep base64 manageable)
    max_h = 600
    if img.height > max_h:
        ratio = max_h / img.height
        new_w = int(img.width * ratio)
        img = img.resize((new_w, max_h), Image.LANCZOS)
    
    img.save(output_path, "PNG", optimize=True)
    print(f"Saved transparent PNG: {output_path} ({img.width}x{img.height})")
    
    # Also create a cropped face version for the lanyard
    face_img = Image.open(input_path).convert("RGBA")
    face_data = face_img.getdata()
    face_new_data = []
    for item in face_data:
        r, g, b, a = item
        if r > threshold and g > threshold and b > threshold:
            face_new_data.append((255, 255, 255, 0))
        else:
            face_new_data.append(item)
    face_img.putdata(face_new_data)
    
    # Crop to content
    face_bbox = face_img.getbbox()
    if face_bbox:
        face_img = face_img.crop(face_bbox)
    
    # Take upper portion for face crop (top 45% of the image)
    face_h = int(face_img.height * 0.45)
    face_w = face_img.width
    # Center crop to square
    if face_w > face_h:
        left = (face_w - face_h) // 2
        face_img = face_img.crop((left, 0, left + face_h, face_h))
    else:
        face_img = face_img.crop((0, 0, face_w, face_h))
    
    # Resize face to 200x200 for lanyard
    face_img = face_img.resize((200, 200), Image.LANCZOS)
    face_path = output_path.replace('.png', '_face.png')
    face_img.save(face_path, "PNG", optimize=True)
    print(f"Saved face crop: {face_path} ({face_img.width}x{face_img.height})")
    
    return output_path, face_path

def to_base64(path):
    """Convert image file to base64 string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

if __name__ == "__main__":
    input_img = r"C:\Users\Janakiraman\.gemini\antigravity\brain\e60e768e-df20-4582-8871-32b197f4b3b3\media__1784713221003.jpg"
    output_img = r"e:\Janakiraman1021\tools\character.png"
    
    full_path, face_path = remove_white_bg(input_img, output_img)
    
    full_b64 = to_base64(full_path)
    face_b64 = to_base64(face_path)
    
    # Save base64 to files for later use
    with open(r"e:\Janakiraman1021\tools\character_b64.txt", "w") as f:
        f.write(full_b64)
    with open(r"e:\Janakiraman1021\tools\face_b64.txt", "w") as f:
        f.write(face_b64)
    
    print(f"\nFull image base64 length: {len(full_b64)} chars")
    print(f"Face image base64 length: {len(face_b64)} chars")
    print("Base64 data saved to tools/character_b64.txt and tools/face_b64.txt")
