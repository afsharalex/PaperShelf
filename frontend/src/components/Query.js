import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Query.css';

const Query = () => {
  const [queryText, setQueryText] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [showResponse, setShowResponse] = useState(false);
  const [queryHistory, setQueryHistory] = useState([]);

  // Load query history from localStorage on component mount
  useEffect(() => {
    const storedHistory = JSON.parse(localStorage.getItem('queryHistory')) || [];
    setQueryHistory(storedHistory);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!queryText.trim()) {
      alert('Please enter a query.');
      return;
    }
    
    // Show loading spinner
    setLoading(true);
    setShowResponse(false);
    
    try {
      const response = await axios.post('/query', {
        query: queryText,
        top_k: 5
      });
      
      // Display the response
      setResponse(response.data);
      setShowResponse(true);
      
      // Add to history
      addToHistory(response.data);
      
      // Clear the form
      setQueryText('');
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      // Hide loading spinner
      setLoading(false);
    }
  };

  const addToHistory = (data) => {
    // Create a new array with the new query at the beginning
    const updatedHistory = [data, ...queryHistory];
    
    // Limit history to 10 items
    if (updatedHistory.length > 10) {
      updatedHistory.pop();
    }
    
    // Update state
    setQueryHistory(updatedHistory);
    
    // Save to local storage
    localStorage.setItem('queryHistory', JSON.stringify(updatedHistory));
  };

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear your query history?')) {
      setQueryHistory([]);
      localStorage.setItem('queryHistory', JSON.stringify([]));
    }
  };

  return (
    <div>
      <h1>Query Academic Papers</h1>
      
      <p>Ask questions about your uploaded papers. Our RAG system will retrieve relevant information and generate accurate answers.</p>
      
      <form id="queryForm" className="query-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="queryText">Your Question:</label>
          <textarea 
            id="queryText" 
            className="query-input" 
            placeholder="e.g., What are the main findings of the paper?" 
            required
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
          ></textarea>
        </div>
        <button type="submit" className="submit-btn">Submit Query</button>
      </form>
      
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Processing your query... This may take a moment.</p>
        </div>
      )}
      
      {showResponse && response && (
        <div className="response">
          <h3>Answer</h3>
          <div className="response-content">
            <p>{response.answer}</p>
          </div>
          {response.retrieved_documents && response.retrieved_documents.length > 0 && (
            <div className="retrieved-documents">
              <h4>Retrieved Documents:</h4>
              <ul>
                {response.retrieved_documents.map((doc, index) => (
                  <li key={index}>
                    <strong>{doc.metadata?.title || 'Unknown'}</strong>: {doc.text.substring(0, 150)}...
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      <div className="history-section">
        <h2>Query History</h2>
        {queryHistory.length === 0 ? (
          <p className="no-history">No queries yet. Ask a question to get started!</p>
        ) : (
          <>
            <div className="history-list">
              {queryHistory.map((item, index) => (
                <div key={index} className="history-item">
                  <h4>Query {index + 1}</h4>
                  <div className="history-query">{item.query}</div>
                  <div className="history-answer"><strong>Answer:</strong> {item.answer}</div>
                  <div className="history-documents">
                    <strong>Sources:</strong>
                    {item.retrieved_documents && item.retrieved_documents.length > 0 ? (
                      item.retrieved_documents.map((doc, docIndex) => (
                        <div key={docIndex} className="history-document">
                          {doc.metadata?.title || 'Unknown'}: {doc.text.substring(0, 100)}...
                        </div>
                      ))
                    ) : (
                      <div>No sources retrieved</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <button className="clear-history" onClick={clearHistory}>Clear History</button>
          </>
        )}
      </div>
    </div>
  );
};

export default Query;