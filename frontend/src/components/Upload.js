import React, { useState } from 'react';
import axios from 'axios';
import './Upload.css';

const Upload = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [hasErrors, setHasErrors] = useState(false);
  const [showResult, setShowResult] = useState(false);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      displayResult('Please select at least one PDF file.', false);
      return;
    }

    // Validate all files are PDFs
    for (let i = 0; i < files.length; i++) {
      if (!files[i].name.toLowerCase().endsWith('.pdf')) {
        displayResult('Only PDF files are accepted.', false);
        return;
      }
    }

    // Show loading spinner
    setLoading(true);
    setShowResult(false);

    const uploadResults = [];
    let uploadHasErrors = false;

    // Process each file
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        uploadResults.push({
          success: true,
          filename: file.name,
          data: response.data
        });
      } catch (error) {
        uploadHasErrors = true;
        uploadResults.push({
          success: false,
          filename: file.name,
          error: error.response?.data?.detail || 'Unknown error occurred'
        });
      }
    }

    // Display results
    setResults(uploadResults);
    setHasErrors(uploadHasErrors);
    setShowResult(true);
    setLoading(false);
    
    // Reset file input
    setFiles([]);
    document.getElementById('pdfFile').value = '';
  };

  const displayResult = (message, isSuccess) => {
    setResults([{ message }]);
    setHasErrors(!isSuccess);
    setShowResult(true);
  };

  const renderResults = () => {
    if (!showResult) return null;

    if (results.length === 1 && results[0].message) {
      // Simple message result
      return (
        <div className={hasErrors ? 'result error' : 'result success'}>
          {results[0].message}
        </div>
      );
    }

    if (results.length === 1) {
      // Single file result
      const result = results[0];
      if (result.success) {
        return (
          <div className="result success">
            <h3>Paper Uploaded Successfully!</h3>
            <p><strong>ID:</strong> {result.data.id}</p>
            <p><strong>Title:</strong> {result.data.title}</p>
            <p><strong>Author:</strong> {result.data.author || 'Unknown'}</p>
            <p><strong>Pages:</strong> {result.data.page_count || 'Unknown'}</p>
            <p>The paper has been processed and is now available for querying.</p>
          </div>
        );
      } else {
        return (
          <div className="result error">
            <h3>Error Uploading Paper</h3>
            <p>Error: {result.error}</p>
          </div>
        );
      }
    } else {
      // Multiple files results
      const successCount = results.filter(r => r.success).length;
      
      return (
        <div className={hasErrors ? 'result error' : 'result success'}>
          <h3>Upload Results ({results.length} files)</h3>
          <p>{successCount} of {results.length} files uploaded successfully.</p>
          <ul>
            {results.map((result, index) => (
              <li key={index}>
                {result.success ? '✅' : '❌'} <strong>{result.filename}</strong>: 
                {result.success 
                  ? ` Uploaded successfully (ID: ${result.data.id})` 
                  : ` ${result.error}`
                }
              </li>
            ))}
          </ul>
        </div>
      );
    }
  };

  return (
    <div>
      <h1>Upload Academic Papers (PDF)</h1>
      
      <p>Upload one or more PDF files to process and store in the PaperShelf system. Each paper will be processed, text extracted, and embeddings generated for later querying.</p>
      
      <form id="uploadForm" className="upload-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="pdfFile">Select PDF File(s):</label>
          <input 
            type="file" 
            id="pdfFile" 
            name="file" 
            accept=".pdf" 
            className="file-input" 
            multiple 
            required
            onChange={handleFileChange}
          />
        </div>
        <button type="submit" className="submit-btn">Upload Papers</button>
      </form>
      
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Processing your papers... This may take a moment.</p>
        </div>
      )}
      
      {renderResults()}
    </div>
  );
};

export default Upload;