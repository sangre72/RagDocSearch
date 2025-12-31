'use client';

import { useState, useEffect } from 'react';
import { Settings, Server, Cpu, Check, X, Loader2, RefreshCw } from 'lucide-react';
import { providerApi } from '@/lib/api';
import type {
  ProviderListResponse,
  CurrentProviderResponse,
  ProviderHealthResponse,
  EmbeddingProviderInfo,
} from '@/types';

interface ProviderSettingsProps {
  onClose: () => void;
  onProviderChange?: () => void;
}

export default function ProviderSettings({ onClose, onProviderChange }: ProviderSettingsProps) {
  const [providers, setProviders] = useState<ProviderListResponse | null>(null);
  const [current, setCurrent] = useState<CurrentProviderResponse | null>(null);
  const [health, setHealth] = useState<ProviderHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 선택 상태
  const [selectedLLM, setSelectedLLM] = useState<string>('');
  const [selectedLLMModel, setSelectedLLMModel] = useState<string>('');
  const [selectedEmbedding, setSelectedEmbedding] = useState<string>('');
  const [selectedEmbeddingModel, setSelectedEmbeddingModel] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [providerList, currentProvider] = await Promise.all([
        providerApi.list(),
        providerApi.getCurrent(),
      ]);

      setProviders(providerList);
      setCurrent(currentProvider);

      // 현재 값으로 초기화
      setSelectedLLM(currentProvider.llm_provider);
      setSelectedLLMModel(currentProvider.llm_model);
      setSelectedEmbedding(currentProvider.embedding_provider);
      setSelectedEmbeddingModel(currentProvider.embedding_model);

      // 헬스 체크 (별도로)
      try {
        const healthStatus = await providerApi.checkHealth();
        setHealth(healthStatus);
      } catch {
        // 헬스 체크 실패는 무시
      }
    } catch (err) {
      setError('Provider 정보를 불러오는데 실패했습니다.');
      console.error('Failed to load provider data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    setUpdating(true);
    setError(null);
    try {
      await providerApi.update({
        llm_provider: selectedLLM,
        llm_model: selectedLLMModel,
        embedding_provider: selectedEmbedding,
        embedding_model: selectedEmbeddingModel,
      });
      await loadData();
      onProviderChange?.();
    } catch (err) {
      setError('Provider 업데이트에 실패했습니다.');
      console.error('Failed to update provider:', err);
    } finally {
      setUpdating(false);
    }
  };

  const selectedLLMProvider = providers?.llm_providers.find(p => p.name === selectedLLM);
  const selectedEmbeddingProvider = providers?.embedding_providers.find(
    p => p.name === selectedEmbedding
  ) as EmbeddingProviderInfo | undefined;

  const hasChanges =
    current &&
    (selectedLLM !== current.llm_provider ||
      selectedLLMModel !== current.llm_model ||
      selectedEmbedding !== current.embedding_provider ||
      selectedEmbeddingModel !== current.embedding_model);

  const embeddingChanged =
    current &&
    (selectedEmbedding !== current.embedding_provider ||
      selectedEmbeddingModel !== current.embedding_model);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400 mx-auto" />
          <p className="text-gray-500 mt-2">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* 헤더 */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Provider 설정
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 본문 */}
        <div className="p-4 space-y-6">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* LLM Provider */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
              <Cpu className="w-5 h-5" />
              LLM Provider
              {health && (
                health.llm.healthy ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <X className="w-4 h-4 text-red-500" />
                )
              )}
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Provider
                </label>
                <select
                  value={selectedLLM}
                  onChange={(e) => {
                    setSelectedLLM(e.target.value);
                    const provider = providers?.llm_providers.find(p => p.name === e.target.value);
                    if (provider && provider.models.length > 0) {
                      setSelectedLLMModel(provider.models[0]);
                    } else {
                      setSelectedLLMModel('');
                    }
                  }}
                  className="w-full px-3 py-2 border rounded-md bg-white text-gray-900 font-medium"
                >
                  {providers?.llm_providers.map((p) => (
                    <option key={p.name} value={p.name}>
                      {p.name} {p.is_local ? '(Local)' : '(Cloud)'}
                      {p.requires_api_key ? ' *' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model
                </label>
                <select
                  value={selectedLLMModel}
                  onChange={(e) => setSelectedLLMModel(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md bg-white text-gray-900 font-medium"
                  disabled={!selectedLLMProvider?.models.length}
                >
                  {selectedLLMProvider?.models.length ? (
                    selectedLLMProvider.models.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))
                  ) : (
                    <option value="">모델 없음</option>
                  )}
                </select>
              </div>
            </div>

            {/* LLM 상태 메시지 */}
            {selectedLLMProvider?.is_local && !selectedLLMProvider?.models.length && (
              <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-md">
                <p className="text-sm text-amber-800 font-medium">
                  로드된 모델이 없습니다
                </p>
                <p className="text-xs text-amber-700 mt-1">
                  {selectedLLM === 'lmstudio' && 'LM Studio에서 모델을 로드해주세요. (LM Studio 앱 → 모델 선택 → Load)'}
                  {selectedLLM === 'ollama' && 'Ollama에서 모델을 설치해주세요. (터미널: ollama pull llama3.2)'}
                  {selectedLLM === 'huggingface' && '모델 다운로드 패널에서 모델을 먼저 다운로드해주세요.'}
                </p>
              </div>
            )}

            {selectedLLMProvider?.requires_api_key && (
              <p className="text-xs text-amber-600 mt-2">
                * API 키가 필요합니다 (.env 파일에 설정)
              </p>
            )}

            {health && !health.llm.healthy && health.llm.error && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800 font-medium">연결 실패</p>
                <p className="text-xs text-red-700 mt-1">{health.llm.error}</p>
              </div>
            )}
          </div>

          {/* Embedding Provider */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
              <Server className="w-5 h-5" />
              Embedding Provider
              {health && (
                health.embedding.healthy ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <X className="w-4 h-4 text-red-500" />
                )
              )}
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Provider
                </label>
                <select
                  value={selectedEmbedding}
                  onChange={(e) => {
                    setSelectedEmbedding(e.target.value);
                    const provider = providers?.embedding_providers.find(
                      p => p.name === e.target.value
                    ) as EmbeddingProviderInfo | undefined;
                    if (provider && provider.models.length > 0) {
                      setSelectedEmbeddingModel(provider.models[0]);
                    } else {
                      setSelectedEmbeddingModel('');
                    }
                  }}
                  className="w-full px-3 py-2 border rounded-md bg-white text-gray-900 font-medium"
                >
                  {providers?.embedding_providers.map((p) => (
                    <option key={p.name} value={p.name}>
                      {p.name} {p.is_local ? '(Local)' : '(Cloud)'}
                      {p.requires_api_key ? ' *' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model
                </label>
                <select
                  value={selectedEmbeddingModel}
                  onChange={(e) => setSelectedEmbeddingModel(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md bg-white text-gray-900 font-medium"
                  disabled={!selectedEmbeddingProvider?.models.length}
                >
                  {selectedEmbeddingProvider?.models.length ? (
                    selectedEmbeddingProvider.models.map((m) => (
                      <option key={m} value={m}>
                        {m}
                        {selectedEmbeddingProvider.dimensions[m] &&
                          ` (${selectedEmbeddingProvider.dimensions[m]}d)`}
                      </option>
                    ))
                  ) : (
                    <option value="">모델 없음</option>
                  )}
                </select>
              </div>
            </div>

            {/* Embedding 상태 메시지 */}
            {selectedEmbeddingProvider?.is_local && !selectedEmbeddingProvider?.models.length && (
              <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-md">
                <p className="text-sm text-amber-800 font-medium">
                  설치된 모델이 없습니다
                </p>
                <p className="text-xs text-amber-700 mt-1">
                  {selectedEmbedding === 'huggingface' && '모델 다운로드 패널(↓ 버튼)에서 임베딩 모델을 먼저 다운로드해주세요.'}
                  {selectedEmbedding === 'ollama' && 'Ollama에서 임베딩 모델을 설치해주세요. (터미널: ollama pull nomic-embed-text)'}
                </p>
              </div>
            )}

            {selectedEmbeddingProvider?.requires_api_key && (
              <p className="text-xs text-amber-600 mt-2">
                * API 키가 필요합니다 (.env 파일에 설정)
              </p>
            )}

            {health && !health.embedding.healthy && health.embedding.error && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800 font-medium">연결 실패</p>
                <p className="text-xs text-red-700 mt-1">{health.embedding.error}</p>
              </div>
            )}

            {embeddingChanged && (
              <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <p className="text-sm text-yellow-800">
                  주의: Embedding Provider를 변경하면 기존 문서를 재인덱싱해야 합니다.
                </p>
              </div>
            )}
          </div>

          {/* 현재 상태 */}
          {current && (
            <div className="text-sm text-gray-500 bg-gray-100 rounded-md p-3">
              <p><strong>현재 LLM:</strong> {current.llm_provider} / {current.llm_model}</p>
              <p><strong>현재 Embedding:</strong> {current.embedding_provider} / {current.embedding_model} ({current.embedding_dimension}d)</p>
            </div>
          )}
        </div>

        {/* 푸터 */}
        <div className="flex items-center justify-between p-4 border-t bg-gray-50">
          <button
            onClick={loadData}
            className="flex items-center gap-1 text-gray-600 hover:text-gray-800"
          >
            <RefreshCw className="w-4 h-4" />
            새로고침
          </button>

          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-md"
            >
              취소
            </button>
            <button
              onClick={handleUpdate}
              disabled={updating || !hasChanges}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {updating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Settings className="w-4 h-4" />
              )}
              적용
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
