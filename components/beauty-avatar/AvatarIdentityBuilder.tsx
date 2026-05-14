export default function AvatarIdentityBuilder({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Avatar Identity Lock</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">{result ? JSON.stringify({
        avatar_id: result.avatar_id,
        identity_lock: result.identity_lock,
        face_profile: result.face_profile
      }, null, 2) : "Chưa có avatar."}</pre>
    </div>
  );
}
