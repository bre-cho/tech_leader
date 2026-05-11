from __future__ import annotations

import json
import logging
import mimetypes
import os
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_UPLOAD_INIT_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
_THUMBNAIL_URL = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"


class YouTubeNativeConfigError(RuntimeError):
    pass


class YouTubeNativeClient:
    """Minimal native YouTube Data API v3 client using stdlib urllib.

    Required env:
      YOUTUBE_CLIENT_ID
      YOUTUBE_CLIENT_SECRET
      YOUTUBE_REFRESH_TOKEN

    Optional env:
      YOUTUBE_ACCESS_TOKEN       hot token; refresh still supported
      YOUTUBE_TOKEN_URL          override for tests
      YOUTUBE_API_BASE_URL       override videos endpoint for tests
      YOUTUBE_UPLOAD_INIT_URL    override resumable init URL for tests
      YOUTUBE_THUMBNAIL_URL      override thumbnail URL for tests
    """

    def __init__(self, timeout_seconds: int = 60) -> None:
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "").strip()
        self.refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN", "").strip()
        self.access_token = os.getenv("YOUTUBE_ACCESS_TOKEN", "").strip()
        self.timeout_seconds = timeout_seconds
        self.token_url = os.getenv("YOUTUBE_TOKEN_URL", _TOKEN_URL).strip()
        self.upload_init_url = os.getenv("YOUTUBE_UPLOAD_INIT_URL", _UPLOAD_INIT_URL).strip()
        self.videos_url = os.getenv("YOUTUBE_API_BASE_URL", _VIDEOS_URL).strip()
        self.thumbnail_url = os.getenv("YOUTUBE_THUMBNAIL_URL", _THUMBNAIL_URL).strip()

    def ensure_access_token(self) -> str:
        if self.access_token:
            return self.access_token
        return self.refresh_access_token()

    def refresh_access_token(self) -> str:
        if not self.client_id or not self.client_secret or not self.refresh_token:
            raise YouTubeNativeConfigError(
                "Native YouTube publishing requires YOUTUBE_CLIENT_ID, "
                "YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN."
            )
        data = urllib.parse.urlencode(
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            }
        ).encode()
        req = urllib.request.Request(
            self.token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:  # noqa: S310
            body = json.loads(resp.read())
        token = str(body.get("access_token") or "")
        if not token:
            raise RuntimeError("YouTube OAuth refresh did not return access_token")
        self.access_token = token
        return token

    def publish_video(
        self,
        *,
        video_source: str,
        snippet: dict[str, Any],
        status: dict[str, Any],
        thumbnail_source: str | None = None,
        poll: bool = True,
    ) -> dict[str, Any]:
        token = self.ensure_access_token()
        local_video = self._materialize_video(video_source)
        try:
            upload_session_url = self._create_resumable_session(token, snippet=snippet, status=status)
            upload_result = self._upload_to_session(upload_session_url, local_video, token)
            video_id = str(upload_result.get("id") or upload_result.get("provider_publish_id") or "")
            thumbnail_result = None
            if thumbnail_source and video_id:
                local_thumbnail = self._materialize_video(thumbnail_source)
                thumbnail_result = self.upload_thumbnail(video_id=video_id, image_path=local_thumbnail, token=token)
            processing_result = self.poll_status(video_id=video_id, token=token) if poll and video_id else None
            return {
                "ok": True,
                "provider_publish_id": video_id,
                "upload": upload_result,
                "thumbnail": thumbnail_result,
                "processing": processing_result,
                "mode": "NATIVE_YOUTUBE_API",
            }
        finally:
            if local_video.startswith(tempfile.gettempdir()):
                try:
                    os.remove(local_video)
                except OSError as cleanup_exc:
                    _logger.warning("YouTubeNativeClient cleanup failed for %s: %s", local_video, cleanup_exc)

    def _create_resumable_session(self, token: str, *, snippet: dict[str, Any], status: dict[str, Any]) -> str:
        metadata = json.dumps({"snippet": snippet, "status": status}).encode()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/*",
        }
        req = urllib.request.Request(self.upload_init_url, data=metadata, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:  # noqa: S310
                location = resp.headers.get("Location") or resp.headers.get("location")
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                token = self.refresh_access_token()
                headers["Authorization"] = f"Bearer {token}"
                req = urllib.request.Request(self.upload_init_url, data=metadata, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:  # noqa: S310
                    location = resp.headers.get("Location") or resp.headers.get("location")
            else:
                raise
        if not location:
            raise RuntimeError("YouTube resumable upload session did not return Location header")
        return location

    def _upload_to_session(self, session_url: str, video_path: str, token: str) -> dict[str, Any]:
        path = Path(video_path)
        content_type = mimetypes.guess_type(path.name)[0] or "video/mp4"
        body = path.read_bytes()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
        }
        req = urllib.request.Request(session_url, data=body, headers=headers, method="PUT")
        with urllib.request.urlopen(req, timeout=max(self.timeout_seconds, 300)) as resp:  # noqa: S310
            return json.loads(resp.read() or b"{}")

    def poll_status(self, *, video_id: str, token: str | None = None, attempts: int = 12, delay_seconds: float = 10.0) -> dict[str, Any]:
        if not video_id:
            return {"ok": False, "error": "missing_video_id"}
        token = token or self.ensure_access_token()
        query = urllib.parse.urlencode({"part": "status,processingDetails", "id": video_id})
        url = f"{self.videos_url}?{query}"
        headers = {"Authorization": f"Bearer {token}"}
        last: dict[str, Any] = {}
        for _ in range(attempts):
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:  # noqa: S310
                raw = json.loads(resp.read() or b"{}")
            item = (raw.get("items") or [{}])[0]
            last = item
            processing = item.get("processingDetails") or {}
            status = processing.get("processingStatus")
            if status in {"succeeded", "failed", "terminated"}:
                return {"ok": status == "succeeded", "raw": item}
            time.sleep(delay_seconds)
        return {"ok": True, "pending": True, "raw": last}

    def upload_thumbnail(self, *, video_id: str, image_path: str, token: str | None = None) -> dict[str, Any]:
        token = token or self.ensure_access_token()
        path = Path(image_path)
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        query = urllib.parse.urlencode({"videoId": video_id})
        req = urllib.request.Request(
            f"{self.thumbnail_url}?{query}",
            data=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": content_type},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:  # noqa: S310
            return json.loads(resp.read() or b"{}")

    @staticmethod
    def _materialize_video(source: str) -> str:
        if not source:
            raise ValueError("missing media source")
        if source.startswith("http://") or source.startswith("https://"):
            suffix = Path(urllib.parse.urlparse(source).path).suffix or ".bin"
            fd, tmp = tempfile.mkstemp(prefix="yt-upload-", suffix=suffix)
            os.close(fd)
            urllib.request.urlretrieve(source, tmp)  # noqa: S310
            return tmp
        if source.startswith("/storage/"):
            candidate = Path("storage") / source.removeprefix("/storage/")
            if candidate.exists():
                return str(candidate)
        if not Path(source).exists():
            raise FileNotFoundError(f"media source not found: {source}")
        return source
