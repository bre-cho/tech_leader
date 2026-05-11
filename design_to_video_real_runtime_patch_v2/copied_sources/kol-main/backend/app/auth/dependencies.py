from __future__ import annotations

import logging
from collections.abc import Callable

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_log = logging.getLogger(__name__)
_bearer = HTTPBearer(auto_error=False)


def _verify_credentials(
    permission: str,
    credentials: HTTPAuthorizationCredentials | None,
) -> None:
    """Verify Bearer token (JWT or static API key) and raise HTTP 401/403 on failure.

    Behaviour
    ---------
    * When ``AUTH_ENABLED=false`` (default in non-production), the check is
      skipped and a debug log is emitted so developers can spot the bypass.
    * When ``AUTH_ENABLED=true``:
        1. A ``Bearer`` token must be present in the ``Authorization`` header.
        2. If the token matches ``settings.api_key`` it is accepted.
        3. Otherwise the token is decoded as a HS256 JWT signed with
           ``settings.jwt_secret_key`` and the ``permissions`` claim is
           checked for the required *permission*.
    * When ``AUTH_ENABLED=true`` but neither ``jwt_secret_key`` nor
      ``api_key`` is configured, a 500 is raised to surface the
      misconfiguration immediately rather than silently accepting all traffic.
    """
    from app.core.config import settings  # noqa: PLC0415

    if not settings.auth_enabled:
        _log.debug(
            "auth: AUTH_ENABLED=false — skipping permission check for %r (env=%s)",
            permission,
            settings.app_env,
        )
        return

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header.  Provide: Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 1. Static API key check (fast path).
    if settings.api_key and token == settings.api_key:
        _log.debug("auth: static API key accepted for permission %r", permission)
        return

    # 2. JWT verification.
    jwt_secrets: list[str] = []
    raw_secret_keys = getattr(settings, "jwt_secret_keys", None)
    if isinstance(raw_secret_keys, str) and raw_secret_keys.strip():
        jwt_secrets.extend(
            [s.strip() for s in raw_secret_keys.split(",") if s.strip()]
        )
    if isinstance(settings.jwt_secret_key, str) and settings.jwt_secret_key:
        jwt_secrets.append(settings.jwt_secret_key)
    # preserve order while removing duplicates
    jwt_secrets = list(dict.fromkeys(jwt_secrets))

    if not jwt_secrets:
        _log.error(
            "auth: AUTH_ENABLED=true but JWT secrets are not set.  "
            "Set JWT_SECRET_KEY/JWT_SECRET_KEYS or API_KEY in the environment."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server auth misconfiguration: JWT secrets not set.",
        )

    raw_expected_issuer = getattr(settings, "jwt_expected_issuer", None)
    raw_expected_audience = getattr(settings, "jwt_expected_audience", None)
    expected_issuer = raw_expected_issuer.strip() if isinstance(raw_expected_issuer, str) and raw_expected_issuer.strip() else None
    expected_audience = raw_expected_audience.strip() if isinstance(raw_expected_audience, str) and raw_expected_audience.strip() else None

    try:
        import jwt  # noqa: PLC0415 — PyJWT is in requirements.txt
        payload = None
        decode_errors: list[str] = []
        for secret in jwt_secrets:
            try:
                payload = jwt.decode(
                    token,
                    secret,
                    algorithms=["HS256"],
                    audience=expected_audience,
                    issuer=expected_issuer,
                    options={
                        "verify_aud": expected_audience is not None,
                        "verify_iss": expected_issuer is not None,
                    },
                )
                break
            except Exception as exc:  # noqa: BLE001
                decode_errors.append(str(exc))
        if payload is None:
            raise RuntimeError("; ".join(decode_errors) or "JWT decode failed")
    except Exception as exc:  # noqa: BLE001
        _log.warning("auth: JWT decode failed for permission %r: %s", permission, exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    perms: list[str] = payload.get("permissions") or []
    if permission not in perms:
        _log.warning(
            "auth: JWT does not carry permission %r (has: %s)",
            permission,
            perms,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token does not have the required permission: {permission!r}",
        )

    _log.debug("auth: JWT accepted for permission %r (sub=%s)", permission, payload.get("sub"))


def require_permission(permission: str) -> Callable[..., None]:
    """Return a FastAPI dependency that enforces *permission* on the caller.

    Usage::

        @router.post("/execute", dependencies=[Depends(require_permission("execute:provider"))])
        def my_endpoint(...): ...

    When ``AUTH_ENABLED=false`` the check is skipped (non-production default).
    When ``AUTH_ENABLED=true`` a valid Bearer token (JWT or static API key)
    carrying the required *permission* must be present.
    """

    def _dependency(
        credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
    ) -> None:
        _verify_credentials(permission, credentials)

    return _dependency
