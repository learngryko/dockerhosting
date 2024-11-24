// src/app/login/page.tsx
"use client";

import LoginForm from '../../components/LoginForm';
import { useRouter, useSearchParams } from 'next/navigation';

const LoginPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirect') || '/'; // Default to home

  const handleLoginSuccess = () => {
    router.push(redirectTo); // Redirect to the intended page
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">Login</h1>
        <LoginForm onSuccess={handleLoginSuccess} redirectTo={redirectTo} />
      </div>
    </div>
  );
};

export default LoginPage;
