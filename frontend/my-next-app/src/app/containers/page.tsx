// src/app/containers/page.tsx

"use client";

import { Container, Project } from "@/types/models";
import Header from "@/components/Header";
import { useState, useEffect } from "react";
import axios from "axios";
import config from "@/../config";
import { useAuthRedirect } from "@/hooks/useAuthRedirect";
import Link from "next/link";

export default function ContainersPage() {
  const [containers, setContainers] = useState<Container[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // For project selection
  const [projectOptions, setProjectOptions] = useState<Project[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [projectName, setProjectName] = useState<string>("");

  const [buildFilePath, setBuildFilePath] = useState<string>("Dockerfile");
  const [port, setPort] = useState<number>(8080);
  const [isCreating, setIsCreating] = useState<boolean>(false);

  // Track container actions (start/stop/delete)
  const [actionInProgress, setActionInProgress] = useState<string | null>(null); 

  const isCheckingAuth = useAuthRedirect("/containers");
  const API_URL = config.backendurl.endsWith("/")
    ? config.backendurl
    : `${config.backendurl}/`;
  const CONTAINERS_ENDPOINT = `${API_URL}containers/`;
  const CREATE_ENDPOINT = `${API_URL}containers/create/`;
  // New DELETE endpoint:
  const DELETE_ENDPOINT = `${API_URL}containers/delete/`;
  const START_ENDPOINT = (container_id: string) => `${API_URL}containers/${container_id}/start/`;
  const STOP_ENDPOINT = (container_id: string) => `${API_URL}containers/${container_id}/stop/`;
  const PROJECTS_ENDPOINT = `${API_URL}user/projects/`;

  useEffect(() => {
    if (isCheckingAuth) return;

    const fetchContainers = async () => {
      const accessToken = localStorage.getItem("access_token");
      if (!accessToken) {
        setError("No access token found");
        setIsLoading(false);
        return;
      }
      try {
        const res = await axios.get(CONTAINERS_ENDPOINT, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        setContainers(res.data.containers || []);
        setIsLoading(false);
      } catch (err: any) {
        console.error(err);
        setError("Failed to fetch containers");
        setIsLoading(false);
      }
    };

    // Fetch containers
    fetchContainers();
  }, [isCheckingAuth, CONTAINERS_ENDPOINT]);

  useEffect(() => {
    // Fetch all projects for the user
    const fetchProjects = async () => {
      const accessToken = localStorage.getItem("access_token");
      if (!accessToken) return;
      try {
        const res = await axios.get(PROJECTS_ENDPOINT, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        setProjectOptions(res.data.projects || []);
      } catch (err: any) {
        console.error(err);
      }
    };
    fetchProjects();
  }, [PROJECTS_ENDPOINT]);

  useEffect(() => {
    if (!searchTerm) {
      setFilteredProjects([]);
      return;
    }
    const matches = projectOptions.filter((p) =>
      p.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredProjects(matches);
  }, [searchTerm, projectOptions]);

  const handleCreate = async () => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      setError("No access token found");
      return;
    }
    setIsCreating(true);
    setError(null);
    try {
      await axios.post(
        CREATE_ENDPOINT,
        { project_name: projectName, build_file_path: buildFilePath, port },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      alert("Container created successfully.");
      setProjectName("");
      setBuildFilePath("Dockerfile");
      setPort(8080);

      // Reload containers
      const res = await axios.get(CONTAINERS_ENDPOINT, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setContainers(res.data.containers || []);
    } catch (err: any) {
      console.error(err);
      setError("Failed to create container");
    } finally {
      setIsCreating(false);
    }
  };

  const handleStart = async (containerId: string) => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      setError("No access token found");
      return;
    }
    setActionInProgress(containerId);
    try {
      const res = await axios.post(
        START_ENDPOINT(containerId),
        {},
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const newStatus = res.data.new_status || "running";
      // Update state
      setContainers((prev) =>
        prev.map((c) =>
          c.container_id === containerId ? { ...c, status: newStatus } : c
        )
      );
    } catch (err: any) {
      console.error(err);
      setError("Failed to start container");
    } finally {
      setActionInProgress(null);
    }
  };

  const handleStop = async (containerId: string) => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      setError("No access token found");
      return;
    }
    setActionInProgress(containerId);
    try {
      const res = await axios.post(
        STOP_ENDPOINT(containerId),
        {},
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const newStatus = res.data.new_status || "exited";
      // Update state
      setContainers((prev) =>
        prev.map((c) =>
          c.container_id === containerId ? { ...c, status: newStatus } : c
        )
      );
    } catch (err: any) {
      console.error(err);
      setError("Failed to stop container");
    } finally {
      setActionInProgress(null);
    }
  };

  const handleDelete = async (containerId: string) => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      setError("No access token found");
      return;
    }
    setActionInProgress(containerId);
    try {
      await axios.delete(DELETE_ENDPOINT, {
        headers: { Authorization: `Bearer ${accessToken}` },
        // Pass container_id in the data of the DELETE request.
        data: { container_id: containerId },
      });
      // Remove the deleted container from the state.
      setContainers((prev) =>
        prev.filter((c) => c.container_id !== containerId)
      );
    } catch (err: any) {
      console.error(err);
      setError("Failed to delete container");
    } finally {
      setActionInProgress(null);
    }
  };

  if (isCheckingAuth || isLoading) {
    return (
      <>
        <Header />
        <div className="flex justify-center items-center h-screen">Loading...</div>
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="p-8">
        <h1 className="text-3xl font-bold mb-6">Containers</h1>
        {error && <div className="text-red-500 mb-4">{error}</div>}

        <div className="border p-4 rounded-md mb-6">
          <h2 className="text-xl font-semibold mb-2">Create New Container</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Select Project</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-2 border rounded mb-2"
                placeholder="Search projects..."
              />
              {filteredProjects.length > 0 && (
                <ul className="border rounded mt-2 max-h-40 overflow-y-auto">
                  {filteredProjects.map((p) => (
                    <li
                      key={p.id}
                      className="p-2 hover:bg-gray-200 cursor-pointer"
                      onClick={() => {
                        setProjectName(p.name);
                        setFilteredProjects([]);
                        setSearchTerm(p.name);
                      }}
                    >
                      {p.name}
                    </li>
                  ))}
                </ul>
              )}
              {projectName && (
                <div className="mt-2">
                  Selected Project: <span className="font-bold">{projectName}</span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Build File Path</label>
              <input
                type="text"
                value={buildFilePath}
                onChange={(e) => setBuildFilePath(e.target.value)}
                className="w-full p-2 border rounded"
                placeholder="e.g. Dockerfile"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Port</label>
              <input
                type="number"
                value={port}
                onChange={(e) => setPort(Number(e.target.value))}
                className="w-full p-2 border rounded"
                placeholder="8080"
              />
            </div>
            <button
              onClick={handleCreate}
              disabled={isCreating || !projectName}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {isCreating ? "Creating..." : "Create Container"}
            </button>
          </div>
        </div>

        {containers.length > 0 ? (
          <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
            <thead className="bg-gray-200">
              <tr>
                <th className="py-3 px-6 text-left">Container ID</th>
                <th className="py-3 px-6 text-left">Project</th>
                <th className="py-3 px-6 text-left">Status</th>
                <th className="py-3 px-6 text-left">Port</th>
                <th className="py-3 px-6 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {containers.map((c) => {
                const isRunning = c.status === "running";
                const isActionDisabled = actionInProgress === c.container_id;
                const serviceUrl = `https://${config.host_ip}/proxy/${c.project}_container`;
                return (
                  <tr key={c.container_id} className="hover:bg-gray-100">
                    <td>{c.container_id}</td>
                    <td>{c.project.name}</td>
                    <td>{c.status}</td>
                    <td>{c.port}</td>
                    <td className="space-x-2">
                      {/* Start / Stop Buttons */}
                      {!isRunning && (
                        <button
                          onClick={() => handleStart(c.container_id)}
                          disabled={isActionDisabled}
                          className="bg-green-500 text-white px-2 py-1 rounded hover:bg-green-600 disabled:opacity-50"
                        >
                          {isActionDisabled ? "Starting..." : "Start"}
                        </button>
                      )}
                      {isRunning && (
                        <button
                          onClick={() => handleStop(c.container_id)}
                          disabled={isActionDisabled}
                          className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 disabled:opacity-50"
                        >
                          {isActionDisabled ? "Stopping..." : "Stop"}
                        </button>
                      )}

                      {/* Delete Button */}
                      <button
                        onClick={() => handleDelete(c.container_id)}
                        disabled={isActionDisabled}
                        className="bg-gray-700 text-white px-2 py-1 rounded hover:bg-gray-800 disabled:opacity-50"
                      >
                        {isActionDisabled ? "Deleting..." : "Delete"}
                      </button>

                      {/* Link to service (only if running) */}
                      {isRunning && (
                        <a
                          href={serviceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                        >
                          Open Service
                        </a>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div>No containers found</div>
        )}
      </main>
    </>
  );
}
