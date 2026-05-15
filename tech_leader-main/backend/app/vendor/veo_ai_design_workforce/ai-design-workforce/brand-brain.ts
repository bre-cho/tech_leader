import type { AIEmployee, BrandBrainOutput, ContextEntity, ContextRelation, DesignBusinessInput, WorkflowStep } from "./types";

const slug = (value: string) =>
  value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "") || "ai-design-brand";

export function buildDesignContextGraph(input: DesignBusinessInput) {
  const brand = slug(input.brandName || input.founderName || "AI Design Workforce OS");
  const entities: ContextEntity[] = [
    {
      id: `${brand}:brand`,
      type: "brand",
      name: input.brandName || "AI Design Workforce OS",
      summary: `Thương hiệu cá nhân giúp ${input.targetAudience} dùng AI để tạo thiết kế bán hàng, không chỉ ảnh đẹp.`,
      metadata: { founder: input.founderName || "Founder", promise: input.corePromise, platform: input.primaryPlatform }
    },
    {
      id: `${brand}:audience`,
      type: "audience",
      name: input.targetAudience,
      summary: `Nhóm khách hàng cần thiết kế nhanh, đẹp, có khả năng chuyển đổi và dễ triển khai bằng AI.`,
      metadata: { pain: "thiếu thời gian, thiếu đội thiết kế, thiếu hệ thống ra poster đều", buyingIntent: "cao" }
    },
    {
      id: `${brand}:style`,
      type: "style",
      name: input.visualStyle || "Luxury / Editorial / Conversion-first",
      summary: "Style DNA dùng để giữ nhất quán poster, banner, thumbnail và landing visual.",
      metadata: { designRule: "product-first, readable typography, strong focal point, trust cues" }
    },
    {
      id: `${brand}:offer`,
      type: "offer",
      name: input.currentOffer || `AI ${input.productCategory} Design System`,
      summary: `Offer giúp khách hàng đạt lời hứa: ${input.corePromise}.`,
      metadata: { pricePoint: input.pricePoint || "low-ticket → high-ticket ladder", category: input.productCategory }
    },
    {
      id: `${brand}:metric`,
      type: "metric",
      name: "Revenue Intelligence",
      summary: "Theo dõi hook, poster, content, lead magnet, offer và doanh thu để clone winner.",
      metadata: { target: input.monthlyRevenueGoal || "tăng trưởng doanh thu đều", loop: "data → memory → clone winner" }
    }
  ];
  const relations: ContextRelation[] = [
    { from: entities[0].id, to: entities[1].id, relation: "serves", weight: 0.96 },
    { from: entities[0].id, to: entities[2].id, relation: "uses_style_dna", weight: 0.91 },
    { from: entities[2].id, to: entities[3].id, relation: "increases_perceived_value", weight: 0.88 },
    { from: entities[3].id, to: entities[4].id, relation: "measured_by", weight: 0.94 },
    { from: entities[4].id, to: entities[2].id, relation: "updates_winner_memory", weight: 0.9 }
  ];
  return { entities, relations };
}

