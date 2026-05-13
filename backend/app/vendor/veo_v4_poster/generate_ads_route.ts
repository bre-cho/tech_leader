import { NextRequest, NextResponse } from 'next/server';
import { runAdsFactoryV6Pro } from '@/lib/v6-pro/runtime';

/**
 * Generate ad variants using the V6Pro engine.
 * This endpoint replaces the legacy V5 /api/generate-ads endpoint.
 */
export async function POST(req: NextRequest) {
  try {
    const input = await req.json();
    if (!input?.product && !input?.product_type) {
      return NextResponse.json({ error: 'Missing product or product_type' }, { status: 400 });
    }
    const result = await runAdsFactoryV6Pro({
      product_type: input.product_type || input.product,
      goal: input.goal || 'conversion',
      brand: input.brand || input.brand_name,
      ratio: input.ratio || '4:5',
    });
    return NextResponse.json({
      engine_version: 'v6pro',
      industry: result.industry,
      winner: result.winner,
      variants: Object.values(result.scored_variants),
    });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to generate ads' }, { status: 500 });
  }
}
