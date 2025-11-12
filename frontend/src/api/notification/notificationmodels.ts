import type { UUID } from "../common/types";

export interface NotificationOut {
  id: UUID;
  created_at: string;
  emitter: string;
  reason: string;
}

export interface NotificationDetailsOut {
  id: UUID;
  created_at: string;
  user_id: UUID;
  source_event_id?: UUID | null;
  emitter: string;
  reason: string;
  message: string;
}