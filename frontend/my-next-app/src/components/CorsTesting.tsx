// /src/components/CorsTesting.tsx
"use client";

import React, { useState } from 'react';
import axios from 'axios';

function CorsTesting() {
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getCsrfToken = async () => {
    try {
      const response = await axios.get('/api/get-csrf-token/', {
        withCredentials: true,
      });
      setCsrfToken(response.data.csrfToken);
      setError(null);
    } catch (err) {
      setError('CORS error or another issue. Check console for details.');
      console.error(err);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Test Django CORS</h2>
      <button onClick={getCsrfToken}>Get CSRF Token</button>
      {csrfToken && <p>CSRF Token: {csrfToken}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default CorsTesting;
