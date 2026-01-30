const STEPS = [
  { label: 'Content', description: 'Review study material' },
  { label: 'Outline', description: 'Generate outline' },
  { label: 'Script', description: 'Generate script' },
  { label: 'Generate', description: 'Create assets & video' },
  { label: 'Preview', description: 'Watch & download' },
];

interface WizardStepperProps {
  currentStep: number;
}

export default function WizardStepper({ currentStep }: WizardStepperProps) {
  return (
    <nav className="mb-8">
      <ol className="flex items-center">
        {STEPS.map((step, i) => {
          const isActive = i === currentStep;
          const isCompleted = i < currentStep;
          return (
            <li key={step.label} className="flex items-center flex-1 last:flex-none">
              <div className="flex items-center gap-2">
                <span
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium border-2 transition-colors ${
                    isActive
                      ? 'bg-indigo-600 border-indigo-600 text-white'
                      : isCompleted
                        ? 'bg-indigo-100 border-indigo-300 text-indigo-700'
                        : 'bg-white border-gray-300 text-gray-400'
                  }`}
                >
                  {isCompleted ? (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    i + 1
                  )}
                </span>
                <div className="hidden sm:block">
                  <p className={`text-sm font-medium ${isActive ? 'text-indigo-600' : isCompleted ? 'text-indigo-500' : 'text-gray-400'}`}>
                    {step.label}
                  </p>
                  <p className="text-xs text-gray-400">{step.description}</p>
                </div>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-0.5 mx-3 ${isCompleted ? 'bg-indigo-300' : 'bg-gray-200'}`} />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
