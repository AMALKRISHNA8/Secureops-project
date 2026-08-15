/**
 * Loading spinner component.
 */

export default function LoadingSpinner({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 animate-fade-in">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 rounded-full border-2 border-gray-700"></div>
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-cyber-400 animate-spin"></div>
      </div>
      <p className="mt-4 text-sm text-gray-400">{text}</p>
    </div>
  );
}
