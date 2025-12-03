import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Submission from './pages/Submission';
import JobView from './pages/JobView';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Submission />} />
          <Route path="/job/:jobId" element={<JobView />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
