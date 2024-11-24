// src/app/projects/page.tsx
"use client";

import Header from '@/components/Header';
import { useAuthRedirect } from '@/hooks/useAuthRedirect';

const ProjectsPage = () => {
  const isCheckingAuth = useAuthRedirect('/projects'); // Redirect to login if not authenticated

  if (isCheckingAuth) {
    // Optionally render a loading spinner or return null
    return null;
  }

  return (
    <>
      <Header />
      <main>
        Projects:
      </main>
    </>
  );
};

export default ProjectsPage;

