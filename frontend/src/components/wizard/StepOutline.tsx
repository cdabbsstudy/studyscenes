import { useState } from 'react';
import type { Project, Outline, OutlineSection } from '../../types';
import { generateOutline, saveOutline } from '../../api/projects';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';

interface StepOutlineProps {
  project: Project;
  onUpdate: (project: Project) => void;
  onNext: () => void;
}

export default function StepOutline({ project, onUpdate, onNext }: StepOutlineProps) {
  const [outline, setOutline] = useState<Outline | null>(project.outline);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function handleGenerate() {
    try {
      setGenerating(true);
      setError('');
      const data = await generateOutline(project.id);
      setOutline(data);
      onUpdate({ ...project, outline: data, status: 'outline_ready' });
    } catch {
      setError('Failed to generate outline');
    } finally {
      setGenerating(false);
    }
  }

  async function handleSave() {
    if (!outline) return;
    try {
      setSaving(true);
      setError('');
      await saveOutline(project.id, outline);
      onUpdate({ ...project, outline, status: 'outline_ready' });
    } catch {
      setError('Failed to save outline');
    } finally {
      setSaving(false);
    }
  }

  function updateSection(index: number, updated: OutlineSection) {
    if (!outline) return;
    const sections = [...outline.sections];
    sections[index] = updated;
    setOutline({ sections });
  }

  function removeSection(index: number) {
    if (!outline) return;
    setOutline({ sections: outline.sections.filter((_, i) => i !== index) });
  }

  function addSection() {
    if (!outline) return;
    setOutline({
      sections: [...outline.sections, { title: 'New Section', key_points: ['Key point'] }],
    });
  }

  if (generating) return <LoadingSpinner message="Generating outline..." />;

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Outline</h2>

      {error && <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4">{error}</div>}

      {!outline ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">Generate an outline from your study content</p>
          <Button onClick={handleGenerate}>Generate Outline</Button>
        </div>
      ) : (
        <>
          <div className="space-y-4 mb-6">
            {outline.sections.map((section, i) => (
              <div key={i} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <input
                    value={section.title}
                    onChange={(e) =>
                      updateSection(i, { ...section, title: e.target.value })
                    }
                    className="font-medium text-gray-900 border-b border-transparent hover:border-gray-300 focus:border-indigo-500 focus:outline-none w-full"
                  />
                  <button
                    onClick={() => removeSection(i)}
                    className="text-gray-400 hover:text-red-500 ml-2 text-sm"
                  >
                    Remove
                  </button>
                </div>
                <ul className="space-y-1">
                  {section.key_points.map((point, j) => (
                    <li key={j} className="flex items-start gap-2">
                      <span className="text-gray-300 mt-0.5">-</span>
                      <input
                        value={point}
                        onChange={(e) => {
                          const points = [...section.key_points];
                          points[j] = e.target.value;
                          updateSection(i, { ...section, key_points: points });
                        }}
                        className="text-sm text-gray-600 border-b border-transparent hover:border-gray-300 focus:border-indigo-500 focus:outline-none flex-1"
                      />
                      <button
                        onClick={() => {
                          const points = section.key_points.filter((_, k) => k !== j);
                          updateSection(i, { ...section, key_points: points });
                        }}
                        className="text-gray-300 hover:text-red-400 text-xs"
                      >
                        x
                      </button>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() =>
                    updateSection(i, {
                      ...section,
                      key_points: [...section.key_points, 'New point'],
                    })
                  }
                  className="text-xs text-indigo-500 hover:text-indigo-700 mt-2"
                >
                  + Add point
                </button>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <Button onClick={addSection} variant="secondary">
              + Add Section
            </Button>
            <Button onClick={handleSave} loading={saving} variant="secondary">
              Save Changes
            </Button>
            <Button onClick={handleGenerate} variant="secondary">
              Regenerate
            </Button>
            <Button onClick={onNext}>Continue to Script</Button>
          </div>
        </>
      )}
    </div>
  );
}
