"use client";

import LoginForm from '../../components/LoginForm';
import { useRouter, useSearchParams } from 'next/navigation';
import useAuth from '@/hooks/useAuth';
import Header from '@/components/Header';

const LoginPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirect') || '/'; // Default to home if no redirect is provided
  const isLoggedIn = useAuth();

  const handleLoginSuccess = () => {
    router.push(redirectTo); // Redirect to the intended page
  };

  if (isLoggedIn) {
    return (
      <>
      <Header />
      <div className="min-h-screen bg-gray-100 flex justify-center items-center">
        <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">You are already logged in</h1>
          <button 
            onClick={() => router.push(redirectTo)} 
            className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600"
          >
            Go back
          </button>
        </div>
      </div>
      </>
    );
  }

  return (
    <>
    <Header />
    <div className="min-h-screen bg-gray-100 flex justify-center items-center">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">Login</h1>
        <LoginForm onSuccess={handleLoginSuccess} />
      </div>
    </div>
    </>
  );
};

export default LoginPage;
