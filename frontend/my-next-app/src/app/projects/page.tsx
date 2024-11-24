"use client";

import Header from '@/components/Header';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuthRedirect } from '@/hooks/useAuthRedirect';
import config from '@/../config';

const ProjectsPage = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const isCheckingAuth = useAuthRedirect('/projects'); // Redirect to login if not authenticated

  // Define the API endpoint
  const API_URL = config.backendurl;
  const PROJECTS_ENDPOINT = `${API_URL}user/projects/`; 

  useEffect(() => {
    if (isCheckingAuth) {
      return;
    }

    const fetchProjects = async () => {
      const accessToken = localStorage.getItem('access_token');
      if (!accessToken) {
        setError('No access token found');
        setIsLoading(false);
        return;
      }

      try {
        const response = await axios.get(PROJECTS_ENDPOINT, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        
        // Assuming the data is structured as shown above
        setProjects(response.data.projects);
        setIsLoading(false);
      } catch (err: any) {
        console.error(err);
        setError('Failed to fetch projects');
        setIsLoading(false);
      }
    };

    fetchProjects();
  }, [isCheckingAuth]);

  if (isCheckingAuth || isLoading) {
    // Optionally render a loading spinner or return null
    return <div>Loading...</div>;
  }

  return (
    <>
      <Header />
      <main>
        <h1>Projects:</h1>
        {error && <div style={{ color: 'red' }}>{error}</div>}
        {projects.length > 0 ? (
          <ul>
            {projects.map((project) => (
              <li key={project.id}>
                <h3>{project.name}</h3>
                <p>{project.description}</p>
                <a href={project.repository_url} target="_blank" rel="noopener noreferrer">
                  Repository URL
                </a>
                <p><strong>Build Path:</strong> {project.build_file_path}</p>
                <p><strong>Owner:</strong> {project.owner.username} ({project.owner.email})</p>
                <p><strong>Created At:</strong> {new Date(project.created_at).toLocaleString()}</p>
                <p><strong>Updated At:</strong> {new Date(project.updated_at).toLocaleString()}</p>
              </li>
            ))}
          </ul>
        ) : (
          <div>No projects found</div>
        )}
      </main>
    </>
  );
};

export default ProjectsPage;
