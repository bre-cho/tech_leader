export default function BeautyDepthPreview({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Beauty Depth Preview</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">
        {result ? JSON.stringify(result.facial_depth, null, 2) : "Facial depth / 3D beauty perception sẽ hiển thị tại đây."}
      </pre>
    </div>
  );
}
