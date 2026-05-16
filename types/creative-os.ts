export type ProviderKey = 'veo' | 'runway' | 'kling' | 'seedance' | 'seedance2-fast'
export type ImageSource = 'upload' | 'generated'
export type StoryboardPlan = {
  project_id: string
  image_source: ImageSource
  image_url: string
  target_video_duration: number
  provider: ProviderKey
  recommended_duration_per_scene: number
  scene_count: number
  scene_duration: number
  planned_batch_size: number
  max_concurrent_render: 1
  total_batches: number
  execution_mode: 'sequential'
  scenes: Array<{ id: string; index: number; title: string; camera: string; motion: string; subtitle: string; provider: string; duration: number; continuity_key: string; status: string }>
  batches: Array<{ id: string; batch_index: number; scene_indexes: number[]; planned_batch_size: number; max_concurrent_render: 1; execution_mode: string; status: string }>
}

export type ProviderDurationProfile = {
  provider: ProviderKey
  recommended_duration_per_scene: number
  max_duration_per_scene: number
  default_planned_batch_size: number
  max_concurrent_render: 1
  cooldown_seconds: number
  retry_limit: number
}

export type RenderStep = {
  batch_index: number
  scene_index: number
  status: string
  max_concurrent_render: 1
  execution_mode: 'sequential'
  provider?: string
  artifact_path?: string | null
  started_at?: string | null
  completed_at?: string | null
  error?: string | null
}

export type RenderExecutionSnapshot = {
  project_id: string
  provider: string
  status: 'idle' | 'running' | 'completed' | 'failed'
  scene_count: number
  planned_batch_size: number
  execution_mode: 'sequential'
  max_concurrent_render: 1
  started_at: string | null
  completed_at: string | null
  completed_scenes: number
  failed_scenes: number
  steps: RenderStep[]
}

export type GeneratedSourceImage = {
  status: 'succeeded' | 'failed'
  prompt: string
  image_url: string
  artifact_path: string
  model: string
  is_mock: boolean
}
