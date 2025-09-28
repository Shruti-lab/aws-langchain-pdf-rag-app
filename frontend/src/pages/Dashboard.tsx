import { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { DocumentUpload } from '../components/DocumentUpload';
import { DocumentList } from '../components/DocumentList';
import { QuestionInput } from '../components/QuestionInput';
import { AnswerDisplay } from '../components/AnswerDisplay';
import { qaService, type QueryResponse } from '../services/api';

export const Dashboard = () => {
  const [strategies, setStrategies] = useState<string[]>(['vector_store', 'sentence_window']);
  const [refreshDocuments, setRefreshDocuments] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);

  useEffect(() => {
    // Fetch available strategies
    qaService.getAvailableStrategies()
      .then(response => {
        if (response.strategies && response.strategies.length > 0) {
          setStrategies(response.strategies);
        }
      })
      .catch(error => {
        console.error('Failed to fetch strategies:', error);
      });
  }, []);

  const handleDocumentUpload = () => {
    setRefreshDocuments(prev => !prev);
  };

  const handleQuestionSubmit = async (question: string, strategy: string, enableEvaluation: boolean) => {
    setIsQuerying(true);
    
    try {
      const response = await qaService.queryDocuments(question, strategy, 5, enableEvaluation);
      setQueryResponse(response);
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      <div className="container mx-auto py-8 px-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <div className="mb-8">
              <DocumentUpload onUploadComplete={handleDocumentUpload} />
            </div>
            <DocumentList 
              onDelete={handleDocumentUpload} 
              refresh={refreshDocuments} 
            />
          </div>
          
          <div className="lg:col-span-2">
            <div className="mb-6">
              <QuestionInput 
                onSubmit={handleQuestionSubmit} 
                strategies={strategies}
                isLoading={isQuerying}
              />
            </div>
            
            <AnswerDisplay 
              response={queryResponse}
              isLoading={isQuerying}
            />
          </div>
        </div>
      </div>
    </div>
  );
};