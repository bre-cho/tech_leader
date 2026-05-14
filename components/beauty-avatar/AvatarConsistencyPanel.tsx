export default function AvatarConsistencyPanel({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Consistency QA</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">{result ? JSON.stringify({
        passed: result.consistency?.passed,
        identity_score: result.consistency?.identity_score,
        pose_consistency: result.consistency?.pose_consistency,
        skin_consistency: result.consistency?.skin_consistency
      }, null, 2) : "Consistency metrics sẽ kiểm tra sau khi tạo avatar."}</pre>
    </div>
  );
}
