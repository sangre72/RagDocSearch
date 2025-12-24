'use client';

import { FileText, Trash2, Calendar } from 'lucide-react';
import type { Document } from '@/types';
import { documentApi } from '@/lib/api';

interface DocumentListProps {
  documents: Document[];
  selectedIds: number[];
  onSelectionChange: (ids: number[]) => void;
  onDocumentDeleted: () => void;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function DocumentList({
  documents,
  selectedIds,
  onSelectionChange,
  onDocumentDeleted,
}: DocumentListProps) {
  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('이 문서를 삭제하시겠습니까?')) return;

    try {
      await documentApi.delete(id);
      onDocumentDeleted();
    } catch (err) {
      console.error('Delete error:', err);
      alert('문서 삭제에 실패했습니다.');
    }
  };

  const handleSelect = (id: number) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((selectedId) => selectedId !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  if (documents.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>업로드된 문서가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          onClick={() => handleSelect(doc.id)}
          className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors
            ${
              selectedIds.includes(doc.id)
                ? 'bg-blue-50 border border-blue-200'
                : 'bg-gray-50 border border-gray-100 hover:bg-gray-100'
            }`}
        >
          <input
            type="checkbox"
            checked={selectedIds.includes(doc.id)}
            onChange={() => handleSelect(doc.id)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            onClick={(e) => e.stopPropagation()}
          />
          <FileText className="w-8 h-8 text-red-500 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900 truncate">{doc.original_filename}</p>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span>{formatFileSize(doc.file_size)}</span>
              {doc.page_count && <span>{doc.page_count}페이지</span>}
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {formatDate(doc.created_at)}
              </span>
            </div>
          </div>
          <button
            onClick={(e) => handleDelete(doc.id, e)}
            className="p-2 text-gray-400 hover:text-red-500 transition-colors"
            title="삭제"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
