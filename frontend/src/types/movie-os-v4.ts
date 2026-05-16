export type MovieOSV4Response = {
  project_id: string
  prompt: string
  mood_profile: {
    mood: string
    lighting: string
    lens: string
    color_script: string[]
    transition_language: string[]
    soundtrack_direction: string
  }
  character_bible: {
    identity_lock: string
    face: string
    costume: string
    jewelry: string
    hairstyle: string
    makeup: string
    continuity_rules: string[]
  }
  emotional_timeline: {
    total_duration: number
    peak_scene_index: number
    points: Array<{
      scene_index: number
      emotional_state: string
      tension: number
      visual_density: number
      retention_goal: string
      silence_or_breath: string
    }>
  }
  storyboard: Array<{
    id: string
    scene_index: number
    title: string
    visual_prompt: string
    negative_prompt: string
    camera_move: string
    lens: string
    lighting: string
    duration: number
    provider: string
    continuity_hash: string
  }>
  sequential_runtime_plan: {
    provider: string
    planned_batch_size: number
    max_concurrent_render: number
    execution_mode: string
    steps: Array<{
      batch_index: number
      scene_index: number
      status: string
      max_concurrent_render: number
      execution_mode: string
    }>
  }
  editor_plan: {
    edit_style: string
    transitions: string[]
    pacing_rules: string[]
    sound_design: string[]
    subtitle_strategy: string
    color_grade: string
  }
  assembly_plan: {
    tracks: string[]
    artifact_targets: string[]
    export_profiles: string[]
    final_duration: number
  }
}
