from app.commercial_intelligence.models import CommercialInput
from app.commercial_intelligence.orchestrator import CommercialVisualReasoningOrchestrator

def test_fmcg_attention_reasoning_passes():
    req = CommercialInput(
        brand_name='IceFresh', product_name='Cooling Shampoo', category='sports_grooming', audience='young active men',
        business_goal='conversion', product_benefits=['cooling freshness','anti-dandruff confidence','clean scalp'],
        export_targets=['billboard','tiktok'], product_materials=['plastic','liquid'], sensory_effect='cooling airflow', price_tier='premium'
    )
    res = CommercialVisualReasoningOrchestrator().run(req)
    assert res.attention_route[0].name == 'headline'
    assert 'environment reacts to cooling' in res.prompt
    assert res.scores['final_commercial_score'] >= 70
    assert res.qa['promotion_status'] in {'APPROVED','NEEDS_REVISION'}
    assert res.winner_dna['category'] == 'sports_grooming'

def test_beauty_prompt_contains_skin_and_product_logic():
    req = CommercialInput(
        brand_name='Lumi', product_name='Gold Serum', category='beauty', audience='premium skincare buyers',
        business_goal='conversion', product_benefits=['glowing skin','hydration','premium texture'],
        export_targets=['social','print'], product_materials=['glass','liquid'], price_tier='luxury'
    )
    res = CommercialVisualReasoningOrchestrator().run(req)
    assert 'skin' in res.prompt.lower()
    assert 'glass' in res.prompt.lower()
    assert res.typography['headline_style'] in {'elegant high-contrast serif','ultra-bold condensed sans-serif','bold clean sans-serif'}
