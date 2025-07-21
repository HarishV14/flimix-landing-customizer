import { useRef } from 'react';
import { Plus, Layers } from 'lucide-react';
import SectionWidget from './SectionWidget';
import { getSectionType } from '../lib/sectionRegistry';

/**
 * Page Canvas Component
 * The main canvas area where sections are displayed
 */
export default function PageCanvas({
  selectedLandingPage,
  selectedSection,
  viewport,
  isPreviewMode,
  onSectionSelect,
  onOpenContentManager,
  onSectionDelete,
  onRemoveContent,
  onDragOver,
  onDrop
}) {
  const canvasRef = useRef(null);

  if (!selectedLandingPage) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Layers className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No page selected</h3>
          <p className="text-gray-600">Select a landing page from the dropdown above to start building</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={canvasRef}
      className={`flex-1 overflow-y-auto ${
        isPreviewMode ? 'bg-white' : 'bg-gray-50'
      }`}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <div className={`mx-auto transition-all duration-300 ${
        viewport === 'desktop' ? 'max-w-none' :
        viewport === 'tablet' ? 'max-w-2xl' :
        'max-w-sm'
      }`}>
        {selectedLandingPage.landingpagesection_set?.map((section) => (
          <SectionWidget
            key={section.section.id}
            section={section}
            isSelected={selectedSection?.section.id === section.section.id}
            template={getSectionType(section.section.section_type)}
            onSectionSelect={onSectionSelect}
            onOpenContentManager={onOpenContentManager}
            onSectionDelete={onSectionDelete}
            onRemoveContent={(contentId) => onRemoveContent(section.section.id, contentId)}
          />
        )) || (
          <div className="flex items-center justify-center h-64 border-2 border-dashed border-gray-300 rounded-lg m-4">
            <div className="text-center">
              <Plus className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">Drag elements here to build your page</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 