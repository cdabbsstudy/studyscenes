import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getProject } from '../api/projects';
import type { Project } from '../types';
import LoadingSpinner from '../components/common/LoadingSpinner';
import WizardStepper from '../components/wizard/WizardStepper';
import StepContent from '../components/wizard/StepContent';
import StepOutline from '../components/wizard/StepOutline';
import StepScript from '../components/wizard/StepScript';
import StepGenerate from '../components/wizard/StepGenerate';
import StepPreview from '../components/wizard/StepPreview';

function statusToStep(status: string): number {
  switch (status) {
    case 'draft':
      return 0;
    case 'outline_ready':
      return 1;
    case 'script_ready':
      return 2;
    case 'assets_ready':
      return 3;
    case 'video_ready':
      return 4;
    default:
      return 0;
  }
}

export default function ProjectWizard() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    loadProject();
  }, [id]);

  async function loadProject() {
    try {
      setLoading(true);
      const data = await getProject(id!);
      setProject(data);
      setStep(statusToStep(data.status));
    } catch {
      setError('Failed to load project');
    } finally {
      setLoading(false);
    }
  }

  function handleUpdate(updated: Project) {
    setProject(updated);
  }

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg">{error}</div>;
  if (!project) return null;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">{project.title}</h1>
      <WizardStepper currentStep={step} />

      {step === 0 && <StepContent project={project} onNext={() => setStep(1)} />}
      {step === 1 && (
        <StepOutline
          project={project}
          onUpdate={handleUpdate}
          onNext={() => setStep(2)}
        />
      )}
      {step === 2 && (
        <StepScript
          project={project}
          onUpdate={handleUpdate}
          onNext={() => setStep(3)}
        />
      )}
      {step === 3 && (
        <StepGenerate
          project={project}
          onUpdate={handleUpdate}
          onNext={() => {
            loadProject();
            setStep(4);
          }}
        />
      )}
      {step === 4 && <StepPreview project={project} />}
    </div>
  );
}
