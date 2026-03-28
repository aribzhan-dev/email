from typing import Dict

ALLOWED_IMAGE_TYPES: Dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

ALLOWED_VIDEO_TYPES: Dict[str, str] = {
    "video/mp4": "mp4",
    "video/mpeg": "mpeg",
    "video/quicktime": "mov",
    "video/x-msvideo": "avi",
    "video/x-ms-wmv": "wmv",
    "video/webm": "webm",
    "video/3gpp": "3gp",
    "video/3gpp2": "3g2",
    "video/x-matroska": "mkv",
    "video/mp2t": "ts",
    "video/x-flv": "flv",
}

ALLOWED_AUDIO_TYPES: Dict[str, str] = {
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/wave": "wav",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/aac": "aac",
    "audio/mp4": "m4a",
    "audio/3gpp": "3gp",
    "audio/amr": "amr",
    "audio/flac": "flac",
    "audio/x-flac": "flac",
}

ALLOWED_DOCUMENT_TYPES: Dict[str, str] = {
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.ms-excel": "xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-excel.sheet.macroenabled.12": "xlsm",
    "application/vnd.ms-powerpoint": "ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/vnd.ms-powerpoint.presentation.macroenabled.12": "pptm",
    "text/plain": "txt",
    "text/csv": "csv",
    "application/zip": "zip",
    "application/x-zip-compressed": "zip",
    "application/x-7z-compressed": "7z",
    "application/vnd.rar": "rar",
    "application/x-rar-compressed": "rar",
    "application/x-tar": "tar",
}

IMAGE_FALLBACK_EXTENSIONS: Dict[str, str] = {
    "jpg": "jpg",
    "jpeg": "jpg",
    "png": "png",
    "webp": "webp",
    "gif": "gif",
}

VIDEO_FALLBACK_EXTENSIONS: Dict[str, str] = {
    "mp4": "mp4",
    "mpeg": "mpeg",
    "mpg": "mpeg",
    "mov": "mov",
    "qt": "mov",
    "avi": "avi",
    "wmv": "wmv",
    "webm": "webm",
    "3gp": "3gp",
    "3g2": "3g2",
    "mkv": "mkv",
    "ts": "ts",
    "flv": "flv",
}

AUDIO_FALLBACK_EXTENSIONS: Dict[str, str] = {
    "mp3": "mp3",
    "wav": "wav",
    "weba": "webm",
    "webm": "webm",
    "ogg": "ogg",
    "oga": "ogg",
    "aac": "aac",
    "m4a": "m4a",
    "3gp": "3gp",
    "amr": "amr",
    "flac": "flac",
}

DOCUMENT_FALLBACK_EXTENSIONS: Dict[str, str] = {
    "pdf": "pdf",
    "doc": "doc",
    "docx": "docx",
    "xls": "xls",
    "xlsx": "xlsx",
    "xlsm": "xlsm",
    "ppt": "ppt",
    "pptx": "pptx",
    "pptm": "pptm",
    "txt": "txt",
    "csv": "csv",
    "zip": "zip",
    "7z": "7z",
    "rar": "rar",
    "tar": "tar",
}