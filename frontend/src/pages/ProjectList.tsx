import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listProjects, deleteProject } from '../api/projects';
import type { ProjectListItem } from '../types';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Button from '../components/common/Button';

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft',
  outline_ready: 'Outline Ready',
  script_ready: 'Script Ready',
  assets_ready: 'Assets Ready',
  video_ready: 'Video Ready',
};

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  outline_ready: 'bg-blue-100 text-blue-700',
  script_ready: 'bg-yellow-100 text-yellow-700',
  assets_ready: 'bg-purple-100 text-purple-700',
  video_ready: 'bg-green-100 text-green-700',
};

export default function ProjectList() {
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      setLoading(true);
      const data = await listProjects();
      setProjects(data);
    } catch {
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this project?')) return;
    try {
      await deleteProject(id);
      setProjects(projects.filter((p) => p.id !== id));
    } catch {
      setError('Failed to delete project');
    }
  }

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
        <Link
          to="/projects/new"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
        >
          New Project
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4">{error}</div>
      )}

      {projects.length === 0 ? (
        <div className="text-center py-16">
          <h2 className="text-lg font-medium text-gray-500 mb-2">No projects yet</h2>
          <p className="text-gray-400 mb-4">Create your first project to get started</p>
          <Link
            to="/projects/new"
            className="inline-block bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700"
          >
            Create Project
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <Link
                    to={`/projects/${project.id}`}
                    className="text-lg font-medium text-gray-900 hover:text-indigo-600"
                  >
                    {project.title}
                  </Link>
                  <div className="flex items-center gap-3 mt-1">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[project.status] || 'bg-gray-100 text-gray-700'}`}
                    >
                      {STATUS_LABELS[project.status] || project.status}
                    </span>
                    <span className="text-sm text-gray-400">
                      {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Link to={`/projects/${project.id}`}>
                    <Button variant="secondary" className="text-xs">Open</Button>
                  </Link>
                  <Button
                    variant="danger"
                    className="text-xs"
                    onClick={() => handleDelete(project.id)}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
