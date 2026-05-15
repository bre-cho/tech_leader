export default function BeautyKOLPersonaPanel({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Beauty KOL Persona</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">{result ? JSON.stringify(result.persona_profile, null, 2) : "Persona sẽ hiển thị sau khi tạo avatar."}</pre>
    </div>
  );
}
