"use client";

import Link from 'next/link';
import { FC, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const Header: FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const router = useRouter();

  useEffect(() => {
    const checkLoginStatus = () => {
      const accessToken = localStorage.getItem('access_token');
      setIsLoggedIn(!!accessToken);
    };

    checkLoginStatus();
    window.addEventListener("storage", checkLoginStatus); // Listen for localStorage changes

    return () => window.removeEventListener("storage", checkLoginStatus); // Cleanup listener
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsLoggedIn(false);
    router.push('/login'); // Redirect to login page after logout
  };

  return (
    <header className="bg-blue-500 py-4 shadow-md">
      <nav>
        <ul className="flex justify-between items-center px-8">
          <li>
            <Link href="/" className="text-white hover:text-blue-300 transition-colors">
              Home
            </Link>
          </li>
          <li
          <li className="ml-auto">
            {isLoggedIn ? (
              <button
                onClick={handleLogout}
                className="text-white hover:text-blue-300 transition-colors"
              >
                Logout
              </button>
            ) : (
              <Link href="/login" className="text-white hover:text-blue-300 transition-colors">
                Login
              </Link>
            )}
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
