"use client";

import Link from 'next/link';
import { FC, useEffect } from 'react';
import useAuth from '../hooks/useAuth';

const Header: FC = () => {
  const { isLoggedIn, isTokenExpiring, timeLeft } = useAuth();

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
          <li>
            <Link href="/containers" className="text-white hover:text-blue-300 transition-colors">
              Containers
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
    </header>
  );
};

export default Header;
