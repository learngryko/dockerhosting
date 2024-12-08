// components/ProjectConfigModal.tsx

"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import config from '@/../config';
import { XMarkIcon } from '@heroicons/react/24/solid';
import FileTree from './FileTree';
import { buildFileTree, TreeNode, FileItem } from '@/utils/buildFileTree';

interface ProjectConfigModalProps {
  project: any;
  onClose: () => void;
  refreshProjects: () => void;
}

const ProjectConfigModal: React.FC<ProjectConfigModalProps> = ({ project, onClose, refreshProjects }) => {
  const [fileTree, setFileTree] = useState<TreeNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isFetchingFiles, setIsFetchingFiles] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>(''); // For optional search functionality

  const API_URL = config.backendurl.endsWith('/') ? config.backendurl : `${config.backendurl}/`;
  const FILES_ENDPOINT = `${API_URL}projects/${encodeURIComponent(project.name)}/files/`;

  useEffect(() => {
    const fetchFiles = async () => {
      const accessToken = localStorage.getItem('access_token');
      if (!accessToken) {
        setError('No access token found');
        setIsFetchingFiles(false);
        return;
      }

      try {
        const response = await axios.get(FILES_ENDPOINT, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        const tree = buildFileTree(response.data.files);
        setFileTree(tree);
        setIsFetchingFiles(false);
      } catch (err: any) {
        console.error(err);
        setError('Failed to fetch files');
        setIsFetchingFiles(false);
      }
    };

    fetchFiles();
  }, [FILES_ENDPOINT]);

  const handleFileSelect = async (filePath: string) => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      setError('No access token found');
      return;
    }

    try {
      const response = await axios.get(`${FILES_ENDPOINT}${encodeURIComponent(filePath)}/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      setSelectedFile(filePath);
      setFileContent(response.data.content);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError('Failed to fetch file content');
    }
  };

  const handleSave = async () => {
    if (!selectedFile) return;

    setIsSaving(true);
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      setError('No access token found');
      setIsSaving(false);
      return;
    }

    try {
      await axios.post(
        `${FILES_ENDPOINT}${encodeURIComponent(selectedFile)}/`,
        { content: fileContent },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      setIsSaving(false);
      alert('File updated successfully.');
      onClose();
      refreshProjects();
    } catch (err: any) {
      console.error(err);
      setError('Failed to save file');
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white w-11/12 md:w-3/4 lg:w-1/2 h-5/6 rounded-lg shadow-lg overflow-y-auto relative">
        <button 
          onClick={onClose} 
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
          aria-label="Close Modal"
        >
          <XMarkIcon className="h-6 w-6" />
        </button>
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-4">Project: {project.name}</h2>
          {error && <div className="text-red-500 mb-4">{error}</div>}
          {isFetchingFiles ? (
            <div className="flex justify-center items-center h-64">
              <svg className="animate-spin h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
            </div>
          ) : (
            <div className="flex flex-col md:flex-row">
              {/* Files Tree */}
              <div className="md:w-1/3 mb-4 md:mb-0">
                <h3 className="text-xl font-semibold mb-2">Files</h3>
                <div className="border rounded-lg p-2 max-h-64 overflow-y-auto">
                  {/* Optional Search Input */}
                  {/* Uncomment the following block if you implement search functionality */}
                  {/* 
                  <input
                    type="text"
                    placeholder="Search files..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full p-2 border rounded mb-4"
                  />
                  */}
                  {fileTree.length > 0 ? (
                    fileTree.map((node) => (
                      <FileTree
                        key={node.name}
                        node={node}
                        onFileSelect={handleFileSelect}
                        currentPath=""
                      />
                    ))
                  ) : (
                    <div className="text-gray-600">No files found.</div>
                  )}
                </div>
              </div>

              {/* File Content Editor */}
              <div className="md:w-2/3 md:pl-4">
                {selectedFile ? (
                  <>
                    <h3 className="text-xl font-semibold mb-2">Editing: {selectedFile}</h3>
                    <textarea 
                      className="w-full h-64 p-2 border rounded-lg resize-none"
                      value={fileContent}
                      onChange={(e) => setFileContent(e.target.value)}
                    />
                    <button 
                      onClick={handleSave} 
                      className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
                      disabled={isSaving}
                    >
                      {isSaving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </>
                ) : (
                  <div className="text-gray-500">Select a file to view and edit its content.</div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectConfigModal;
