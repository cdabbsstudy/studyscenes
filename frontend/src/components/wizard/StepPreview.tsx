import type { Project } from '../../types';
import Button from '../common/Button';

interface StepPreviewProps {
  project: Project;
}

export default function StepPreview({ project }: StepPreviewProps) {
  const videoUrl = project.video_path;

  if (!videoUrl) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No video available. Go back and generate one.</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Preview Video</h2>

      <div className="bg-black rounded-lg overflow-hidden mb-6">
        <video
          controls
          className="w-full max-h-[480px]"
          src={videoUrl}
        >
          Your browser does not support the video tag.
        </video>
      </div>

      <div className="flex gap-3">
        <a href={videoUrl} download>
          <Button>Download MP4</Button>
        </a>
        <Button variant="secondary" onClick={() => window.location.reload()}>
          Start Over
        </Button>
      </div>

      {project.scenes.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Scenes</h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {project.scenes.map((scene) => (
              <div key={scene.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                {scene.image_path && (
                  <img
                    src={scene.image_path}
                    alt={scene.title}
                    className="w-full h-32 object-cover"
                  />
                )}
                <div className="p-3">
                  <p className="font-medium text-sm text-gray-900">{scene.title}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {scene.duration_sec.toFixed(1)}s
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
