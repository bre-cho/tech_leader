const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

type DesignStudioPayload = {
  industry: string;
  product: string;
  audience: string;
  channel: string;
  goal: string;
  brand_name: string;
  budget_tier: string;
  language: string;
};

export async function runDesignStudio(payload: DesignStudioPayload) {
  const response = await fetch(`${API_BASE_URL}/api/v1/design-studio/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Design Studio API failed with status ${response.status}`);
  }

  return response.json();
}
