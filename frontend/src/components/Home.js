import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Home.css';

const Home = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/sessions');
      setSessions(response.data.sessions || []);
      setError(null);
    } catch (err) {
      setError('Error loading sessions: ' + (err.response?.data?.detail || err.message));
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Welcome to PaperShelf</h1>
      <p className="description">An intelligent academic paper management and query system powered by RAG (Retrieval-Augmented Generation)</p>

      <div className="feature-cards">
        <div className="card">
          <div className="card-icon">📄</div>
          <h2>Upload Papers</h2>
          <p>Upload your academic papers (PDF format) to the system. We'll process them, extract text, and make them available for intelligent querying.</p>
          <Link to="/upload-page" className="btn">Upload Now</Link>
        </div>

        <div className="card">
          <div className="card-icon">🔍</div>
          <h2>Query Papers</h2>
          <p>Ask questions about your uploaded papers. Our RAG system will retrieve relevant information and generate accurate answers.</p>
          <Link to="/query-page" className="btn">Start Querying</Link>
        </div>
      </div>

      <div className="chat-history">
        <h2>Chat History</h2>
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading sessions...</p>
          </div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : sessions.length === 0 ? (
          <div className="no-sessions">No chat sessions found. Start a new chat by visiting the Query page.</div>
        ) : (
          <div className="session-list">
            {sessions.map(session => {
              const date = new Date(session.created_at);
              const formattedDate = date.toLocaleString();
              
              return (
                <div key={session.session_id} className="session-item">
                  <div className="session-info">
                    <div>Session ID: {session.session_id.substring(0, 8)}...</div>
                    <div className="session-date">{formattedDate}</div>
                  </div>
                  <div className="session-actions">
                    <a href={`/sessions/${session.session_id}`} target="_blank" rel="noopener noreferrer" className="session-btn view-btn">View</a>
                    <a href={`/sessions/${session.session_id}/export-pdf`} target="_blank" rel="noopener noreferrer" className="session-btn export-btn">Export PDF</a>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="footer">
        <p>PaperShelf - Your intelligent academic paper assistant</p>
      </div>
    </div>
  );
};

export default Home;