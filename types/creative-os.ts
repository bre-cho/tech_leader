export type ProviderKey = 'veo' | 'runway' | 'kling' | 'seedance';
export type ImageSource = 'upload' | 'generated';

export type StoryboardPlan = {
  project_id: string;
  image_source: ImageSource;
  image_url: string;
  target_video_duration: number;
  provider: ProviderKey;
  recommended_duration_per_scene: number;
  scene_count: number;
  scene_duration: number;
  planned_batch_size: number;
  max_concurrent_render: 1;
  total_batches: number;
  execution_mode: 'sequential';
  scenes: Array<{
    id: string;
    index: number;
    title: string;
    camera: string;
    motion: string;
    subtitle: string;
    provider: string;
    duration: number;
    continuity_key: string;
    status: string;
  }>;
  batches: Array<{
    id: string;
    batch_index: number;
    scene_indexes: number[];
    planned_batch_size: number;
    max_concurrent_render: 1;
    execution_mode: string;
    status: string;
  }>;
};
