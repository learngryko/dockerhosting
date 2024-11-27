"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import { logout } from '@/app/api';

const LogoutPage = () => {
  const router = useRouter();

  useEffect(() => {
    const performLogout = async () => {
      const success = await logout(); // Call the logout function from api.ts
      if (success) {
        // Redirect to home page after successful logout
        setTimeout(() => {
          router.push('/');
        }, 1500); // Redirect after 1 second
      } else {
        console.error('Logout failed.');
      }
    };

    performLogout();
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
