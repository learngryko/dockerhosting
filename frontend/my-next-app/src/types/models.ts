// Updated Interfaces for Django models

export interface User {
  id: number;
  username: string;
  email: string; // Add other fields as needed
}

export interface Project {
  id: number;
  name: string;
  description: string;
  repository_url: string;
  build_file_path: string;
  created_at: string; // ISO format
  updated_at: string; // ISO format
  owner: User; // Reference to the User model
}

export interface Environment {
  id: number;
  project: Project; // Reference to the Project model
  env_vars: Record<string, any>; // Environment variables
  resource_limits: Record<string, string>; // e.g., { cpu: "2", memory: "512m" }
  created_at: string; // ISO format
  updated_at: string; // ISO format
}

export interface File {
  id: number;
  project: Project; // Reference to the Project model
  file_path: string;
  content: string;
  extension: string;
  to_host: boolean;
  created_at: string; // ISO format
  updated_at: string; // ISO format
}

export interface Container {
  id: number;
  project: Project; // Reference to the Project model
  container_id: string;
  status: string; // e.g., 'running', 'stopped'
  port: number;
  created_at: string; // ISO format
  updated_at: string; // ISO format
}
