import { Eye, Smartphone, Tablet, Monitor as Desktop } from 'lucide-react';
import React from 'react';

export default function CanvasToolbar({ viewport, setViewport, isPreviewMode, setIsPreviewMode }) {
  return (
    <div className="flex items-center gap-2">
      {/* Viewport Controls */}
      <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setViewport('desktop')}
          className={`p-2 rounded ${viewport === 'desktop' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
        >
          <Desktop className="h-4 w-4" />
        </button>
        <button
          onClick={() => setViewport('tablet')}
          className={`p-2 rounded ${viewport === 'tablet' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
        >
          <Tablet className="h-4 w-4" />
        </button>
        <button
          onClick={() => setViewport('mobile')}
          className={`p-2 rounded ${viewport === 'mobile' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
        >
          <Smartphone className="h-4 w-4" />
        </button>
      </div>
      {/* Preview Toggle */}
      <button
        onClick={() => setIsPreviewMode(!isPreviewMode)}
        className={`px-3 py-1 rounded-md text-sm font-medium ${
          isPreviewMode 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        <Eye className="h-4 w-4 inline mr-1" />
        Preview
      </button>
    </div>
  );
} 