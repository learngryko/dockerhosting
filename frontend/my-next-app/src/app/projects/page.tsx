// src/app/projects/page.tsx
"use client";

import Header from '@/components/Header';
import { useAuthRedirect } from '@/hooks/useAuthRedirect';

const ProjectsPage = () => {
  useAuthRedirect('/projects'); // Redirect to login if not authenticated

  return (
    <>
      <Header />
      <main>
        projects:
      </main>
    </>
  );
};

export default ProjectsPage;
