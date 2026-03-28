from fastapi import APIRouter, UploadFile, File

from app.modules.files.services.file_service import save_upload
from app.modules.files.utils.file_types import *

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    return await save_upload(
        file,
        allowed_mime=ALLOWED_IMAGE_TYPES,
        fallback_exts=IMAGE_FALLBACK_EXTENSIONS,
        kind="image",
        subdir="images",
    )


@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    return await save_upload(
        file,
        allowed_mime=ALLOWED_VIDEO_TYPES,
        fallback_exts=VIDEO_FALLBACK_EXTENSIONS,
        kind="video",
        subdir="videos",
    )


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    return await save_upload(
        file,
        allowed_mime=ALLOWED_AUDIO_TYPES,
        fallback_exts=AUDIO_FALLBACK_EXTENSIONS,
        kind="audio",
        subdir="audios",
    )


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    return await save_upload(
        file,
        allowed_mime=ALLOWED_DOCUMENT_TYPES,
        fallback_exts=DOCUMENT_FALLBACK_EXTENSIONS,
        kind="document",
        subdir="documents",
    )