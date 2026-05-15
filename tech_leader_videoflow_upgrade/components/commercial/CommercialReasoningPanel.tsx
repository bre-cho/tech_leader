export function CommercialReasoningPanel({result}:{result:any}){
  return <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <section className="rounded-2xl bg-neutral-900 p-5"><h2 className="text-xl font-bold">Attention Route</h2><ol className="mt-3 space-y-2">{result.attention_route.map((z:any)=><li key={z.name} className="p-3 rounded-xl bg-neutral-800"><b>{z.priority}. {z.name}</b><p className="text-sm text-neutral-400">{z.role} — {z.suggested_position}</p></li>)}</ol></section>
    <section className="rounded-2xl bg-neutral-900 p-5"><h2 className="text-xl font-bold">Scores</h2><div className="grid grid-cols-2 gap-2 mt-3">{Object.entries(result.scores).map(([k,v]:any)=><div key={k} className="rounded-xl bg-neutral-800 p-3"><p className="text-xs text-neutral-400">{k}</p><p className="text-2xl font-bold">{v}</p></div>)}</div></section>
    <section className="rounded-2xl bg-neutral-900 p-5 lg:col-span-2"><h2 className="text-xl font-bold">Compiled HiDream / Premium Render Prompt</h2><pre className="whitespace-pre-wrap text-sm text-neutral-300 mt-3">{result.prompt}</pre></section>
  </div>
}
