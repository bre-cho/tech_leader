export default function AvatarRender8KPanel({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">8K Render Profile</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">{result ? JSON.stringify({
        quality: result.render_profile?.quality,
        prompt: result.render_profile?.prompt?.substring(0, 100) + "...",
        negative_prompt: result.render_profile?.negative_prompt?.substring(0, 60) + "...",
        sampler: result.render_profile?.sampler
      }, null, 2) : "Render profile sẽ được thiết lập theo industry + persona."}</pre>
    </div>
  );
}
