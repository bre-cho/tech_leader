export type Goal = "sale" | "brand" | "conversion" | "trust" | "viral" | "lookbook";

export type Mechanism =
  | "ingredient"
  | "offer"
  | "emotion"
  | "energy"
  | "feature"
  | "lifestyle"
  | "luxury"
  | "lookbook";

export type VariantName = "trust" | "viral" | "conversion";

export type PosterInput = {
  industry: string;
  productName: string;
  productType?: string;
  description?: string;
  goal?: Goal;
  mood?: string;
  target?: string;
  ingredients?: string[];
  headline?: string;
  subline1?: string;
  subline2?: string;
  price?: string;
  hasModel?: boolean;
  hasPackaging?: boolean;
  hasCollection?: boolean;
  useReferenceImage?: boolean;
};

export type MechanismResult = {
  primary: Mechanism;
  secondary: Mechanism | null;
  scores: Record<Mechanism, number>;
};

export type VariantScores = {
  ctr: number;
  attention: number;
  trust: number;
  finalScore: number;
};

export type VisualVariant = {
  variant: VariantName;
  type?: VariantName;
  label: string;
  sellingMechanism: MechanismResult;
  layout: string;
  visualDirection: string;
  headlineStyle: string;
  prompt: string;
  negativePrompt: string;
  scores: VariantScores;
};

export type PosterResponse = {
  input: PosterInput;
  mechanism: MechanismResult;
  variants: VisualVariant[];
  winner: VisualVariant;
  render: {
    /** "provider_ready" signals the prompt contract is fully compiled and ready
     *  for a render provider (Adobe Firefly, Canva, etc.) to consume.
     *  No provider has been invoked yet by this engine layer. */
    mode: "provider_ready";
    status: "ready_for_provider";
    message: string;
    imageUrl?: string;
  };
};
