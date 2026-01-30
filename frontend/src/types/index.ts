export interface Project {
  id: string;
  title: string;
  content: string;
  outline: Outline | null;
  script: Script | null;
  status: string;
  video_path: string | null;
  audio_path: string | null;
  created_at: string;
  updated_at: string;
  scenes: Scene[];
}

export interface ProjectListItem {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Scene {
  id: string;
  project_id: string;
  order_index: number;
  title: string;
  narration: string;
  visual_desc: string;
  image_path: string | null;
  duration_sec: number;
  created_at: string;
}

export interface OutlineSection {
  title: string;
  key_points: string[];
}

export interface Outline {
  sections: OutlineSection[];
}

export interface ScriptScene {
  title: string;
  narration: string;
  visual_desc: string;
}

export interface Script {
  scenes: ScriptScene[];
}

export interface AssetStatus {
  status: string;
  progress: number;
  message: string;
}

export interface VideoStatus {
  status: string;
  progress: number;
  video_path: string | null;
  message: string;
}
