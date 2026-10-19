import { Zap, ExternalLink } from 'lucide-react';

export default function SwiftPay() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 text-center mt-20">
      <div className="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center text-white mx-auto shadow-xl">
        <Zap size={48} />
      </div>
      <h1 className="text-3xl font-bold text-gray-900 tracking-tight">SwiftPay has been moved!</h1>
      <p className="text-gray-600 max-w-lg mx-auto">
        As part of our production architecture upgrade, SwiftPay is now running as a completely separate standalone application, mirroring a real-world enterprise setup.
      </p>
      
      <a 
        href="http://localhost:5174" 
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all active:scale-95"
      >
        <span>Open Standalone SwiftPay App</span>
        <ExternalLink size={18} />
      </a>
    </div>
  );
}
