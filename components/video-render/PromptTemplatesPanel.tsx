"use client";

const PROMPT_TEMPLATES = [
  {
    name: "Fashion Runway",
    text: "Professional fashion runway model walking down a luxurious catwalk, dramatic lighting with gold accents, slow zoom-in on face, confident expression, high-end editorial mood, 4K cinematic"
  },
  {
    name: "Product Hero Shot",
    text: "Beauty product centered in frame, soft backlit glow, hands gently rotating the bottle, warm golden lighting, premium macro focus, minimalist luxury background, cinematic depth"
  },
  {
    name: "Lifestyle Social",
    text: "Young woman enjoying product in natural daylight, candid authentic moment, soft motion, warm earthy tones, relatable expression, social media friendly, TikTok/Reels ready"
  },
  {
    name: "Commercial Reveal",
    text: "Dynamic product reveal with fast camera push-in, dramatic lighting sweep, high energy motion, bold contrast, on-brand colors, call-to-action moment, commercial spot ready"
  }
];

export default function PromptTemplatesPanel() {
  function handleTemplateClick(text: string) {
    const textArea = document.getElementById("prompt-textarea") as HTMLTextAreaElement | null;
    if (textArea) {
      textArea.value = text;
      textArea.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  return (
    <div style={{ display: "grid", gap: "0.75rem" }}>
      {PROMPT_TEMPLATES.map((t, i) => (
        <div
          key={i}
          style={{
            background: "#111",
            border: "1px solid #222",
            borderRadius: "0.5rem",
            padding: "0.75rem 1rem",
            cursor: "pointer",
            transition: "all .15s",
          }}
          onClick={() => handleTemplateClick(t.text)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              handleTemplateClick(t.text);
            }
          }}
          role="button"
          tabIndex={0}
        >
          <p style={{ margin: "0 0 0.3rem 0", color: "#d4a843", fontSize: "0.85rem", fontWeight: 600 }}>
            {t.name}
          </p>
          <p style={{ margin: 0, color: "#666", fontSize: "0.8rem", lineHeight: 1.4 }}>
            {t.text.substring(0, 80)}...
          </p>
        </div>
      ))}
    </div>
  );
}

