from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import apps.api.main as main_module
import apps.worker.celery_app as worker_module
from apps.api.core.config import settings
from apps.api.db.session import Base, get_db
import packages.campaign_intelligence.engines as engines_module


def test_creative_intelligence_flow(monkeypatch, tmp_path: Path):
    settings.app_env = "local"
    settings.auth_jwt_secret = "creative-secret"
    settings.auth_jwt_algorithm = "HS256"
    settings.dev_internal_token_secret = "creative-dev-secret"

    db_path = tmp_path / "creative_intelligence.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    def immediate_delay(job_id: str, prompt: str, provider: str):
        return worker_module.render_creative_job(job_id, prompt, provider)

    class FakeAdobeRenderProvider:
        def generate(self, prompt: str, context: dict | None = None) -> dict:
            return {
                "artifact_id": "adobe_asset_real",
                "artifact_type": "image",
                "mime_type": "image/png",
                "url": "https://img.adobe.test/render.png",
                "provider_used": "adobe",
                "prompt_used": prompt,
                "adobe_asset_id": "adobe_asset_real",
                "metadata": {"brand": (context or {}).get("brand")},
            }

    class FakeCanvaRenderProvider:
        def generate(self, prompt: str, context: dict | None = None) -> dict:
            return {
                "artifact_id": "canva_design_real",
                "artifact_type": "layout",
                "mime_type": "image/png",
                "url": "https://cdn.canva.test/export.png",
                "provider_used": "canva",
                "prompt_used": prompt,
                "canva_design_id": "canva_design_real",
                "metadata": {"template_id": (context or {}).get("template_id")},
            }

    monkeypatch.setattr(main_module, "_run_migrations", lambda: None)
    monkeypatch.setattr(worker_module, "SessionLocal", testing_session_local)
    monkeypatch.setattr(main_module.render_creative_job, "delay", immediate_delay)
    monkeypatch.setattr(engines_module, "AdobeRenderProvider", FakeAdobeRenderProvider)
    monkeypatch.setattr(engines_module, "CanvaRenderProvider", FakeCanvaRenderProvider)

    main_module.app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(main_module.app) as client:
            token_res = client.post(
                "/internal/dev/token",
                json={"user_id": "creative-user", "email": "creative@example.com", "expires_in_seconds": 1800},
                headers={"x-dev-internal-secret": settings.dev_internal_token_secret},
            )
            assert token_res.status_code == 200
            access_token = token_res.json()["access_token"]
            auth_headers = {"Authorization": f"Bearer {access_token}"}

            brand_res = client.post(
                "/api/v1/brands",
                json={"name": "Creative Brand", "industry": "beauty"},
                headers=auth_headers,
            )
            assert brand_res.status_code == 200
            brand_id = brand_res.json()["id"]

            session_res = client.post(
                "/api/v1/creative/sessions",
                json={
                    "brand_id": brand_id,
                    "industry": "beauty",
                    "product": "Glass Skin Serum",
                    "goal": "premium_conversion",
                    "platform": "instagram",
                    "audience": "women 22-35",
                    "perception_targets": ["luxury", "trust"],
                    "assets": [{"template_id": "tpl_123"}],
                },
                headers=auth_headers,
            )
            assert session_res.status_code == 200
            session_id = session_res.json()["id"]

            skills_res = client.get("/api/v1/skills", headers=auth_headers)
            assert skills_res.status_code == 200
            assert len(skills_res.json()["skills"]) >= 1

            design_systems_res = client.get("/api/v1/design-systems", headers=auth_headers)
            assert design_systems_res.status_code == 200
            assert len(design_systems_res.json()["design_systems"]) >= 1

            plan_res = client.post(f"/api/v1/creative/sessions/{session_id}/plan", headers=auth_headers)
            assert plan_res.status_code == 200
            plan_data = plan_res.json()
            assert plan_data["design_system"]["id"] == "luxury_editorial"

            score_res = client.post(f"/api/v1/creative/sessions/{session_id}/score", headers=auth_headers)
            assert score_res.status_code == 200
            assert score_res.json()["luxury_score"] >= 80

            put_brand_dna_res = client.put(
                f"/api/v1/creative/brand-dna/{brand_id}",
                json={"dna": {"tone": "luxury", "palette": ["black", "gold"]}},
                headers=auth_headers,
            )
            assert put_brand_dna_res.status_code == 200
            assert put_brand_dna_res.json() == {
                "brand_id": brand_id,
                "dna": {"tone": "luxury", "palette": ["black", "gold"]},
            }

            render_res = client.post(
                "/api/v1/creative/render-jobs",
                json={"session_id": session_id, "prompt": plan_data["prompt_stack"]["creative_prompt"], "provider": "adobe+canva"},
                headers=auth_headers,
            )
            assert render_res.status_code == 200
            job_id = render_res.json()["id"]
            assert render_res.json()["status"] == "queued"

            get_render_res = client.get(f"/api/v1/creative/render-jobs/{job_id}", headers=auth_headers)
            assert get_render_res.status_code == 200
            assert get_render_res.json()["status"] == "succeeded"
            assert get_render_res.json()["result"]["provider_used"] == "adobe+canva"
            assert get_render_res.json()["result"]["adobe_asset_id"] == "adobe_asset_real"
            assert get_render_res.json()["result"]["canva_design_id"] == "canva_design_real"
            assert get_render_res.json()["result"]["image_url"] == "https://img.adobe.test/render.png"
            assert get_render_res.json()["result"]["export_url"] == "https://cdn.canva.test/export.png"

            brand_dna_res = client.get(f"/api/v1/creative/brand-dna/{brand_id}", headers=auth_headers)
            assert brand_dna_res.status_code == 200
            assert brand_dna_res.json() == {
                "brand_id": brand_id,
                "dna": {"tone": "luxury", "palette": ["black", "gold"]},
            }
    finally:
        main_module.app.dependency_overrides.clear()