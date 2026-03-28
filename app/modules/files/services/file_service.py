import aiofiles
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from fastapi import UploadFile, HTTPException

from app.core.config import get_settings

settings = get_settings()


def _resolve_extension(
    file: UploadFile,
    allowed_mime: Dict[str, str],
    fallback_exts: Dict[str, str],
) -> str:
    content_type = (file.content_type or "").lower()

    if content_type in allowed_mime:
        return allowed_mime[content_type]

    name = (file.filename or "").lower()
    for ext, normalized in fallback_exts.items():
        if name.endswith("." + ext):
            return normalized

    return ""


async def save_upload(
    file: UploadFile,
    *,
    allowed_mime: Dict[str, str],
    fallback_exts: Dict[str, str],
    kind: str,
    subdir: Optional[str] = None,
):
    ext = _resolve_extension(file, allowed_mime, fallback_exts)

    if not ext:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}",
        )

    base_dir = Path(settings.UPLOAD_DIR).resolve()

    target_root = base_dir / subdir if subdir else base_dir

    dated_dir = target_root / datetime.utcnow().strftime("%Y/%m/%d")
    dated_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.{ext}"
    file_path = dated_dir / filename

    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            await out.write(chunk)

    await file.close()

    relative = file_path.relative_to(base_dir).as_posix()
    public_path = f"/uploads/{relative}"

    return {
        "success": True,
        "path": public_path,
        "file_name": filename,
        "file_type": file.content_type,
        "file_size": file.size if hasattr(file, "size") else 0,
        "kind": kind,
        "original_name": file.filename,
    }