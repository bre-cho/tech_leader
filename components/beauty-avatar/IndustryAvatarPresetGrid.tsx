const presets = [
  "personal_beauty", "kol_beauty", "studio_makeup", "wedding_studio", "spa",
  "fashion_brand", "cosmetic_brand", "beauty_clinic", "tiktok_creator"
];

export default function IndustryAvatarPresetGrid() {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Industry Avatar Presets</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4">
        {presets.map((p) => <div key={p} className="rounded-2xl border border-neutral-700 p-3 text-sm">{p}</div>)}
      </div>
    </div>
  );
}
