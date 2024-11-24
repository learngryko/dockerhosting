// src/hooks/useAuthRedirect.ts
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export const useAuthRedirect = (redirectPath: string) => {
  const router = useRouter();

  useEffect(() => {
    const isLoggedIn = !!localStorage.getItem('authToken'); // Replace with your auth check logic
    if (!isLoggedIn) {
      router.replace(`/login?redirect=${redirectPath}`);
    }
  }, [router, redirectPath]);
};
