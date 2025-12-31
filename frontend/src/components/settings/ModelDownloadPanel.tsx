'use client';

import { useState, useEffect } from 'react';
import {
  Download,
  X,
  ChevronDown,
  ChevronUp,
  Loader2,
  Check,
  AlertCircle,
  Trash2,
  HardDrive,
} from 'lucide-react';
import { modelApi } from '@/lib/api';
import type { AvailableModel, CachedModel, DownloadStatus } from '@/types';

interface ModelDownloadPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ModelDownloadPanel({ isOpen, onClose }: ModelDownloadPanelProps) {
  const [minimized, setMinimized] = useState(false);
  const [activeTab, setActiveTab] = useState<'available' | 'cached'>('available');
  const [modelType, setModelType] = useState<'embedding' | 'llm'>('embedding');
  const [availableModels, setAvailableModels] = useState<AvailableModel[]>([]);
  const [cachedModels, setCachedModels] = useState<CachedModel[]>([]);
  const [downloadingModels, setDownloadingModels] = useState<Map<string, DownloadStatus>>(new Map());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadModels();
    }
  }, [isOpen, modelType]);

  const loadModels = async () => {
    setLoading(true);
    try {
      const [available, cached] = await Promise.all([
        modelType === 'embedding'
          ? modelApi.getAvailableEmbedding()
          : modelApi.getAvailableLLM(),
        modelApi.getCached(),
      ]);
      setAvailableModels(available);
      setCachedModels(cached);
    } catch (err) {
      console.error('Failed to load models:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (model: AvailableModel) => {
    const status: DownloadStatus = {
      model_name: model.name,
      status: 'downloading',
      progress: 0,
    };
    setDownloadingModels(prev => new Map(prev).set(model.name, status));

    try {
      await modelApi.startDownload({
        model_name: model.name,
        model_type: modelType,
      });

      // 폴링으로 상태 확인
      const pollStatus = async () => {
        const currentStatus = await modelApi.getDownloadStatus(model.name);
        setDownloadingModels(prev => new Map(prev).set(model.name, currentStatus));

        if (currentStatus.status === 'downloading' || currentStatus.status === 'pending') {
          setTimeout(pollStatus, 2000);
        } else {
          // 완료 또는 실패
          setTimeout(() => {
            setDownloadingModels(prev => {
              const next = new Map(prev);
              next.delete(model.name);
              return next;
            });
            loadModels(); // 캐시 목록 새로고침
          }, 2000);
        }
      };

      pollStatus();
    } catch (err) {
      console.error('Failed to start download:', err);
      setDownloadingModels(prev => new Map(prev).set(model.name, {
        model_name: model.name,
        status: 'failed',
        error: 'Download failed',
      }));
    }
  };

  const handleDelete = async (model: CachedModel) => {
    if (!confirm(`${model.name} 모델을 삭제하시겠습니까?`)) return;

    try {
      await modelApi.deleteModel(model.name);
      loadModels();
    } catch (err) {
      console.error('Failed to delete model:', err);
    }
  };

  const isModelCached = (modelName: string) => {
    return cachedModels.some(m => m.name === modelName);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    } else if (bytes < 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    } else {
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white rounded-lg shadow-2xl border z-40">
      {/* 헤더 */}
      <div
        className="flex items-center justify-between p-3 bg-gray-100 rounded-t-lg cursor-pointer"
        onClick={() => setMinimized(!minimized)}
      >
        <div className="flex items-center gap-2">
          <Download className="w-5 h-5 text-blue-600" />
          <span className="font-semibold text-gray-900">모델 다운로드</span>
          {downloadingModels.size > 0 && (
            <span className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">
              {downloadingModels.size}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {minimized ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* 본문 */}
      {!minimized && (
        <div className="max-h-96 overflow-hidden flex flex-col">
          {/* 탭 */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('available')}
              className={`flex-1 py-2 text-sm font-medium ${
                activeTab === 'available'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-700'
              }`}
            >
              다운로드 가능
            </button>
            <button
              onClick={() => setActiveTab('cached')}
              className={`flex-1 py-2 text-sm font-medium ${
                activeTab === 'cached'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-700'
              }`}
            >
              설치됨 ({cachedModels.length})
            </button>
          </div>

          {/* 모델 타입 선택 (다운로드 가능 탭) */}
          {activeTab === 'available' && (
            <div className="border-b bg-gray-50">
              <div className="flex gap-2 p-2">
                <button
                  onClick={() => setModelType('embedding')}
                  className={`flex-1 py-1.5 text-xs rounded font-medium ${
                    modelType === 'embedding'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  Embedding
                </button>
                <button
                  onClick={() => setModelType('llm')}
                  className={`flex-1 py-1.5 text-xs rounded font-medium ${
                    modelType === 'llm'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  LLM
                </button>
              </div>
              <p className="px-2 pb-2 text-xs text-gray-600">
                {modelType === 'embedding'
                  ? '📌 문서 검색용 벡터 임베딩 모델 (HuggingFace)'
                  : '📌 로컬 실행용 경량 LLM 모델 (HuggingFace)'}
              </p>
            </div>
          )}

          {/* 모델 목록 */}
          <div className="overflow-y-auto flex-1 p-2">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
              </div>
            ) : activeTab === 'available' ? (
              availableModels.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-gray-600 font-medium">
                    사용 가능한 모델이 없습니다
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    서버 연결을 확인해주세요
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {availableModels.map((model) => {
                    const downloading = downloadingModels.get(model.name);
                    const cached = isModelCached(model.name);

                    return (
                      <div
                        key={model.name}
                        className="p-2 border rounded-md bg-white hover:bg-gray-50"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {model.name.split('/').pop()}
                            </p>
                            <p className="text-xs text-gray-700 truncate">
                              {model.description}
                            </p>
                            <p className="text-xs text-gray-600">
                              {model.size_mb >= 1024
                                ? `${(model.size_mb / 1024).toFixed(1)} GB`
                                : `${model.size_mb} MB`}
                              {model.dimension && ` • ${model.dimension}d`}
                            </p>
                          </div>

                          <div className="ml-2">
                            {cached ? (
                              <span className="text-green-500">
                                <Check className="w-5 h-5" />
                              </span>
                            ) : downloading ? (
                              downloading.status === 'failed' ? (
                                <span className="text-red-500">
                                  <AlertCircle className="w-5 h-5" />
                                </span>
                              ) : (
                                <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                              )
                            ) : (
                              <button
                                onClick={() => handleDownload(model)}
                                className="p-1 text-blue-500 hover:bg-blue-50 rounded"
                              >
                                <Download className="w-5 h-5" />
                              </button>
                            )}
                          </div>
                        </div>

                        {downloading && downloading.status === 'downloading' && (
                          <div className="mt-2">
                            <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-500 transition-all"
                                style={{ width: `${downloading.progress || 0}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )
            ) : (
              cachedModels.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-gray-600 font-medium">
                    설치된 모델이 없습니다
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    &apos;다운로드 가능&apos; 탭에서 모델을 다운로드하세요
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {cachedModels.map((model) => (
                    <div
                      key={model.name}
                      className="p-2 border rounded-md bg-white flex items-center justify-between"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <HardDrive className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {model.name.split('/').pop()}
                          </p>
                          <p className="text-xs text-gray-600">
                            {formatSize(model.size_bytes)}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDelete(model)}
                        className="p-1 text-red-500 hover:bg-red-50 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}