export function createDesignEmployees(): AIEmployee[] {
  return [
    {
      id: "brand-strategy-agent",
      name: "Brand Strategy Agent",
      department: "Strategy",
      mission: "Định vị thương hiệu cá nhân, lời hứa thị trường, content pillars và product ladder.",
      kpi: "Brand clarity score ≥ 90",
      tools: ["Audience Map", "Positioning Canvas", "Offer Ladder"],
      outputs: ["Brand DNA", "One-liner", "Content pillars", "Offer ladder"]
    },
    {
      id: "design-research-agent",
      name: "Design Research Agent",
      department: "Market Intelligence",
      mission: "Quét trend thiết kế AI, đối thủ, visual angle và nhu cầu chủ shop/creator/marketer.",
      kpi: "Trend-to-content fit ≥ 85",
      tools: ["Trend Scan", "Competitor Swipe", "Visual Gap Map"],
      outputs: ["Trend report", "Visual angle", "Reference direction"]
    },
    {
      id: "poster-director-agent",
      name: "Poster Director Agent",
      department: "Creative Production",
      mission: "Biến sản phẩm thành poster/banner/thumbnail có focal point, bố cục, ánh sáng và CTA rõ.",
      kpi: "Poster score ≥ 88",
      tools: ["V4 Poster Engine", "Prompt V6", "Poster Intelligence Rules"],
      outputs: ["Poster concept", "Image prompt", "Layout brief"]
    },
    {
      id: "content-agent",
      name: "Content Agent",
      department: "Growth Content",
      mission: "Tạo video script, carousel, caption và email kéo khách từ nội dung vào offer.",
      kpi: "Hook score ≥ 90; CTA clarity ≥ 85",
      tools: ["Short Script", "Carousel Writer", "Caption Engine"],
      outputs: ["Short video script", "Caption", "Carousel", "Email nurture"]
    },
    {
      id: "offer-agent",
      name: "Offer Agent",
      department: "Revenue",
      mission: "Đóng gói prompt pack, template pack, khóa học, dịch vụ setup và membership.",
      kpi: "Offer clarity ≥ 90; value stack ≥ 85",
      tools: ["Product Ladder", "Pricing Map", "Bonus Stack"],
      outputs: ["Offer page", "Product pack", "Checkout brief"]
    },
    {
      id: "analytics-agent",
      name: "Analytics Agent",
      department: "Revenue Intelligence",
      mission: "Đọc dữ liệu content, lead, conversion, revenue; đề xuất clone/kill/improve.",
      kpi: "Every campaign has decision: clone, improve, or kill",
      tools: ["Winner DNA", "Self-learning AI", "Scale Intelligence"],
      outputs: ["Performance report", "Winner memory", "Next experiment"]
    }
  ];
}

export function buildWorkflows(input: DesignBusinessInput): BrandBrainOutput["workflows"] {
  const contentSteps: WorkflowStep[] = [
    { id: "scan", name: "Trend Scan", ownerAgent: "design-research-agent", input: input.niche, output: "3 trend angles", qualityGate: "Có pain + proof + visual novelty" },
    { id: "poster", name: "Poster Demo", ownerAgent: "poster-director-agent", input: "winning angle", output: "poster prompt + layout brief", qualityGate: "Product focus ≥ 85, readability ≥ 85" },
    { id: "script", name: "Short Video Script", ownerAgent: "content-agent", input: "poster demo", output: "30–45s script", qualityGate: "Hook ≤ 3s, CTA rõ" },
    { id: "lead", name: "Lead Magnet", ownerAgent: "offer-agent", input: "content topic", output: "free checklist/prompt pack", qualityGate: "Immediate value, low friction" },
    { id: "measure", name: "Analytics Decision", ownerAgent: "analytics-agent", input: "views/clicks/leads/sales", output: "clone/improve/kill", qualityGate: "Có quyết định tiếp theo", automationHook: "Update Winner DNA" }
  ];
  const revenueSteps: WorkflowStep[] = [
    { id: "package", name: "Package Digital Product", ownerAgent: "offer-agent", input: "winner style + audience pain", output: "prompt/template pack", qualityGate: "Có outcome rõ và demo trước/sau" },
    { id: "landing", name: "Landing Offer Brief", ownerAgent: "content-agent", input: "product pack", output: "landing copy + FAQ + CTA", qualityGate: "Promise-proof-price match" },
    { id: "nurture", name: "Nurture Sequence", ownerAgent: "content-agent", input: "lead list", output: "5-email sequence", qualityGate: "Không hard sell sớm" },
    { id: "scale", name: "Clone Winner", ownerAgent: "analytics-agent", input: "sales data", output: "next product/angle", qualityGate: "ROAS/Conversion signal đủ" }
  ];
  return [
    { id: "daily-content-to-lead", name: "Daily Content → Lead Workflow", goal: "Biến năng lực thiết kế AI thành lead hằng ngày", steps: contentSteps },
    { id: "winner-to-product", name: "Winner → Digital Product Workflow", goal: "Biến poster/content thắng thành sản phẩm số có thể bán", steps: revenueSteps }
  ];
}

