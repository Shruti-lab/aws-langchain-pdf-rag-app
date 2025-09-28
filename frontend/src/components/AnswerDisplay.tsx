import { useState } from 'react';
import { type QueryResponse } from '../services/api';

interface AnswerDisplayProps {
  response: QueryResponse | null;
  isLoading: boolean;
}

export const AnswerDisplay = ({ response, isLoading }: AnswerDisplayProps) => {
  const [showSources, setShowSources] = useState(false);

  if (isLoading) {
    return (
      <div className="answer-display bg-white p-6 rounded-lg shadow-md">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6 mb-2"></div>
        </div>
        <div className="mt-6 text-center text-gray-500">
          Generating answer...
        </div>
      </div>
    );
  }

  if (!response) {
    return null;
  }

  return (
    <div className="answer-display bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Answer</h2>
      
      <div className="mb-6">
        <div className="prose max-w-none">
          {response.answer.split('\n').map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
      </div>
      
      {response.sources && response.sources.length > 0 && (
        <div className="mt-4">
          <button
            onClick={() => setShowSources(!showSources)}
            className="text-blue-600 text-sm flex items-center"
          >
            {showSources ? 'Hide Sources' : 'Show Sources'} ({response.sources.length})
            <svg 
              className={`ml-1 h-4 w-4 transition-transform ${showSources ? 'rotate-180' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {showSources && (
            <div className="mt-3 border-t pt-3">
              <h3 className="font-medium text-sm mb-2">Sources:</h3>
              <ul className="text-sm space-y-2">
                {response.sources.map((source, index) => (
                  <li key={index} className="p-3 bg-gray-50 rounded">
                    <div className="font-medium mb-1">
                      {source.filename} 
                      <span className="text-gray-500 ml-2">
                        (Score: {(source.score * 100).toFixed(1)}%)
                      </span>
                    </div>
                    <div className="text-gray-700">{source.text_snippet}</div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {response.evaluation_enabled && response.metrics && (
        <div className="mt-6 p-4 bg-blue-50 rounded-md">
          <h3 className="font-medium text-sm mb-2">Evaluation Metrics:</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {Object.entries(response.metrics).map(([key, value]: [string, any]) => (
              <div key={key} className="text-center p-3 bg-white rounded shadow-sm">
                <div className="text-xs text-gray-500">{key}</div>
                <div className="text-lg font-semibold">
                  {typeof value.score === 'number' ? (value.score * 100).toFixed(1) + '%' : value.score}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-4 text-sm text-gray-500">
        Strategy: {response.strategy === 'vector_store' ? 'Vector Store' : 'Sentence Window'}
      </div>
    </div>
  );
};