export const Header = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 shadow-md">
      <div className="container mx-auto">
        <h1 className="text-2xl font-bold">RAG Document Q&A</h1>
        <p className="text-sm">Ask questions about your documents using AI</p>
      </div>
    </header>
  );
};