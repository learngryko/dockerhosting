// src/app/projects/page.tsx

"use client";

import Header from '@/components/Header';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuthRedirect } from '@/hooks/useAuthRedirect';
import config from '@/../config';
import ProjectConfigModal from '@/components/ProjectConfigModal';

const ProjectsPage = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<any | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const isCheckingAuth = useAuthRedirect('/projects'); // Redirect to login if not authenticated

  const API_URL = config.backendurl.endsWith('/') ? config.backendurl : `${config.backendurl}/`;
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
        
        setProjects(response.data.projects);
        setIsLoading(false);
      } catch (err: any) {
        console.error(err);
        setError('Failed to fetch projects');
        setIsLoading(false);
      }
    };

    fetchProjects();
  }, [isCheckingAuth, PROJECTS_ENDPOINT]);

  const handleRowClick = (project: any) => {
    setSelectedProject(project);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedProject(null);
  };

  if (isCheckingAuth || isLoading) {
    return <><Header /><div className="flex justify-center items-center h-screen">Loading...</div></>;
  }

  return (
    <>
      <Header />
      <main className="p-8">
        <h1 className="text-3xl font-bold mb-6">Projects</h1>
        {error && <div className="text-red-500 mb-4">{error}</div>}
        {projects.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
              <thead className="bg-gray-200">
                <tr>
                  <th className="py-3 px-6 text-left">Name</th>
                  <th className="py-3 px-6 text-left">Description</th>
                  <th className="py-3 px-6 text-left">Repository URL</th>
                  <th className="py-3 px-6 text-left">Build Path</th>
                  <th className="py-3 px-6 text-left">Owner</th>
                  <th className="py-3 px-6 text-left">Created At</th>
                  <th className="py-3 px-6 text-left">Updated At</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project) => (
                  <tr
                    key={project.id}
                    className="hover:bg-gray-100 cursor-pointer"
                    onClick={() => handleRowClick(project)}
                  >
                    <td className="py-4 px-6">{project.name}</td>
                    <td className="py-4 px-6">{project.description}</td>
                    <td className="py-4 px-6">
                      <a href={project.repository_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
                        Repository Link
                      </a>
                    </td>
                    <td className="py-4 px-6">{project.build_file_path}</td>
                    <td className="py-4 px-6">
                      {project.owner.username} ({project.owner.email})
                    </td>
                    <td className="py-4 px-6">{new Date(project.created_at).toLocaleString()}</td>
                    <td className="py-4 px-6">{new Date(project.updated_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-gray-600">No projects found</div>
        )}

        {/* Config Modal */}
        {isModalOpen && selectedProject && (
          <ProjectConfigModal 
            project={selectedProject} 
            onClose={handleCloseModal} 
            refreshProjects={() => {
              setIsLoading(true);
              setError(null);
              setProjects([]);
              axios.get(PROJECTS_ENDPOINT, {
                headers: {
                  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                },
              })
              .then(response => {
                setProjects(response.data.projects);
                setIsLoading(false);
              })
              .catch(err => {
                console.error(err);
                setError('Failed to fetch projects');
                setIsLoading(false);
              });
            }}
          />
        )}
      </main>
    </>
  );
};

export default ProjectsPage;
