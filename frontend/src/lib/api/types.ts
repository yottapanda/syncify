export interface SyncRequest {
  id: number;
  user_id: string;
  song_count: number;
  progress: number;
  created: Date;
  completed: Date | null;
}

export interface User {
  id: string;
  display_name: string;
}
