import { OpenRouterStore } from "./openRouterStore";

export async function openRouterChat(messages: Array<{ role: string; content: string }>) {
  const auth = new OpenRouterStore().getAuth();
  const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...auth.headers
    },
    body: JSON.stringify({
      model: auth.model,
      messages
    })
  });
  if (!res.ok) {
    throw new Error(`OpenRouter request failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}
