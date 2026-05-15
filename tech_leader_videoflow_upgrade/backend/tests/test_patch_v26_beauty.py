"""
Test V26 Beauty Perception patches
"""
import io
from pathlib import Path
from PIL import Image

# Mock the router since we can't run async tests directly
def test_v26_beauty_basic():
    """Test V26 beauty patch basic functionality"""
    
    # Create a test image
    img = Image.new("RGB", (100, 100), color="pink")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    
    # Import and test core logic
    from app.creative_infra_mvp.api.beauty_patches import (
        _analyze_skin_tone,
        _analyze_face,
        _contour_highlight_analysis,
        _semantic_makeup_transfer,
        _beauty_perception_scoring
    )
    
    # Test face analysis
    face_geom = _analyze_face(img)
    assert "face_width" in face_geom
    assert "symmetry_score" in face_geom
    
    # Test skin tone analysis
    skin_tone = _analyze_skin_tone(img)
    assert "tone" in skin_tone
    assert "undertone" in skin_tone
    assert "saturation" in skin_tone
    assert "brightness" in skin_tone
    assert isinstance(skin_tone["brightness"], float)
    
    # Test contour analysis
    contour = _contour_highlight_analysis(skin_tone, face_geom)
    assert "contour_shade" in contour
    assert "blending_method" in contour
    
    # Test makeup transfer
    makeup = _semantic_makeup_transfer(skin_tone, "kol_beauty", "soft_glam")
    assert "eye_makeup" in makeup
    assert "lip_makeup" in makeup
    assert "identity_preservation" in makeup
    
    # Test beauty perception
    perception = _beauty_perception_scoring(skin_tone, face_geom)
    assert "perceived_luminosity" in perception
    assert "overall_beauty_score" in perception
    assert 0 <= perception["overall_beauty_score"] <= 1
    
    print("✓ V26 beauty analysis test passed")
    print(f"  Skin tone: {skin_tone['tone']}, undertone: {skin_tone['undertone']}")
    print(f"  Beauty score: {perception['overall_beauty_score']:.2f}")

def test_v26_routes_defined():
    """Test that all required routes are registered"""
    from app.creative_infra_mvp.api.beauty_patches import router
    
    routes = [route.path for route in router.routes]
    
    # All endpoints should be defined (with full prefix path)
    assert "/api/v1/beauty/analyze" in routes, "Missing /analyze endpoint"
    assert "/api/v1/beauty/transfer" in routes, "Missing /transfer endpoint"
    assert "/api/v1/beauty/contour" in routes, "Missing /contour endpoint"
    assert "/api/v1/beauty/skin-tone" in routes, "Missing /skin-tone endpoint"
    assert "/api/v1/beauty/perception" in routes, "Missing /perception endpoint"
    assert "/api/v1/beauty/graph" in routes, "Missing /graph endpoint"
    assert "/api/v1/beauty/memory/{brand_name}" in routes, "Missing /memory endpoint"
    assert "/api/v1/beauty/metrics" in routes, "Missing /metrics endpoint"
    
    print(f"✓ All {len([r for r in routes if r.startswith('/')])} beauty endpoints registered")

if __name__ == "__main__":
    test_v26_beauty_basic()
    test_v26_routes_defined()
    print("\n✓ V26 Beauty Perception tests completed successfully")
