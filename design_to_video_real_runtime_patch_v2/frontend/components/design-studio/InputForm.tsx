"use client";

import type { FormState } from "./types";

type Props = {
  form: FormState;
  onChange: (next: FormState) => void;
  onGenerate: () => void;
};

export function InputForm({ form, onChange, onGenerate }: Props) {
  return (
    <div className="grid md:grid-cols-4 gap-3 rounded-2xl bg-neutral-900 p-6">
      {Object.entries(form).map(([key, value]) => (
        <label key={key} className="space-y-2 text-sm text-neutral-300">
          {key}
          <input
            className="w-full rounded-xl bg-neutral-800 p-3 text-white"
            value={value}
            onChange={(e) => onChange({ ...form, [key]: e.target.value })}
          />
        </label>
      ))}
      <button
        onClick={onGenerate}
        className="md:col-span-4 rounded-xl bg-yellow-400 px-4 py-3 font-semibold text-black"
      >
        Generate Image Concepts
      </button>
    </div>
  );
}
