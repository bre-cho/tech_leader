export type MovieDirectorResponse = {
  project_id: string
  prompt: string
  mood_profile: {
    primary_mood: string
    lighting: string
    lens: string
    color_script: string[]
    camera_movement: string[]
  }
  character_bible: {
    face: string
    costume: string
    jewelry: string
    hairstyle: string
    makeup: string
    continuity_rules: string[]
  }
  storyboard: Array<{
    id: string
    scene_index: number
    title: string
    visual_prompt: string
    camera: string
    motion: string
    lens: string
    lighting: string
    duration: number
    continuity_notes: string[]
    provider: string
  }>
  rhythm_timeline: {
    duration: number
    peak_scene_index: number
    rhythm_points: Array<{
      scene_index: number
      emotional_pacing: string
      tension: number
      visual_energy: number
      retention_goal: string
    }>
  }
  editor_plan: {
    edit_style: string
    transitions: string[]
    pacing_notes: string[]
    sound_design: string[]
    subtitle_strategy: string
  }
  assembly_plan: {
    timeline_tracks: string[]
    final_duration: number
    artifact_targets: string[]
    export_profiles: string[]
  }
  sequential_render_policy: {
    planned_batch_size: number
    max_concurrent_render: number
    execution_mode: string
    provider: string
  }
}
