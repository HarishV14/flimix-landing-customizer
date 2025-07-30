import React, { useState } from 'react';
import SectionWidget from './SectionWidget';
import { Plus } from 'lucide-react';
import { endpoints } from '../lib/api';
import { toast } from 'react-hot-toast';

export default function PageCanvas({
  selectedLandingPage,
  setSelectedLandingPage,
  selectedSection,
  setSelectedSection,
  isSidebarDragging,
  handleSidebarDragOver,
  handleSidebarDrop,
  getSectionType,
  handleOpenContentManager,
  handleSectionDelete,
  handleRemoveContent,
  viewport
}) {
  // Section drag-and-drop state and handlers (now local)
  const [draggedSectionIndex, setDraggedSectionIndex] = useState(null);
  const [isSectionDragging, setIsSectionDragging] = useState(false);

  const handleSectionDragStart = (e, idx) => {
    setDraggedSectionIndex(idx);
    setIsSectionDragging(true);
  };

  const handleSectionDragOver = (e, idx) => {
    e.preventDefault();
  };

  const handleSectionDrop = async (e, idx) => {
    e.preventDefault();
    if (draggedSectionIndex === null || draggedSectionIndex === idx) return;
    if (!selectedLandingPage) return;
    // 1. Reorder the array in the frontend (for immediate feedback)
    const newOrder = [...selectedLandingPage.landingpagesection_set];
    const [moved] = newOrder.splice(draggedSectionIndex, 1);
    newOrder.splice(idx, 0, moved);
    // 2. Update local state for instant UI feedback
    setSelectedLandingPage({
      ...selectedLandingPage,
      landingpagesection_set: newOrder
    });
    setDraggedSectionIndex(null);
    setIsSectionDragging(false);
    // 3. Update backend with LandingPageSection ids
    try {
      const orderString = newOrder.map(s => s.id).join(',');
      await endpoints.reorderLandingPageSections(selectedLandingPage.id, { section_order: orderString });
      toast.success('Section order updated!');
    } catch (err) {
      toast.error('Failed to update section order');
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Canvas Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {selectedLandingPage ? `${selectedLandingPage.name} - ${selectedLandingPage.landingpagesection_set?.length || 0} sections` : 'No page selected'}
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>Drag elements from the sidebar to add them to your page</span>
        </div>
      </div>
      {/* Canvas Area with drag-and-drop for sections */}
      <div
        onDragOver={isSidebarDragging ? handleSidebarDragOver : undefined}
        onDrop={isSidebarDragging ? handleSidebarDrop : undefined}
      >
        <div className={`mx-auto transition-all duration-300 ${
          viewport === 'desktop' ? 'max-w-none' :
          viewport === 'tablet' ? 'max-w-2xl' :
          'max-w-sm'
        }`}>
          {selectedLandingPage?.landingpagesection_set?.map((section, idx) => (
            <div
              key={section.section.id}
              draggable={!isSidebarDragging}
              onDragStart={!isSidebarDragging ? (e) => handleSectionDragStart(e, idx) : undefined}
              onDragOver={!isSidebarDragging ? (e) => handleSectionDragOver(e, idx) : undefined}
              onDrop={!isSidebarDragging ? (e) => handleSectionDrop(e, idx) : undefined}
            >
              <SectionWidget
                section={section}
                isSelected={selectedSection?.section.id === section.section.id}
                template={getSectionType(section.section.section_type)}
                onSectionSelect={setSelectedSection}
                onOpenContentManager={handleOpenContentManager}
                onSectionDelete={handleSectionDelete}
                onRemoveContent={(contentId) => handleRemoveContent(section.section.id, contentId)}
                isSectionDragging={isSectionDragging}
              />
            </div>
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
    </div>
  );
} 