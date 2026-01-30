import type { Project } from '../../types';
import Button from '../common/Button';

interface StepContentProps {
  project: Project;
  onNext: () => void;
}

export default function StepContent({ project, onNext }: StepContentProps) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Review Study Content</h2>
      <div className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
        <h3 className="font-medium text-gray-700 mb-2">{project.title}</h3>
        <div className="prose prose-sm max-w-none text-gray-600 whitespace-pre-wrap">
          {project.content}
        </div>
      </div>
      <p className="text-sm text-gray-500 mb-4">
        {project.content.split(/\s+/).length} words
      </p>
      <Button onClick={onNext}>Continue to Outline</Button>
    </div>
  );
}
