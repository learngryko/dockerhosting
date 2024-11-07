// src/app/login/page.tsx
"use client"; // Ensures this component runs on the client side

import LoginForm from '../../components/LoginForm';
import { useRouter } from 'next/navigation';

const LoginPage = () => {
  const router = useRouter();

  const handleLoginSuccess = () => {
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">Login</h1>
        <LoginForm onSuccess={handleLoginSuccess} />
      </div>
    </div>
  );
};

export default LoginPage;
