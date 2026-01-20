ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_stream, max_size_mb):
    file_stream.seek(0, 2)  # Move to end of file
    size = file_stream.tell()
    file_stream.seek(0)  # Reset to start of file
    return size <= max_size_mb * 1024 * 1024