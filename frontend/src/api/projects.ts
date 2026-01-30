import api from './client';
import type {
  Project,
  ProjectListItem,
  Outline,
  Script,
  AssetStatus,
  VideoStatus,
} from '../types';

export async function listProjects(): Promise<ProjectListItem[]> {
  const { data } = await api.get('/projects');
  return data;
}

export async function createProject(title: string, content: string): Promise<Project> {
  const { data } = await api.post('/projects', { title, content });
  return data;
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await api.get(`/projects/${id}`);
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/projects/${id}`);
}

export async function generateOutline(id: string): Promise<Outline> {
  const { data } = await api.post(`/projects/${id}/generate/outline`);
  return data;
}

export async function saveOutline(id: string, outline: Outline): Promise<Outline> {
  const { data } = await api.put(`/projects/${id}/outline`, outline);
  return data;
}

export async function generateScript(id: string): Promise<Script> {
  const { data } = await api.post(`/projects/${id}/generate/script`);
  return data;
}

export async function saveScript(id: string, script: Script): Promise<Script> {
  const { data } = await api.put(`/projects/${id}/script`, script);
  return data;
}

export async function startAssetGeneration(id: string): Promise<void> {
  await api.post(`/projects/${id}/generate/assets`);
}

export async function getAssetStatus(id: string): Promise<AssetStatus> {
  const { data } = await api.get(`/projects/${id}/generate/assets/status`);
  return data;
}

export async function startVideoGeneration(id: string): Promise<void> {
  await api.post(`/projects/${id}/generate/video`);
}

export async function getVideoStatus(id: string): Promise<VideoStatus> {
  const { data } = await api.get(`/projects/${id}/generate/video/status`);
  return data;
}
