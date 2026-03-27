import uuid
import os
from fastapi import UploadFile

BASE_UPLOAD_DIR = "uploads"

def generate_unique_filename(filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4().hex}{ext}"


def get_upload_path(file_type: str) -> str:
    if file_type.startswith("image"):
        return os.path.join(BASE_UPLOAD_DIR, "images")
    elif file_type.startswith("video"):
        return os.path.join(BASE_UPLOAD_DIR, "videos")
    elif file_type.startswith("audio"):
        return os.path.join(BASE_UPLOAD_DIR, "audios")
    else:
        return os.path.join(BASE_UPLOAD_DIR, "files")


async def save_file(file: UploadFile) -> tuple[str, str, str, int]:
    content = await file.read()

    file_type = file.content_type or "application/octet-stream"

    folder = get_upload_path(file_type)
    os.makedirs(folder, exist_ok=True)

    filename = file.filename or "file"
    unique_name = generate_unique_filename(filename)

    file_path = os.path.join(folder, unique_name)

    with open(file_path, "wb") as f:
        f.write(content)

    return file_path, unique_name, file_type, len(content)