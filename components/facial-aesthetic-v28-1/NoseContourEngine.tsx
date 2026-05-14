export default function NoseContourEngine({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Nose Structure + Contour Reasoning</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">
        {result ? JSON.stringify({
          nose_structure: result.nose_structure,
          contour_highlight: result.contour_highlight
        }, null, 2) : "Sống mũi, contour và highlight sẽ hiển thị tại đây."}
      </pre>
    </div>
  );
}
