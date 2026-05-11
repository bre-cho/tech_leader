# 12 — ENV AND PROVIDER CONFIG

## Backend common

```bash
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/design_video
REDIS_URL=redis://localhost:6379/0
APP_ENV=development
PUBLIC_BASE_URL=http://localhost:8000
```

## Image/poster runtime

Nếu dùng poster-engine-backend:

```bash
POSTER_ENGINE_BASE_URL=http://localhost:8010
IMAGE_PROVIDER_MODE=poster_engine_backend
IMAGE_GENERATION_REQUIRED=true
```

Nếu dùng Next route từ `veo-main-7`:

```bash
NEXT_PUBLIC_APP_URL=http://localhost:3000
IMAGE_PROVIDER_MODE=next_image_api
IMAGE_GENERATE_ENDPOINT=http://localhost:3000/api/image/generate
```

## Video provider runtime

```bash
VIDEO_RENDER_MODE=real_provider
VIDEO_PROVIDER_DEFAULT=runway
VIDEO_PROVIDER_ALLOW_MOCK=false
PROVIDER_FACTORY_ENABLE_LEGACY_MOCK_CLIENT=false
```

## Provider keys

Tên env thực tế cần đối chiếu với adapters đã copy:

```bash
GOOGLE_VEO_API_KEY=
GOOGLE_VEO_PROJECT_ID=
RUNWAY_API_KEY=
KLING_ACCESS_KEY=
KLING_SECRET_KEY=
SEEDANCE_API_KEY=
SEEDANCE2_API_KEY=
VOLCENGINE_ACCESS_KEY_ID=
VOLCENGINE_SECRET_ACCESS_KEY=
```

## Object storage

```bash
OBJECT_STORAGE_PROVIDER=s3
S3_BUCKET=
S3_REGION=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
```

## Production hard rule

Production không được bật mock:

```bash
APP_ENV=production
VIDEO_PROVIDER_ALLOW_MOCK=false
IMAGE_GENERATION_REQUIRED=true
```
