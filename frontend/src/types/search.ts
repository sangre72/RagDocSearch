/**
 * Search domain types
 * Synced with backend: app/schemas.py
 */

export interface SearchQuery {
  query: string;
  top_k?: number;
  document_ids?: number[];
}

export interface SearchResult {
  chunk_id: number;
  document_id: number;
  filename: string;
  content: string;
  page_number: number | null;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
}

export interface ChatQuery {
  query: string;
  document_ids?: number[];
  top_k?: number;
}

export interface ChatResponse {
  answer: string;
  sources: SearchResult[];
}
