from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get('/api/v1/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'

def test_operating_law_endpoint():
    res = client.get('/api/v1/governance/operating-law')
    assert res.status_code == 200
    body = res.json()
    assert 'Workflow' in body['law']
    assert 'verify' in body['required_steps']


def test_design_studio_full_runtime():
    payload = {
        'industry': 'spa mỹ phẩm',
        'product': 'serum phục hồi da',
        'audience': 'phụ nữ 25-35',
        'channel': 'TikTok',
        'goal': 'bán hàng',
        'brand_name': 'Lumi Skin',
    }
    res = client.post('/api/v1/design-studio/run', json=payload)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body['promotion_mode'] == 'REAL'
    assert body['promotion_gate']['status'] == 'PASSED'
    assert body['law_trace']['verify'] is True
    assert len(body['image_concepts']) >= 3
    assert len(body['storyboard']) >= 5
    assert body['best_concept']['score']['video_upsell_ready'] is True


def test_design_studio_dry_run_skips_persistence():
    memory_before = client.get('/api/v1/memory/winner-dna')
    assert memory_before.status_code == 200
    entities_before = client.get('/api/v1/context-graph/entities')
    assert entities_before.status_code == 200

    payload = {
        'industry': 'spa mỹ phẩm',
        'product': 'serum phục hồi da',
        'audience': 'phụ nữ 25-35',
        'channel': 'TikTok',
        'goal': 'bán hàng',
        'brand_name': 'Lumi Skin',
        'dry_run': True,
    }
    res = client.post('/api/v1/design-studio/run', json=payload)
    assert res.status_code == 200, res.text
    body = res.json()

    assert body['dry_run'] is True
    assert body['promotion_mode'] == 'DRY_RUN'
    assert body['verification']['passed'] is True
    assert body['law_trace']['verify'] is True
    assert body['law_trace']['memory_update'] is True
    assert body['promotion_gate']['status'] == 'DRY_RUN'
    assert body['promotion_gate']['promotable'] is False
    assert body['promotion_gate']['passed'] is False
    assert body['context_graph_update']['written'] is False
    assert body['memory_update']['skipped'] is True

    memory_after = client.get('/api/v1/memory/winner-dna')
    assert memory_after.status_code == 200
    entities_after = client.get('/api/v1/context-graph/entities')
    assert entities_after.status_code == 200

    assert len(memory_after.json()['items']) == len(memory_before.json()['items'])
    assert len(entities_after.json()['items']) == len(entities_before.json()['items'])
