'use client'

import { useMemo, useState } from 'react'
import type { MovieOSV4Response } from '@/types/movie-os-v4'

const steps = ['Prompt','Director Brief','Narrative Graph','Mood + Lens','Character Bible','Shot Plan','Emotional Graph','Scene Dependencies','Sequential Runtime','Memory Update']

const moodProfiles = {
  gothic_luxury: {
    lighting:'ruby velvet low-key cinematic lighting with gold rim highlights',
    lens:'85mm portrait lens, shallow depth of field',
    colors:['deep ruby','black velvet','antique gold','soft skin highlight'],
    textures:['velvet','ruby gemstone','black lace','polished gold'],
    transitions:['ruby glint match cut','velvet fade','shadow dissolve'],
  },
  vogue_fantasy: {
    lighting:'high-fashion editorial spotlight with glossy runway reflections',
    lens:'50mm editorial fashion lens',
    colors:['violet blue','emerald green','silver highlight','moonlit black'],
    textures:['translucent wings','crystal fabric','reflective runway','editorial haze'],
    transitions:['runway flash cut','fabric motion dissolve','spotlight wipe'],
  },
  ethereal_spiritual: {
    lighting:'golden hour backlight with glowing particle atmosphere',
    lens:'35mm natural cinematic lens',
    colors:['warm gold','soft amber','misty green','skin glow'],
    textures:['transparent fabric','hair particles','sun flare','dust glow'],
    transitions:['gold particle dissolve','sun flare wipe','breathing fade'],
  },
  cinematic_fantasy: {
    lighting:'magical volumetric cinematic light',
    lens:'35mm fantasy cinema lens',
    colors:['violet','emerald','moonlit blue','soft gold'],
    textures:['sparkles','mist','cinematic costume','glowing atmosphere'],
    transitions:['magic dissolve','soft glow wipe','motion match cut'],
  },
}

const shotTitles = ['First Frame Hook','Hero Identity Reveal','World Establishing Shot','Texture Detail Insert','Emotional Close-up','Transformation Escalation','Power Motion Scene','Emotional Peak','Final Hero Tableau']
const cameraMoves = ['slow cinematic push-in','controlled portrait glide','wide crane reveal','macro beauty detail','handheld emotional drift','orbit transformation move','dolly with fabric motion','rising hero orbit','final locked tableau']

