import { useState, useEffect, useRef, useCallback } from 'react';
import type { Project } from '../../types';
import {
  startAssetGeneration,
  getAssetStatus,
  startVideoGeneration,
  getVideoStatus,
} from '../../api/projects';
import Button from '../common/Button';
import ProgressBar from '../common/ProgressBar';

interface StepGenerateProps {
  project: Project;
  onUpdate: (project: Project) => void;
  onNext: () => void;
}

type Phase = 'idle' | 'assets' | 'video' | 'done' | 'error';

export default function StepGenerate({ project, onUpdate, onNext }: StepGenerateProps) {
  const [phase, setPhase] = useState<Phase>(
    project.status === 'video_ready' ? 'done' : project.status === 'assets_ready' ? 'idle' : 'idle'
  );
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const cleanup = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => () => cleanup(), [cleanup]);

  async function handleStart() {
    setError('');
    setPhase('assets');
    setProgress(0);
    setMessage('Starting asset generation...');

    try {
      await startAssetGeneration(project.id);
      pollAssets();
    } catch {
      setPhase('error');
      setError('Failed to start asset generation');
    }
  }

  function pollAssets() {
    cleanup();
    pollRef.current = setInterval(async () => {
      try {
        const status = await getAssetStatus(project.id);
        setProgress(status.progress);
        setMessage(status.message);

        if (status.status === 'completed') {
          cleanup();
          onUpdate({ ...project, status: 'assets_ready' });
          // Automatically start video generation
          startVideoPhase();
        } else if (status.status === 'failed') {
          cleanup();
          setPhase('error');
          setError(status.message);
        }
      } catch {
        cleanup();
        setPhase('error');
        setError('Lost connection while checking status');
      }
    }, 1000);
  }

  async function startVideoPhase() {
    setPhase('video');
    setProgress(0);
    setMessage('Starting video stitching...');

    try {
      await startVideoGeneration(project.id);
      pollVideo();
    } catch {
      setPhase('error');
      setError('Failed to start video generation');
    }
  }

  function pollVideo() {
    cleanup();
    pollRef.current = setInterval(async () => {
      try {
        const status = await getVideoStatus(project.id);
        setProgress(status.progress);
        setMessage(status.message);

        if (status.status === 'completed') {
          cleanup();
          onUpdate({
            ...project,
            status: 'video_ready',
            video_path: status.video_path,
          });
          setPhase('done');
        } else if (status.status === 'failed') {
          cleanup();
          setPhase('error');
          setError(status.message);
        }
      } catch {
        cleanup();
        setPhase('error');
        setError('Lost connection while checking status');
      }
    }, 1500);
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Video</h2>

      {error && <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4">{error}</div>}

      {phase === 'idle' && (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-2">
            This will generate images for each scene, create narration audio, and stitch everything into a video.
          </p>
          <p className="text-sm text-gray-400 mb-6">
            {project.script?.scenes.length || 0} scenes to process
          </p>
          <Button onClick={handleStart}>Generate Video</Button>
        </div>
      )}

      {phase === 'assets' && (
        <div className="py-8">
          <p className="text-sm font-medium text-gray-700 mb-4">Generating assets...</p>
          <ProgressBar progress={progress} message={message} />
        </div>
      )}

      {phase === 'video' && (
        <div className="py-8">
          <p className="text-sm font-medium text-gray-700 mb-4">Stitching video...</p>
          <ProgressBar progress={progress} message={message} />
        </div>
      )}

      {phase === 'done' && (
        <div className="text-center py-8">
          <div className="bg-green-50 text-green-700 px-4 py-3 rounded-lg mb-4">
            Video generated successfully!
          </div>
          <Button onClick={onNext}>Preview Video</Button>
        </div>
      )}

      {phase === 'error' && (
        <div className="text-center py-4">
          <Button onClick={handleStart}>Retry</Button>
        </div>
      )}
    </div>
  );
}
