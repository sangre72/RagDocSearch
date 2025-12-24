'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { documentApi } from '@/lib/api';

interface DocumentUploadProps {
  onUploadComplete: () => void;
}

export default function DocumentUpload({ onUploadComplete }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('PDF 파일만 업로드 가능합니다.');
        return;
      }

      setUploading(true);
      setError(null);

      try {
        await documentApi.upload(file);
        onUploadComplete();
      } catch (err) {
        console.error('Upload error:', err);
        setError('파일 업로드에 실패했습니다.');
      } finally {
        setUploading(false);
      }
    },
    [onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-2">
          {uploading ? (
            <>
              <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
              <p className="text-gray-600">문서를 처리하고 있습니다...</p>
            </>
          ) : isDragActive ? (
            <>
              <Upload className="w-10 h-10 text-blue-500" />
              <p className="text-blue-500">여기에 파일을 놓으세요</p>
            </>
          ) : (
            <>
              <FileText className="w-10 h-10 text-gray-400" />
              <p className="text-gray-600">PDF 파일을 드래그하거나 클릭하여 업로드</p>
              <p className="text-sm text-gray-400">최대 10MB</p>
            </>
          )}
        </div>
      </div>
      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
    </div>
  );
}
