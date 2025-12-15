"""
Image upload utility for handling file uploads with GUID-based filenames
"""
import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app
from app.config.settings import settings

# Allowed upload extensions (images + common document/audio/video formats)
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg',
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt',
    'mp4', 'mp3'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_folder():
    """Get the upload folder path"""
    base_dir = Path(settings.STATIC_FOLDER)
    upload_folder = base_dir / 'uploads'
    upload_folder.mkdir(parents=True, exist_ok=True)
    return str(upload_folder)

def get_upload_url_path(filename):
    """Get the URL path for an uploaded file"""
    # Normalize path separators for URL
    filename = filename.replace('\\', '/')
    return f'/static/uploads/{filename}'

def save_uploaded_file(file, subfolder=''):
    """
    Save an uploaded file with GUID-based filename
    
    Args:
        file: Werkzeug FileStorage object
        subfolder: Optional subfolder within uploads directory
    
    Returns:
        Relative URL path to the saved file, or None if upload failed
    """
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        raise ValueError(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}')
    
    # Get file extension
    ext = file.filename.rsplit('.', 1)[1].lower()
    
    # Generate GUID-based filename
    guid = str(uuid.uuid4())
    filename = f"{guid}.{ext}"
    
    # Get upload folder
    upload_folder = Path(get_upload_folder())
    if subfolder:
        upload_folder = upload_folder / subfolder
        upload_folder.mkdir(parents=True, exist_ok=True)
    
    # Save file
    filepath = upload_folder / filename
    file.save(str(filepath))
    
    # Optimize image if it's a raster format
    if ext.lower() in {'png', 'jpg', 'jpeg', 'webp'}:
        try:
            img = Image.open(filepath)
            # Convert RGBA to RGB for JPEG
            if ext.lower() == 'jpg' and img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            
            # Save optimized version
            img.save(filepath, optimize=True, quality=85)
        except Exception as e:
            # If optimization fails, keep original
            pass
    
    # Return relative URL path
    if subfolder:
        return get_upload_url_path(f"{subfolder}/{filename}")
    return get_upload_url_path(filename)

def delete_uploaded_file(url_path):
    """
    Delete an uploaded file by its URL path
    
    Args:
        url_path: URL path like '/static/uploads/filename.jpg'
    """
    if not url_path or not url_path.startswith('/static/uploads/'):
        return False
    
    # Extract filename from URL path
    filename = url_path.replace('/static/uploads/', '')
    filepath = Path(get_upload_folder()) / filename
    
    if filepath.exists():
        try:
            filepath.unlink()
            return True
        except Exception:
            return False
    return False
