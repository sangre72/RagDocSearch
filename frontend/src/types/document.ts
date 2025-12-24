/**
 * Document domain types
 * Synced with backend: app/schemas.py
 */

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  page_count: number | null;
  created_at: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface UploadResponse {
  message: string;
  document: Document;
}
