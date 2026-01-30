import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProject } from '../api/projects';
import Button from '../components/common/Button';

export default function NewProject() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('Title and content are required');
      return;
    }
    try {
      setLoading(true);
      setError('');
      const project = await createProject(title.trim(), content.trim());
      navigate(`/projects/${project.id}`);
    } catch {
      setError('Failed to create project');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">New Project</h1>

      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Project Title
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Biology Chapter 5 Review"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
            Study Content
          </label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your study notes, textbook content, or any material you want to turn into a video..."
            rows={12}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-y"
          />
          <p className="text-xs text-gray-400 mt-1">
            {content.length} characters
          </p>
        </div>

        <div className="flex gap-3">
          <Button type="submit" loading={loading}>
            Create Project
          </Button>
          <Button type="button" variant="secondary" onClick={() => navigate('/projects')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
