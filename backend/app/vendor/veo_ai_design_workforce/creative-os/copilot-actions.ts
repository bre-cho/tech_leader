import type { CreativeOSActionMode, CreativeOSRequest, CreativeStudioBrief } from "@/lib/creative-os/types";

export type CreativeCopilotCommand = {
  mode: CreativeOSActionMode;
  label: string;
  description: string;
  userPrompt: string;
};

export const CREATIVE_COPILOT_COMMANDS: CreativeCopilotCommand[] = [
  {
    mode: "run_full_pipeline",
    label: "Chạy full Creative OS",
    description: "Đi từ brief → perception → CIG → variants → QA → render contract.",
    userPrompt: "Chạy toàn bộ pipeline và chọn poster winner."
  },
  {
    mode: "improve_luxury",
    label: "Làm luxury hơn",
    description: "Tăng cảm giác cao cấp bằng whitespace, serif, ánh sáng điện ảnh, product isolation.",
    userPrompt: "Làm poster này luxury hơn nhưng vẫn rõ sản phẩm."
  },
  {
    mode: "increase_trust",
    label: "Tăng trust",
    description: "Tăng tín hiệu tin cậy: proof, clarity, expert cue, hierarchy sạch.",
    userPrompt: "Tăng cảm giác tin cậy và chuyên nghiệp."
  },
  {
    mode: "increase_product_dominance",
    label: "Tăng product dominance",
    description: "Đưa sản phẩm thành điểm nhìn đầu tiên và giảm nhiễu visual.",
    userPrompt: "Tăng độ nổi bật của sản phẩm, giảm text phụ."
  },
  {
    mode: "fix_typography",
    label: "Sửa typography",
    description: "Tối ưu headline, CTA gravity, hierarchy và spacing.",
    userPrompt: "Sửa typography để dễ đọc và premium hơn."
  },
  {
    mode: "fix_qa",
    label: "Auto-fix QA",
    description: "Chạy hardlock QA và tạo kế hoạch sửa lỗi trước khi render.",
    userPrompt: "Kiểm tra QA và tự sửa các lỗi hardlock."
  },
  {
    mode: "explain_graph",
    label: "Giải thích CIG",
    description: "Giải thích vì sao từng node creative tạo ra perception/attention/trust.",
    userPrompt: "Giải thích Creative Intelligence Graph của poster này."
  },
  {
    mode: "save_winner",
    label: "Lưu winner DNA",
    description: "Chuẩn bị dữ liệu Brand Memory cho campaign winner.",
    userPrompt: "Lưu creative DNA của biến thể thắng."
  }
];

export function buildCreativeOSPayload(
  mode: CreativeOSActionMode,
  brief: CreativeStudioBrief,
  instruction?: string,
  currentState?: Record<string, unknown>
): CreativeOSRequest {
  return {
    mode,
    instruction,
    brief,
    currentState
  };
}

export async function callCreativeOS(payload: CreativeOSRequest) {
  const response = await fetch("/api/creative-os/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error || "Creative OS action failed");
  }
  return data;
}
