export default function MakeupAvatarPreview({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Makeup / Style Transfer</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">{result ? JSON.stringify(result.makeup_style, null, 2) : "Makeup style sẽ được chọn theo persona + skin tone."}</pre>
    </div>
  );
}
