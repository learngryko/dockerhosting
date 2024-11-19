// src/services/apiActions.ts

import api from './api';

export const cloneRepository = async () => {
  return await api.post('clone-repo/');
};

export const listFiles = async (projectName: string) => {
  return await api.get(`projects/${projectName}/files/`);
};

export const getFileContent = async (projectName: string, filePath: string) => {
  return await api.get(`projects/${projectName}/files/${filePath}/`);
};

export const setToHostFlag = async (projectName: string, flagValue: string) => {
  return await api.patch(`project/${projectName}/set-to-host/${flagValue}/`);
};

export const createContainer = async () => {
  return await api.post('create-container/');
};

export const listContainers = async (projectName: string) => {
  return await api.get(`containers/${projectName}/`);
};

export const startContainer = async (containerId: string) => {
  return await api.post(`containers/${containerId}/start/`);
};

export const stopContainer = async (containerId: string) => {
  return await api.post(`containers/${containerId}/stop/`);
};
