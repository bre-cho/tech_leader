export type FashionRuntimeResponse = {
  project_id: string
  brief: string
  visual_dna: {
    archetype: string
    palette: string[]
    material_language: string[]
    lighting_language: string
    camera_language: string[]
    hair_signature: string
    luxury_signals: string[]
    motion_signals: string[]
    commerce_angle: string
    scores: Record<string, number>
  }
  emotional_graph: {
    nodes: Array<Record<string, string>>
    edges: Array<Record<string, string>>
    dominant_emotion: string
    virality_hook: string
  }
  continuity_lock: {
    face_identity: string
    hair_identity: string
    outfit_rules: string[]
    makeup_rules: string[]
    pose_rules: string[]
    drift_guards: string[]
  }
  fashion_motion: {
    motion_style: string
    camera_rhythm: string[]
    pose_sequence: string[]
    hair_motion: string
    cloth_motion: string
  }
  beauty_commerce: {
    product_positioning: string
    audience_desire: string
    trust_triggers: string[]
    conversion_triggers: string[]
    content_angle: string
  }
  storyboard: Array<{
    id: string
    scene_index: number
    title: string
    visual_prompt: string
    camera: string
    motion: string
    duration: number
    provider: string
    continuity_notes: string[]
  }>
  sequential_render_plan: Array<{
    batch_index: number
    scene_index: number
    status: string
    max_concurrent_render: number
    execution_mode: string
  }>
  winner_dna_memory: Record<string, any>
}
