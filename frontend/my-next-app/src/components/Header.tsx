"use client"; // This marks this component as a Client Component

import Link from 'next/link';
import { FC, useState, useEffect } from 'react';
import { login } from '../app/api'; // Import your login function

const Header: FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

  // Check if the user is logged in (by checking if access token exists in localStorage)
  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      setIsLoggedIn(true); // User is logged in
    } else {
      setIsLoggedIn(false); // User is not logged in
    }
  }, []);

  const handleLogin = async () => {
    // Trigger login (ensure you pass valid credentials)
    const success = await login('yourUsername', 'yourPassword'); // Replace with actual form data
    if (success) {
      setIsLoggedIn(true); // Update the UI to reflect login state
    }
  };

  const handleLogout = () => {
    // Remove tokens from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsLoggedIn(false); // Update the UI to reflect logout state
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
          <li>
            <Link href="/about" className="text-white hover:text-blue-300 transition-colors">
              About
            </Link>
          </li>
          <li>
            <Link href="/contact" className="text-white hover:text-blue-300 transition-colors">
              Contact
            </Link>
          </li>
          <li className="ml-auto">
            {isLoggedIn ? (
              <button
                onClick={handleLogout}
                className="text-white hover:text-blue-300 transition-colors"
              >
                Logout
              </button>
            ) : (
              <button
                onClick={handleLogin}
                className="text-white hover:text-blue-300 transition-colors"
              >
                Login
              </button>
            )}
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
