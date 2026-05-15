export type V6Goal = "sale" | "lead" | "click" | "brand" | "education" | "event";

export type SellingMechanism =
  | "product"
  | "emotion"
  | "problem"
  | "result"
  | "authority"
  | "offer"
  | "education"
  | "event";

export type V6Input = {
  text: string;
  product?: string;
  industry?: string;
  audience?: string;
  goal?: V6Goal;
  mood?: "luxury" | "bold" | "minimal" | "trust" | "viral";
  hasPackaging?: boolean;
  hasCollection?: boolean;
};

export type V6FunnelResult = {
  landing: {
    heroHeadline: string;
    subHeadline: string;
    cta: string;
  };
  sections: string[];
  thankYou: string;
  email: {
    subject: string;
    body: string;
  };
};

export type V6AdsPlanResult = {
  objective: string;
  angles: string[];
  captions: string[];
  ctas: string[];
  budgetTest: string;
  kpi: string[];
};

export type V6KpiRules = {
  ctrLow: string;
  cplHigh: string;
  roasHigh: string;
};

export type V6Output = {
  mechanism: SellingMechanism;
  hook: string;
  cta: string;
  layout: string;
  visual: string;
  posterPrompts: {
    trust: string;
    viral: string;
    conversion: string;
  };
  funnel: V6FunnelResult;
  botFlow: string[];
  adsPlan: V6AdsPlanResult;
  kpiRules: V6KpiRules;
};
