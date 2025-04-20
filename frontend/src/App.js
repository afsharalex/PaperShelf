import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Home from './components/Home';
import Upload from './components/Upload';
import Query from './components/Query';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <div className="app">
        <div className="container">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload-page" element={<Upload />} />
            <Route path="/query-page" element={<Query />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;