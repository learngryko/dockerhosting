"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';

const LogoutPage = () => {
  const router = useRouter();

  useEffect(() => {
    // Remove tokens or authentication details from localStorage or wherever you store them
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Optionally, you could reset the state on a global level here if needed.

    setTimeout(() => {
      router.push('/'); // Redirect to home page after logout
    }, 1000); // Redirect after 1 seconds
  }, [router]);

  return (
    <>
    <Header />
    <div className="min-h-screen bg-gray-100 flex justify-center items-center">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Logging you out...</h1>
        <p className="text-gray-600">You will be redirected shortly...</p>
      </div>
    </div>
    </>
  );
};

export default LogoutPage;