export function AutonomousMovieOSV4() {
  const [prompt,setPrompt] = useState('dark fantasy queen cinematic trailer')
  const [duration,setDuration] = useState(60)
  const [provider,setProvider] = useState('kling')
  const [plannedBatchSize,setPlannedBatchSize] = useState(6)
  const [movie,setMovie] = useState<MovieOSV4Response | null>(null)

  const detectedMood = useMemo(() => {
    const text = prompt.toLowerCase()
    if (text.includes('gothic') || text.includes('ruby') || text.includes('queen')) return 'gothic_luxury'
    if (text.includes('vogue') || text.includes('fashion') || text.includes('couture')) return 'vogue_fantasy'
    if (text.includes('spiritual') || text.includes('ethereal') || text.includes('golden')) return 'ethereal_spiritual'
    return 'cinematic_fantasy'
  }, [prompt])

  function runAutonomousDirector() {
    const mood = moodProfiles[detectedMood as keyof typeof moodProfiles]
    const recommended = provider === 'veo' ? 8 : provider === 'seedance' ? 6 : 5
    const sceneCount = Math.max(1, Math.ceil(duration / recommended))
    const sceneDuration = Number((duration / sceneCount).toFixed(2))

    const storyboard = Array.from({length:sceneCount}).map((_,i) => {
      const sceneIndex = i + 1
      return {
        id:`scene-${sceneIndex}`,
        scene_index:sceneIndex,
        title:shotTitles[i % shotTitles.length],
        visual_prompt:`${prompt}. ${shotTitles[i % shotTitles.length]}. ${mood.lighting}. ${mood.lens}. Camera: ${cameraMoves[i % cameraMoves.length]}. Preserve character identity, costume, jewelry, hairstyle, makeup and temporal coherence.`,
        negative_prompt:'face drift, costume inconsistency, random jewelry, broken continuity, bad anatomy, text, watermark',
        camera_move:cameraMoves[i % cameraMoves.length],
        lens:mood.lens,
        lighting:mood.lighting,
        color_script:mood.colors,
        duration:sceneDuration,
        provider,
        continuity_hash:`${detectedMood}:identity_lock:scene:${sceneIndex}`,
      }
    })

    const response: MovieOSV4Response = {
      project_id:'movie-os-v4-demo',
      prompt,
      director_brief:{
        logline:`A cinematic autonomous movie generated from: ${prompt}`,
        genre:detectedMood.replace('_',' '),
        audience_emotion:'awe, desire, curiosity, cinematic payoff',
        visual_promise:'a complete movie timeline with continuity, rhythm, and sequential runtime',
        director_intent:'Turn a simple prompt into a cinematic production plan with memory and governance.',
        success_criteria:['Strong hook','Character consistency','Emotional escalation','Sequential runtime','Final assembly ready'],
      },
      narrative_graph:{
        nodes:['Director Prompt','Hero Identity','World Mood','Transformation Arc','Emotional Peak','Final Assembly'].map((label,i)=>({id:`node-${i+1}`,label,role:['input','character','mood','story','rhythm','delivery'][i],description:`${label} generated from prompt`,weight:1-i*0.04})),
        edges:[{source:'node-1',target:'node-2',relation:'defines'},{source:'node-2',target:'node-3',relation:'inhabits'},{source:'node-3',target:'node-4',relation:'enables'},{source:'node-4',target:'node-5',relation:'peaks_at'},{source:'node-5',target:'node-6',relation:'resolves_into'}],
      },
      mood_profile:{
        mood:detectedMood,
        secondary_moods:['fantasy','luxury','emotional'],
        lighting:mood.lighting,
        lens:mood.lens,
        color_script:mood.colors,
        texture_language:mood.textures,
        transition_language:mood.transitions,
        soundtrack_direction:'cinematic pulse with emotional breath timing',
      },
      character_bible:{
        identity_lock:`${detectedMood} hero identity locked across all scenes`,
        face:'same cinematic hero face identity',
        costume:detectedMood === 'gothic_luxury' ? 'deep ruby velvet gown with black lace and gold trim' : 'mood-consistent cinematic costume',
        jewelry:'mood-consistent crown, earrings, necklace and accessories',
        hairstyle:'consistent hairstyle silhouette and color',
        age:'adult cinematic character',
        body_silhouette:'consistent elegant cinematic silhouette',
        makeup:'consistent cinematic beauty makeup',
        continuity_rules:['No face drift','Maintain costume palette','Maintain jewelry','Maintain hairstyle','Maintain makeup','Preserve temporal coherence'],
      },
      shot_plan:storyboard.map(scene=>({scene_index:scene.scene_index,title:scene.title,shot_role:scene.title,camera_move:scene.camera_move,lens:scene.lens,framing:'cinematic composition',motion:scene.camera_move,emotion:scene.scene_index < 3 ? 'hook and identity' : scene.scene_index < sceneCount * .7 ? 'escalation' : 'payoff',duration:scene.duration,provider})),
      emotional_timeline:{
        total_duration:duration,
        peak_scene_index:Math.max(1,Math.floor(sceneCount*.72)),
        points:storyboard.map(scene=>({scene_index:scene.scene_index,emotional_state:scene.scene_index < 3 ? 'hook' : scene.scene_index < sceneCount*.7 ? 'escalation' : 'payoff',tension:Math.min(95,45+scene.scene_index*4),visual_density:Math.min(98,60+scene.scene_index*4),retention_goal:scene.scene_index===1?'stop scroll immediately':'maintain cinematic attention',silence_or_breath:scene.scene_index===1?'short silence before first motion':'breath pause between reveals'})),
      },
      storyboard,
      scene_dependency_graph:{
        dependencies:storyboard.flatMap(scene=>scene.scene_index===1?[]:[{source_scene:scene.scene_index-1,target_scene:scene.scene_index,dependency_type:'temporal_continuity',rebuild_policy:'rebuild_target_if_previous_changes'},{source_scene:1,target_scene:scene.scene_index,dependency_type:'character_identity_lock',rebuild_policy:'preserve_character_bible'}]),
      },
      sequential_runtime_plan:{
        provider,
        planned_batch_size:plannedBatchSize,
        max_concurrent_render:1,
        execution_mode:'sequential',
        steps:storyboard.map(scene=>({batch_index:Math.ceil(scene.scene_index/plannedBatchSize),scene_index:scene.scene_index,status:'queued',max_concurrent_render:1,execution_mode:'sequential'})),
      },
      editor_plan:{
        edit_style:'autonomous cinematic trailer edit',
        transitions:mood.transitions,
        pacing_rules:['hold first frame','cut on motion','peak near 70 percent','hold final reveal'],
        sound_design:['cinematic pulse','texture shimmer','ambient breath','final hit'],
        subtitle_strategy:'minimal cinematic subtitles in safe zone',
        color_grade:`${detectedMood} cinematic grade`,
      },
      assembly_plan:{
        tracks:['video_scene_track','character_continuity_track','subtitle_track','music_track','sound_design_track','transition_track','color_grade_track','memory_manifest_track'],
        artifact_targets:['final_movie_mp4','preview_movie_mp4','thumbnail_jpg','subtitle_srt','timeline_manifest_json','provider_job_manifest_json','memory_graph_update_json'],
        export_profiles:['vertical_9_16_short','square_1_1_social','cinematic_16_9_master'],
        final_duration:duration,
      },
      memory_update:{
        namespace:'default_movie_os',
        nodes:[{id:`mood:${detectedMood}`,type:'mood',label:detectedMood},{id:`lens:${mood.lens}`,type:'lens',label:mood.lens},{id:`provider:${provider}`,type:'provider',label:provider}],
        edges:[{source:`mood:${detectedMood}`,target:`lens:${mood.lens}`,relation:'uses_lens'},{source:`mood:${detectedMood}`,target:`provider:${provider}`,relation:'rendered_by'}],
        winner_dna:{mood:detectedMood,lens:mood.lens,lighting:mood.lighting,provider},
      },
    }
    setMovie(response)
  }

  function openStudio() {
    if (!movie) return
    const payload = encodeURIComponent(JSON.stringify(movie))
    const studioUrl = process.env.NEXT_PUBLIC_VIDEO_STUDIO_URL || 'http://localhost:5173'
    window.open(`${studioUrl}?movie_os_v4=${payload}`, '_blank')
  }

  return <main className="v4-shell">
    <aside className="v4-sidebar"><div className="v4-logo">Movie OS V4</div><p className="v4-muted">SUPERCool-inspired autonomous movie infrastructure with Agent16 runtime governance.</p><div className="v4-step-list">{steps.map((s,i)=><button className={i<8?'v4-step active':'v4-step'} key={s}><span>{String(i+1).padStart(2,'0')}</span><strong>{s}</strong></button>)}</div></aside>
    <section className="v4-main">
      <section className="v4-hero"><div><div className="v4-eyebrow">AUTONOMOUS AI FILM PRODUCTION INFRASTRUCTURE</div><h1>Prompt → Movie Timeline With Memory</h1><p className="v4-muted">Không render từng ảnh rời rạc. Hệ thống tạo dòng thời gian điện ảnh có trí nhớ, nhân vật nhất quán và runtime tuần tự.</p></div><button className="v4-primary" onClick={runAutonomousDirector}>Run Movie OS V4</button></section>
      <section className="v4-grid"><div className="v4-card"><div className="v4-eyebrow">USER PROMPT</div><h2>Simple prompt</h2><textarea className="v4-textarea" value={prompt} onChange={e=>setPrompt(e.target.value)} /></div><div className="v4-card"><div className="v4-eyebrow">RUNTIME CONFIG</div><h2>Provider governance</h2><div className="v4-form"><label className="v4-label">Duration<input type="number" value={duration} onChange={e=>setDuration(Number(e.target.value))}/></label><label className="v4-label">Provider<select value={provider} onChange={e=>setProvider(e.target.value)}><option value="kling">Kling</option><option value="runway">Runway</option><option value="veo">Veo</option><option value="seedance">Seedance</option></select></label><label className="v4-label">Planned batch size<input type="number" value={plannedBatchSize} onChange={e=>setPlannedBatchSize(Number(e.target.value))}/></label><label className="v4-label">Concurrency<input value="1 scene" readOnly /></label></div></div></section>
      {movie&&<><section className="v4-card"><div className="v4-eyebrow">AI DIRECTOR BRIEF</div><h2>{movie.director_brief.genre}</h2><Row label="Logline" value={movie.director_brief.logline}/><Row label="Audience emotion" value={movie.director_brief.audience_emotion}/><Row label="Visual promise" value={movie.director_brief.visual_promise}/></section><section className="v4-card"><div className="v4-eyebrow">NARRATIVE INTENT GRAPH</div><div className="v4-graph">{movie.narrative_graph.nodes.map(n=><article className="v4-node" key={n.id}><strong>{n.label}</strong><p>{n.role}</p><p>{n.description}</p></article>)}</div></section><section className="v4-grid"><div className="v4-card"><div className="v4-eyebrow">MOOD + COLOR + LENS ENGINE</div><h2>{movie.mood_profile.mood}</h2><Row label="Lighting" value={movie.mood_profile.lighting}/><Row label="Lens" value={movie.mood_profile.lens}/><div className="v4-tags">{movie.mood_profile.color_script.map(x=><span key={x}>{x}</span>)}</div></div><div className="v4-card"><div className="v4-eyebrow">CHARACTER BIBLE</div><h2>Continuity Lock</h2><Row label="Identity" value={movie.character_bible.identity_lock}/><Row label="Costume" value={movie.character_bible.costume}/><Row label="Jewelry" value={movie.character_bible.jewelry}/><Row label="Makeup" value={movie.character_bible.makeup}/></div></section><section className="v4-card"><div className="v4-eyebrow">STORYBOARD RUNTIME</div><h2>{movie.storyboard.length} scenes</h2><div className="v4-storyboard">{movie.storyboard.map(scene=><article className="v4-scene" key={scene.id}><div className="v4-frame">Scene {scene.scene_index}</div><h3>{scene.title}</h3><p>{scene.camera_move}</p><p>{scene.duration}s</p></article>)}</div></section><section className="v4-card"><div className="v4-eyebrow">EMOTIONAL TIMELINE GRAPH</div><div className="v4-rhythm">{movie.emotional_timeline.points.map(p=><div key={p.scene_index}><Row label={`Scene ${p.scene_index} · ${p.emotional_state}`} value={`Density ${p.visual_density}`}/><div className="v4-bar"><div className="v4-fill" style={{width:`${p.visual_density}%`}} /></div></div>)}</div></section><section className="v4-card"><div className="v4-eyebrow">SEQUENTIAL PROVIDER RUNTIME</div><div className="v4-runtime-grid">{movie.sequential_runtime_plan.steps.map(step=><article className="v4-render-step" key={step.scene_index}><strong>Batch {step.batch_index}</strong><p>Scene {step.scene_index}</p><p>{step.execution_mode} · 1/1</p></article>)}</div></section><section className="v4-card"><div className="v4-eyebrow">MEMORY GRAPH UPDATE</div><div className="v4-tags">{Object.entries(movie.memory_update.winner_dna).map(([k,v])=><span key={k}>{k}: {v}</span>)}</div><button className="v4-primary" style={{marginTop:18}} onClick={openStudio}>Open Autonomous Movie Studio V4</button></section></>}
    </section>
    <aside className="v4-right"><section className="v4-card"><div className="v4-eyebrow">LIVE AUTONOMOUS RUNTIME</div><h2>Director State</h2><div className="v4-log">Mood detected: {detectedMood}</div><div className="v4-log">Character Continuity Runtime: locked</div><div className="v4-log">Temporal Coherence Guard: active</div><div className="v4-log">Scene Dependency Rebuilder: ready</div><div className="v4-log">Sequential Runtime: concurrency 1/1</div></section>{movie&&<section className="v4-card"><div className="v4-eyebrow">ASSEMBLY TARGETS</div><h2>Final Movie</h2>{movie.assembly_plan.artifact_targets.slice(0,5).map(x=><Row key={x} label={x} value="ready"/>)}</section>}</aside>
  </main>
}

function Row({label,value}:{label:string;value:string|number}){return <div className="v4-row"><span>{label}</span><strong>{value}</strong></div>}
