from __future__ import annotations

from sqlalchemy.orm import Session


class AvatarRepo:
    """Lightweight avatar repository used by execution bridge."""

    def get_avatar(self, db: Session, avatar_id: str):
        if not avatar_id:
            return None
        try:
            from app.models.avatar_profile import AvatarProfile

            return db.query(AvatarProfile).filter(AvatarProfile.id == avatar_id).first()
        except Exception:
            return None
