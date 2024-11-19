// src/components/PingTest/PingTest.tsx

import React, { useState } from 'react';
import api from '../../services/api'; // Make sure you have your axios setup here

const PingTest: React.FC = () => {
  const [pingResponse, setPingResponse] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const testPing = async () => {
    try {
      const response = await api.get('/ping'); // Assuming the API has a `/ping` endpoint
      setPingResponse(response.data.message);
    } catch (err: any) {
      setError('Failed to ping the server');
      console.error(err);
    }
  };

  return (
    <div>
      <h2>Ping Test</h2>
      <button onClick={testPing}>Ping Server</button>
      {pingResponse && <p>Response: {pingResponse}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default PingTest;
