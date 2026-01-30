interface ProgressBarProps {
  progress: number; // 0.0 - 1.0
  message?: string;
}

export default function ProgressBar({ progress, message }: ProgressBarProps) {
  const percent = Math.round(progress * 100);
  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm text-gray-600">{message || 'Processing...'}</span>
        <span className="text-sm font-medium text-indigo-600">{percent}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
