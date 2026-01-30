import { useState } from 'react';
import type { Project, Script, ScriptScene } from '../../types';
import { generateScript, saveScript } from '../../api/projects';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';

interface StepScriptProps {
  project: Project;
  onUpdate: (project: Project) => void;
  onNext: () => void;
}

export default function StepScript({ project, onUpdate, onNext }: StepScriptProps) {
  const [script, setScript] = useState<Script | null>(project.script);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function handleGenerate() {
    try {
      setGenerating(true);
      setError('');
      const data = await generateScript(project.id);
      setScript(data);
      onUpdate({ ...project, script: data, status: 'script_ready' });
    } catch {
      setError('Failed to generate script');
    } finally {
      setGenerating(false);
    }
  }

  async function handleSave() {
    if (!script) return;
    try {
      setSaving(true);
      setError('');
      await saveScript(project.id, script);
      onUpdate({ ...project, script, status: 'script_ready' });
    } catch {
      setError('Failed to save script');
    } finally {
      setSaving(false);
    }
  }

  function updateScene(index: number, updated: ScriptScene) {
    if (!script) return;
    const scenes = [...script.scenes];
    scenes[index] = updated;
    setScript({ scenes });
  }

  if (generating) return <LoadingSpinner message="Generating script..." />;

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Script</h2>

      {error && <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4">{error}</div>}

      {!script ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">Generate a narration script from your outline</p>
          <Button onClick={handleGenerate}>Generate Script</Button>
        </div>
      ) : (
        <>
          <div className="space-y-4 mb-6">
            {script.scenes.map((scene, i) => (
              <div key={i} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="mb-3">
                  <label className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Scene {i + 1} Title
                  </label>
                  <input
                    value={scene.title}
                    onChange={(e) => updateScene(i, { ...scene, title: e.target.value })}
                    className="w-full font-medium text-gray-900 border-b border-gray-200 focus:border-indigo-500 focus:outline-none mt-1 pb-1"
                  />
                </div>
                <div className="mb-3">
                  <label className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Narration
                  </label>
                  <textarea
                    value={scene.narration}
                    onChange={(e) => updateScene(i, { ...scene, narration: e.target.value })}
                    rows={3}
                    className="w-full text-sm text-gray-600 border border-gray-200 rounded px-2 py-1 focus:border-indigo-500 focus:outline-none mt-1 resize-y"
                  />
                  <p className="text-xs text-gray-400">
                    {scene.narration.split(/\s+/).length} words (~
                    {Math.ceil((scene.narration.split(/\s+/).length / 150) * 60)}s)
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Visual Description
                  </label>
                  <textarea
                    value={scene.visual_desc}
                    onChange={(e) => updateScene(i, { ...scene, visual_desc: e.target.value })}
                    rows={2}
                    className="w-full text-sm text-gray-600 border border-gray-200 rounded px-2 py-1 focus:border-indigo-500 focus:outline-none mt-1 resize-y"
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <Button onClick={handleSave} loading={saving} variant="secondary">
              Save Changes
            </Button>
            <Button onClick={handleGenerate} variant="secondary">
              Regenerate
            </Button>
            <Button onClick={onNext}>Continue to Generate</Button>
          </div>
        </>
      )}
    </div>
  );
}
