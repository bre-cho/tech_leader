export async function handleBananaWebhook(payload: unknown) {
  // Gemini image generation is usually synchronous through generateContent.
  // This hook is reserved for Vertex/queue integrations.
  return {
    status: "accepted",
    provider: "google-banana",
    received: payload
  };
}
