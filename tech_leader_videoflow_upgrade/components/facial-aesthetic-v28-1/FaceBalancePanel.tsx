export default function FaceBalancePanel({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Facial Balance Engine</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">
        {result ? JSON.stringify(result.facial_balance, null, 2) : "Chưa chạy phân tích."}
      </pre>
    </div>
  );
}
