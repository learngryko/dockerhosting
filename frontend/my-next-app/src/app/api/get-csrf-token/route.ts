// /src/app/api/get-csrf-token/route.ts
import { NextResponse } from 'next/server';
import axios from 'axios';

export async function GET() {
  try {
    const response = await axios.get('http://django:8000/api/get-csrf-token/', {
      withCredentials: true,
    });
    const csrfToken = response.data.csrfToken;
    
    // Return the CSRF token in a JSON response
    return NextResponse.json({ csrfToken });
  } catch (error) {
    console.error('Error fetching CSRF token:', error);
    
    // Return an error response with a 500 status code
    return NextResponse.json({ error: 'Failed to fetch CSRF token' }, { status: 500 });
  }
}
