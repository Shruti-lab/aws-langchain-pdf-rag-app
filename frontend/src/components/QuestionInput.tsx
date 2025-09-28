import { useState } from 'react';

interface QuestionInputProps {
  onSubmit: (question: string, strategy: string, enableEvaluation: boolean) => void;
  strategies: string[];
  isLoading: boolean;
}

export const QuestionInput = ({ onSubmit, strategies, isLoading }: QuestionInputProps) => {
  const [question, setQuestion] = useState('');
  const [strategy, setStrategy] = useState(strategies[0] || 'vector_store');
  const [enableEvaluation, setEnableEvaluation] = useState(false);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (question.trim()) {
      onSubmit(question, strategy, enableEvaluation);
    }
  };

  return (
    <div className="question-input bg-white p-6 rounded-lg shadow-md">
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Ask a question about your documents
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What are the key points discussed in the document?"
            className="w-full p-3 border rounded-md h-24"
            disabled={isLoading}
            required
          />
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2">
              Indexing Strategy
            </label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full p-2 border rounded-md"
              disabled={isLoading}
            >
              {strategies.map((s) => (
                <option key={s} value={s}>
                  {s === 'vector_store' ? 'Vector Store' : 'Sentence Window'}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end mb-2 sm:mb-0">
            <label className="inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={enableEvaluation}
                onChange={(e) => setEnableEvaluation(e.target.checked)}
                className="form-checkbox h-5 w-5 text-blue-600"
                disabled={isLoading}
              />
              <span className="ml-2 text-sm">Enable Evaluation</span>
            </label>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md disabled:bg-blue-300"
        >
          {isLoading ? 'Processing...' : 'Submit Question'}
        </button>
      </form>
    </div>
  );
};