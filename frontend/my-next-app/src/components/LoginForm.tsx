// src/components/LoginForm.tsx
import { useState } from 'react';
import { login } from '../app/api'; // Import the login function
import { useRouter } from 'next/navigation';

interface LoginFormProps {
  onSuccess: () => void;
  redirectTo?: string; // Optional redirect target
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, redirectTo }) => {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); // Clear any previous errors

    try {
      const success = await login(username, password); // Assume login is an async function that returns a boolean

      if (success) {
        console.log('Login successful!');
        onSuccess();
        if (redirectTo) {
          router.push(redirectTo); // Redirect to the intended page
        }
      } else {
        setError('Login failed, please try again.');
      }
    } catch (err) {
      console.error('An error occurred during login:', err);
      setError('An unexpected error occurred. Please try again.');
    }
  };

  return (
    <form onSubmit={handleLogin} className="space-y-4">
      <div>
        <label htmlFor="username" className="block text-sm font-medium text-gray-700">
          Username
        </label>
        <input
          type="text"
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="mt-1 block w-full p-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="mt-1 block w-full p-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <button
        type="submit"
        className="w-full py-3 mt-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
      >
        Login
      </button>
      {error && (
        <p className="mt-2 text-center text-sm text-red-600">
          {error}
        </p>
      )}
    </form>
  );
};

export default LoginForm;


