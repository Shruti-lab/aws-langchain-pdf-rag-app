import { useState } from 'react';
import { documentService } from '../services/api';

interface DocumentUploadProps {
  onUploadComplete: () => void;
}

export const DocumentUpload = ({ onUploadComplete }: DocumentUploadProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const [strategy, setStrategy] = useState<string>('vector_store');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [strategies, setStrategies] = useState<string[]>(['vector_store', 'sentence_window']);

  // Fetch available strategies on component mount
  useState(() => {
    documentService.getIndexingStrategies()
      .then(response => {
        if (response.strategies && response.strategies.length > 0) {
          setStrategies(response.strategies);
        }
      })
      .catch(error => {
        console.error('Failed to fetch strategies:', error);
      });
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(Array.from(event.target.files));
    }
  };

  const handleStrategyChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setStrategy(event.target.value);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (files.length === 0) {
      setError('Please select at least one file.');
      return;
    }
    
    setIsUploading(true);
    setError(null);
    
    try {
      await documentService.uploadDocuments(files, strategy);
      setFiles([]);
      onUploadComplete();
    } catch (error) {
      console.error('Upload failed:', error);
      setError('Failed to upload documents. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };
  
  return (
    <div className="document-upload bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Indexing Strategy
          </label>
          <select
            value={strategy}
            onChange={handleStrategyChange}
            className="w-full p-2 border rounded-md"
            disabled={isUploading}
          >
            {strategies.map(s => (
              <option key={s} value={s}>
                {s === 'vector_store' ? 'Vector Store' : 'Sentence Window'}
              </option>
            ))}
          </select>
          <p className="text-sm text-gray-500 mt-1">
            {strategy === 'vector_store' 
              ? 'Standard chunking with vector embedding' 
              : 'Sentence-based chunking with context windows'}
          </p>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Select Documents (PDF, TXT)
          </label>
          <input
            type="file"
            accept=".pdf,.txt"
            multiple
            onChange={handleFileChange}
            className="w-full p-2 border rounded-md"
            disabled={isUploading}
          />
        </div>
        
        {files.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-medium">Selected Files:</p>
            <ul className="text-sm">
              {files.map((file, index) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
        
        <button
          type="submit"
          disabled={isUploading || files.length === 0}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md disabled:bg-blue-300"
        >
          {isUploading ? 'Uploading...' : 'Upload Documents'}
        </button>
      </form>
    </div>
  );
};