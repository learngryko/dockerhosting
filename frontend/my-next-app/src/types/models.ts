// Interfaces for the Django models

export interface Project {
    id: number;
    name: string;
    description: string;
    repository_url: string;
    build_file_path: string;
    created_at: string; // Date string (ISO format)
    updated_at: string; // Date string (ISO format)
  }
  
  export interface Environment {
    id: number;
    project: Project; // Reference to Project model
    env_vars: Record<string, any>; // You can customize based on your env var structure
    resource_limits: Record<string, string>; // E.g., { cpu: "2", memory: "512m" }
    created_at: string; // Date string (ISO format)
    updated_at: string; // Date string (ISO format)
  }
  
  export interface File {
    id: number;
    project: Project; // Reference to Project model
    file_path: string;
    content: string;
    extension: string;
    to_host: boolean;
    created_at: string; // Date string (ISO format)
    updated_at: string; // Date string (ISO format)
  }
  
  export interface Container {
    id: number;
    project: Project; // Reference to Project model
    container_id: string;
    status: string; // E.g., 'running', 'stopped'
    port: number;
    created_at: string; // Date string (ISO format)
    updated_at: string; // Date string (ISO format)
  }
  