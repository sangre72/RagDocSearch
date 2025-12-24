'use client';

import { useState, useEffect } from 'react';
import { FileText, MessageCircle, RefreshCw } from 'lucide-react';
import DocumentUpload from '@/components/DocumentUpload';
import DocumentList from '@/components/DocumentList';
import ChatInterface from '@/components/ChatInterface';
import { documentApi } from '@/lib/api';
import type { Document } from '@/types';

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await documentApi.list();
      setDocuments(response.documents);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <FileText className="w-8 h-8 text-blue-500" />
            <h1 className="text-2xl font-bold text-gray-900">RAG Document Search</h1>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            PDF 문서를 업로드하고 AI로 검색하세요
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Documents */}
          <div className="lg:col-span-1 space-y-6">
            {/* Upload Section */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                문서 업로드
              </h2>
              <DocumentUpload onUploadComplete={fetchDocuments} />
            </div>

            {/* Document List */}
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  문서 목록 ({documents.length})
                </h2>
                <button
                  onClick={fetchDocuments}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                  title="새로고침"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>
              {selectedIds.length > 0 && (
                <div className="mb-3 flex items-center justify-between text-sm">
                  <span className="text-blue-600">
                    {selectedIds.length}개 선택됨
                  </span>
                  <button
                    onClick={() => setSelectedIds([])}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    선택 해제
                  </button>
                </div>
              )}
              {loading ? (
                <div className="flex justify-center py-8">
                  <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
                </div>
              ) : (
                <DocumentList
                  documents={documents}
                  selectedIds={selectedIds}
                  onSelectionChange={setSelectedIds}
                  onDocumentDeleted={fetchDocuments}
                />
              )}
            </div>
          </div>

          {/* Right Panel - Chat */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow h-[calc(100vh-200px)] flex flex-col">
              <div className="p-4 border-b">
                <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                  <MessageCircle className="w-5 h-5" />
                  문서 검색 및 질문
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  {selectedIds.length > 0
                    ? `선택된 ${selectedIds.length}개 문서에서 검색`
                    : '모든 문서에서 검색'}
                </p>
              </div>
              <div className="flex-1 overflow-hidden">
                <ChatInterface selectedDocumentIds={selectedIds} />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
