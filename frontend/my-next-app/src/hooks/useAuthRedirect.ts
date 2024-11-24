import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export const useAuthRedirect = (redirectPath: string) => {
  const router = useRouter();
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    const isLoggedIn = !!localStorage.getItem('access_token');
    if (!isLoggedIn) {
      router.replace(`/login?redirect=${redirectPath}`);
    } else {
      setIsCheckingAuth(false); // Stop checking auth once confirmed logged in
    }
  }, [router, redirectPath]);

  return isCheckingAuth;
};
