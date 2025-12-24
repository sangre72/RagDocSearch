import axios from 'axios';
import type {
  Document,
  DocumentListResponse,
  UploadResponse,
  SearchResponse,
  ChatResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const documentApi = {
  upload: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (): Promise<DocumentListResponse> => {
    const response = await api.get<DocumentListResponse>('/documents');
    return response.data;
  },

  get: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${id}`);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },
};

export const searchApi = {
  search: async (
    query: string,
    topK: number = 5,
    documentIds?: number[]
  ): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/search', {
      query,
      top_k: topK,
      document_ids: documentIds,
    });
    return response.data;
  },

  chat: async (
    query: string,
    topK: number = 5,
    documentIds?: number[]
  ): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/search/chat', {
      query,
      top_k: topK,
      document_ids: documentIds,
    });
    return response.data;
  },
};
