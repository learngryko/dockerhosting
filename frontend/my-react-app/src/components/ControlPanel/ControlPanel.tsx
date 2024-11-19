// src/components/ControlPanel/ControlPanel.tsx

import React, { useState } from 'react';
import {
  cloneRepository,
  listFiles,
  getFileContent,
  setToHostFlag,
  createContainer,
  listContainers,
  startContainer,
  stopContainer,
} from '../../services/apiActions';

const ControlPanel: React.FC = () => {
  const [projectName, setProjectName] = useState('');
  const [filePath, setFilePath] = useState('');
  const [flagValue, setFlagValue] = useState('');
  const [containerId, setContainerId] = useState('');

  const handleCloneRepo = async () => {
    try {
      const response = await cloneRepository();
      console.log('Clone Repo Response:', response.data);
    } catch (error) {
      console.error('Error cloning repository:', error);
    }
  };

  const handleListFiles = async () => {
    try {
      const response = await listFiles(projectName);
      console.log('List Files Response:', response.data);
    } catch (error) {
      console.error('Error listing files:', error);
    }
  };

  const handleFileContent = async () => {
    try {
      const response = await getFileContent(projectName, filePath);
      console.log('File Content Response:', response.data);
    } catch (error) {
      console.error('Error getting file content:', error);
    }
  };

  const handleSetToHostFlag = async () => {
    try {
      const response = await setToHostFlag(projectName, flagValue);
      console.log('Set To Host Flag Response:', response.data);
    } catch (error) {
      console.error('Error setting to host flag:', error);
    }
  };

  const handleCreateContainer = async () => {
    try {
      const response = await createContainer();
      console.log('Create Container Response:', response.data);
    } catch (error) {
      console.error('Error creating container:', error);
    }
  };

  const handleListContainers = async () => {
    try {
      const response = await listContainers(projectName);
      console.log('List Containers Response:', response.data);
    } catch (error) {
      console.error('Error listing containers:', error);
    }
  };

  const handleStartContainer = async () => {
    try {
      const response = await startContainer(containerId);
      console.log('Start Container Response:', response.data);
    } catch (error) {
      console.error('Error starting container:', error);
    }
  };

  const handleStopContainer = async () => {
    try {
      const response = await stopContainer(containerId);
      console.log('Stop Container Response:', response.data);
    } catch (error) {
      console.error('Error stopping container:', error);
    }
  };

  return (
    <div className="control-panel">
      <h2>Project Control Panel</h2>

      <button onClick={handleCloneRepo}>Clone Repository</button>
      
      <div>
        <input
          type="text"
          placeholder="Project Name"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
        />
        <button onClick={handleListFiles}>List Files</button>
      </div>

      <div>
        <input
          type="text"
          placeholder="File Path"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
        />
        <button onClick={handleFileContent}>Get File Content</button>
      </div>

      <div>
        <input
          type="text"
          placeholder="Flag Value"
          value={flagValue}
          onChange={(e) => setFlagValue(e.target.value)}
        />
        <button onClick={handleSetToHostFlag}>Set To Host Flag</button>
      </div>

      <button onClick={handleCreateContainer}>Create Container</button>

      <div>
        <button onClick={handleListContainers}>List Containers</button>
      </div>

      <div>
        <input
          type="text"
          placeholder="Container ID"
          value={containerId}
          onChange={(e) => setContainerId(e.target.value)}
        />
        <button onClick={handleStartContainer}>Start Container</button>
        <button onClick={handleStopContainer}>Stop Container</button>
      </div>
    </div>
  );
};

export default ControlPanel;
