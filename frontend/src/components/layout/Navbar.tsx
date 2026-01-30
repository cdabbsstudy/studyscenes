import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/projects" className="text-xl font-bold text-indigo-600">
          StudyScenes
        </Link>
        <Link
          to="/projects/new"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
        >
          New Project
        </Link>
      </div>
    </nav>
  );
}
