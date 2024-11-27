"use client";

import Link from 'next/link';
import { FC } from 'react';
import useAuth from '../hooks/useAuth';

const Header: FC = () => {
  const { isLoggedIn, isTokenExpiring, timeLeft } = useAuth();

  // Format time left into a readable format (e.g., minutes and seconds)
  const formatTimeLeft = (time: number) => {
    const minutes = Math.floor(time / 1000 / 60);
    const seconds = Math.floor((time / 1000) % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
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
            <Link href="/projects" className="text-white hover:text-blue-300 transition-colors">
              Projects
            </Link>
          </li>
          <li className="ml-auto">
            {isLoggedIn ? (
              <Link href="/logout" className="text-white hover:text-blue-300 transition-colors">
                Logout
              </Link>
            ) : (
              <Link href="/login" className="text-white hover:text-blue-300 transition-colors">
                Login
              </Link>
            )}
          </li>
        </ul>
      </nav>

      {/* Show timer if the token is expiring */}
      {isTokenExpiring && (
        <div className="text-yellow-300 text-center mt-2">
          <p>Your session will expire in {formatTimeLeft(timeLeft)}. Please save your work.</p>
        </div>
      )}
    </header>
  );
};

export default Header;
