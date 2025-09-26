import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Document {
  document_id: string;
  filename: string;
  file_path: string;
  num_pages: number;
  status: string;
  indexing_strategy: string;
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    filename: string;
    document_id: string;
    score: number;
    text_snippet: string;
  }>;
  strategy: string;
  evaluation_enabled: boolean;
  metrics?: any;
}

export const documentService = {
  uploadDocuments: async (files: File[], indexingStrategy: string) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('indexing_strategy', indexingStrategy);
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  listDocuments: async () => {
    const response = await api.get('/documents/list');
    return response.data;
  },
  
  deleteDocument: async (documentId: string) => {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  },
  
  getIndexingStrategies: async () => {
    const response = await api.get('/documents/strategies');
    return response.data;
  },
};

export const qaService = {
  queryDocuments: async (question: string, strategy: string, similarityTopK: number = 5, enableEvaluation: boolean = false) => {
    const response = await api.post('/qa/query', {
      question,
      strategy,
      similarity_top_k: similarityTopK,
      enable_evaluation: enableEvaluation,
    });
    return response.data as QueryResponse;
  },
  
  compareStrategies: async (question: string, strategies: string[] = ['vector_store', 'sentence_window'], similarityTopK: number = 5) => {
    const response = await api.post('/qa/compare', {
      question,
      strategies,
      similarity_top_k: similarityTopK,
    });
    return response.data;
  },
  
  getAvailableStrategies: async () => {
    const response = await api.get('/qa/strategies');
    return response.data;
  },
};