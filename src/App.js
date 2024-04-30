import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [article, setArticle] = useState('');
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');

  // Handle input changes in the article text
  const handleInputChange = (event) => {
    setArticle(event.target.value);
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      // Send a POST request to the Flask backend
      const response = await axios.post('/summarize', { text: article });

      if (response.data && response.data.summary) {
        // Set the summary and clear any error
        setSummary(response.data.summary);
        setError('');
      } else {
        // Set an error message if no summary is returned
        setError('Error: Unable to generate summary.');
      }
    } catch (err) {
      // Set an error message if there was an issue with the request
      setError('Error: Unable to connect to the server.');
    }
  };

  return (
    <div className="app">
      <h1>Text Summarizer</h1>
      
      {/* Form to enter text */}
      <form onSubmit={handleSubmit}>
        <textarea
          value={article}
          onChange={handleInputChange}
          placeholder="Enter text to summarize..."
          rows="20"
          cols="80"
          required
        />
        <button type="submit">Summarize</button>
      </form>

      {/* Display the summary if available */}
      {summary && (
        <div className="summary">
          <h2>Summary</h2>
          <p>{summary}</p>
        </div>
      )}

      {/* Display error messages if any */}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default App;
