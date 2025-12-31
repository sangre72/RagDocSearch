/**
 * Provider 관련 타입 정의
 */

// === LLM/Embedding Provider 정보 ===

export interface ProviderInfo {
  name: string;
  models: string[];
  is_local: boolean;
  requires_api_key: boolean;
}

export interface EmbeddingProviderInfo extends ProviderInfo {
  dimensions: Record<string, number>;
}

export interface ProviderListResponse {
  llm_providers: ProviderInfo[];
  embedding_providers: EmbeddingProviderInfo[];
}

// === 현재 Provider 설정 ===

export interface CurrentProviderResponse {
  llm_provider: string;
  llm_model: string;
  llm_temperature: number;
  embedding_provider: string;
  embedding_model: string;
  embedding_dimension: number;
}

export interface UpdateProviderRequest {
  llm_provider?: string;
  llm_model?: string;
  llm_temperature?: number;
  embedding_provider?: string;
  embedding_model?: string;
}

// === Provider 상태 ===

export interface ProviderHealthResponse {
  llm: {
    provider: string;
    model: string;
    healthy: boolean;
    error?: string;
  };
  embedding: {
    provider: string;
    model: string;
    healthy: boolean;
    error?: string;
  };
}

// === 모델 다운로드 ===

export interface AvailableModel {
  name: string;
  description: string;
  size_mb: number;
  dimension?: number;
}

export interface CachedModel {
  name: string;
  path: string;
  size_bytes: number;
  size_mb: number;
  downloaded_at: string;
}

export interface DownloadStatus {
  model_name: string;
  status: 'pending' | 'downloading' | 'completed' | 'failed' | 'not_found';
  progress?: number;
  error?: string;
}

export interface DownloadRequest {
  model_name: string;
  model_type: 'embedding' | 'llm';
}
