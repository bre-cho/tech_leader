import { randomUUID } from "node:crypto";
import type { CreativeIntelligenceGraph, CreativeStudioBrief, PerceptionNode } from "@/lib/creative-os/types";

export function buildCreativeIntelligenceGraph(
  brief: CreativeStudioBrief,
  perceptionNodes: PerceptionNode[],
  instruction = ""
): CreativeIntelligenceGraph {
  const graphId = randomUUID();
  const nodes = [
    ...perceptionNodes.map((node) => ({
      id: node.id,
      type: "perception" as const,
      label: node.label,
      meaning: node.signals.join(" + "),
      weight: node.score
    })),
    {
      id: "branding_palette",
      type: "branding" as const,
      label: "Palette as brand signal",
      meaning: "Color is treated as perception carrier, not decoration.",
      weight: 82
    },
    {
      id: "composition_dominance",
      type: "composition" as const,
      label: "Product dominance and eye flow",
      meaning: "The poster must control first fixation, product clarity, and CTA gravity.",
      weight: 88
    },
    {
      id: "typography_hierarchy",
      type: "typography" as const,
      label: "Typography hierarchy",
      meaning: "Headline acts as attention dominance node; CTA acts as conversion gravity node.",
      weight: 86
    },
    {
      id: "emotion_design",
      type: "emotion" as const,
      label: "Emotional design",
      meaning: "The visual must create desire/trust before explaining features.",
      weight: 84
    },
    {
      id: "campaign_evolution",
      type: "campaign" as const,
      label: "Campaign evolution memory",
      meaning: "Winner patterns should be saved as reusable creative DNA.",
      weight: 80
    },
    {
      id: "operator_action",
      type: "action" as const,
      label: "Creative operator command",
      meaning: instruction || "Run closed-loop poster production from intent to QA-ready render contract.",
      weight: 78
    }
  ];

  const perceptionEdges = perceptionNodes.flatMap((node) => [
    {
      from: node.id,
      to: "branding_palette",
      relation: "supports" as const,
      reason: `${node.label} determines palette, material texture, and lighting language.`
    },
    {
      from: node.id,
      to: "composition_dominance",
      relation: "amplifies" as const,
      reason: `${node.label} must be made visible through object scale, isolation, depth, and eye flow.`
    }
  ]);

  const edges = [
    ...perceptionEdges,
    {
      from: "typography_hierarchy",
      to: "composition_dominance",
      relation: "supports" as const,
      reason: "Typography must guide visual flow instead of competing with product dominance."
    },
    {
      from: "emotion_design",
      to: "typography_hierarchy",
      relation: "amplifies" as const,
      reason: "Emotional copy controls attention and trust before conversion."
    },
    {
      from: "composition_dominance",
      to: "campaign_evolution",
      relation: "evolves" as const,
      reason: "Dominance patterns are stored for future winner cloning and fatigue control."
    },
    {
      from: "operator_action",
      to: "campaign_evolution",
      relation: "supports" as const,
      reason: "Agent actions must produce inspectable state changes and learning events."
    }
  ];

  return {
    graphId,
    nodes,
    edges,
    summary: `CIG maps ${brief.productName || "the product"} from business intent into perception, typography, composition, QA, and reusable brand memory.`
  };
}