export function runBrandBrain(input: DesignBusinessInput): BrandBrainOutput {
  const brand = input.brandName || "AI Design Workforce OS";
  return {
    positioning: `${brand} là hệ thống giúp ${input.targetAudience} dùng AI để tạo thiết kế quảng cáo có khả năng bán hàng, xây content chứng minh năng lực và đóng gói thành sản phẩm số/doanh thu tự động.`,
    oneLiner: `Từ một founder tự làm thiết kế → thành AI Design Workforce tạo poster, content, offer và revenue loop mỗi ngày.`,
    contentPillars: [
      "Before/After: từ ảnh thường thành poster bán hàng",
      "Prompt Breakdown: giải phẫu prompt thiết kế AI",
      "AI Design Workflow: cách sản xuất 10–30 visual/ngày",
      "Case Study: clone winner từ poster/content có tín hiệu tốt",
      "Productized Design: biến template/prompt thành sản phẩm số"
    ],
    productLadder: [
      { stage: "free", product: "AI Poster Starter Kit", promise: "Tạo poster đầu tiên trong 10 phút", priceHint: "Free lead magnet" },
      { stage: "low_ticket", product: "Prompt Pack theo ngành", promise: "Có ngay 50–100 prompt dùng được", priceHint: "99k–499k" },
      { stage: "mid_ticket", product: "Khóa học AI Design System", promise: "Tự xây hệ thiết kế AI cho shop/creator", priceHint: "1.5tr–5tr" },
      { stage: "high_ticket", product: "Setup AI Design Workforce cho doanh nghiệp", promise: "Cài hệ sản xuất poster/banner/thumbnail nội bộ", priceHint: "15tr–100tr+" },
      { stage: "recurring", product: "AI Design Membership", promise: "Prompt/template/workshop cập nhật hằng tháng", priceHint: "199k–999k/tháng" }
    ],
    aiEmployees: createDesignEmployees(),
    contextGraph: buildDesignContextGraph(input),
    workflows: buildWorkflows(input),
    launchPlan7Days: [
      { day: 1, action: "Chốt Brand DNA + 5 content pillars", artifact: "Brand DNA page", successMetric: "Thông điệp rõ trong 1 câu" },
      { day: 2, action: "Tạo 3 poster demo theo 3 ngành", artifact: "Poster prompt + demo layout", successMetric: "Poster score ≥ 85" },
      { day: 3, action: "Quay/viết 3 short video giải phẫu poster", artifact: "Short scripts", successMetric: "Hook score ≥ 90" },
      { day: 4, action: "Tạo lead magnet 20 prompt miễn phí", artifact: "PDF/Notion lead magnet", successMetric: "CTA click ≥ 3%" },
      { day: 5, action: "Đóng gói low-ticket prompt pack", artifact: "Product pack + checkout brief", successMetric: "Offer clarity ≥ 90" },
      { day: 6, action: "Tạo landing page + email nurture", artifact: "Landing + 5 emails", successMetric: "Lead-to-offer flow hoàn chỉnh" },
      { day: 7, action: "Đọc số liệu và clone winner", artifact: "Winner DNA record", successMetric: "Có quyết định clone/improve/kill" }
    ],
    revenueLoop: [
      "Trend → Poster demo → Content proof → Lead magnet",
      "Lead magnet → Email nurture → Prompt/template pack",
      "Customer result → Case study → High-ticket setup",
      "Performance data → Winner DNA → Clone content/product"
    ],
    qualityGates: [
      "NO BRAND DNA → NO CONTENT",
      "NO PRODUCT FOCUS → NO POSTER",
      "NO LEAD MAGNET → NO SCALE CONTENT",
      "NO REVENUE SIGNAL → NO CLONE",
      "NO WINNER MEMORY → NO NEXT PRODUCT"
    ]
  };
}

export const defaultDesignBusinessInput: DesignBusinessInput = {
  founderName: "TungNS",
  brandName: "AI Design Workforce OS",
  niche: "thiết kế AI cho poster/banner/thumbnail quảng cáo",
  targetAudience: "chủ shop, creator, marketer và SME không có đội thiết kế mạnh",
  corePromise: "tạo visual quảng cáo chuẩn agency bằng AI, nhanh hơn và có khả năng chuyển đổi tốt hơn",
  productCategory: "poster, banner, thumbnail, landing visual, prompt/template pack",
  primaryPlatform: "TikTok",
  visualStyle: "Luxury editorial, product-first, high-conversion advertising",
  currentOffer: "AI Poster Prompt & Template Pack",
  pricePoint: "low-ticket → course → high-ticket setup",
  monthlyRevenueGoal: "tăng trưởng từ sản phẩm số + dịch vụ setup"
};
