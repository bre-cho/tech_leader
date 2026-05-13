import { GoogleAccountStore } from "../services/accounts/googleAccountStore";
import { OpenRouterStore } from "../services/settings/openRouterStore";

process.env.APP_SECRET = "test-secret";

const google = new GoogleAccountStore();
const acc = google.add({
  label: "Test Google",
  apiKey: "AIzaSyDummyTestKey123456789",
  enabled: true,
  capabilities: ["nano_banana", "veo_3_1"],
  quotaWeight: 1
});
if (!acc.maskedApiKey.includes("...")) throw new Error("Google key masking failed");

const selected = google.select("nano_banana", 0);
if (selected.accountId !== acc.id) throw new Error("Google account selection failed");

const openrouter = new OpenRouterStore();
const pub = openrouter.update({
  enabled: true,
  apiKey: "sk-or-v1-dummykey1234567890",
  selectedModel: "openai/gpt-4o-mini",
  siteUrl: "https://example.com",
  appTitle: "AI Creative OS"
});
if (!pub.maskedApiKey?.includes("...")) throw new Error("OpenRouter key masking failed");

const auth = openrouter.getAuth();
if (!auth.headers.Authorization.startsWith("Bearer ")) throw new Error("OpenRouter bearer auth failed");

console.log("Accounts + OpenRouter settings test passed");
