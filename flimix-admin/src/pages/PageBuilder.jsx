import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { endpoints } from '../lib/api';
import { toast } from 'react-hot-toast';
import ContentManager from '../components/ContentManager';
import {
  Eye,
  Save,
  Smartphone,
  Tablet,
  Monitor as Desktop,
  X,
  Plus
} from 'lucide-react';

// Import our new components
import SectionSidebar from '../components/SectionSidebar';
import SectionProperties from '../components/SectionProperties';
import SectionWidget from '../components/SectionWidget'; // Added import for SectionWidget
import { getSectionType } from '../lib/sectionRegistry'; // Add this import
import LandingPageSelector from '../components/LandingPageSelector';
import CanvasToolbar from '../components/CanvasToolbar';
import PageCanvas from '../components/PageCanvas';

export default function PageBuilder() {
  // Core state
  const [selectedLandingPage, setSelectedLandingPage] = useState(null);
  const [selectedSection, setSelectedSection] = useState(null);
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [viewport, setViewport] = useState('desktop');
  const [showContentManager, setShowContentManager] = useState(false);
  const [isSidebarDragging, setIsSidebarDragging] = useState(false);
  
  const queryClient = useQueryClient();

  const { data: landingPages = [], isLoading } = useQuery({
    queryKey: ['landing-pages'],
    queryFn: endpoints.landingPages,
  });


  const createSectionMutation = useMutation({
    mutationFn: (data) => endpoints.createSection(data),
    onSuccess: (newSection) => {
      queryClient.invalidateQueries(['sections']);
      toast.success('Section created successfully!');
      return newSection;
    },
    onError: () => toast.error('Failed to create section')
  });

  const addSectionToLandingPageMutation = useMutation({
    mutationFn: ({ landingPageId, sectionId }) => endpoints.addSectionToLandingPage(landingPageId, sectionId),
    onSuccess: () => {
      queryClient.invalidateQueries(['landing-pages']);
      toast.success('Section added to page!');
    },
    onError: () => toast.error('Failed to add section to page')
  });

  const removeContentMutation = useMutation({
    mutationFn: ({ sectionId, itemId }) => endpoints.removeContentFromSection(sectionId, itemId),
    onSuccess: () => {
      queryClient.invalidateQueries(['sections']);
      queryClient.invalidateQueries(['landing-pages']);
      toast.success('Content removed from section!');
    },
    onError: () => toast.error('Failed to remove content')
  });

  const removeSectionFromLandingPageMutation = useMutation({
    mutationFn: ({ landingPageId, sectionId }) => endpoints.removeSectionFromLandingPage(landingPageId, sectionId),
    onSuccess: () => {
      queryClient.invalidateQueries(['landing-pages']);
      toast.success('Section removed from page!');
    },
    onError: () => toast.error('Failed to remove section from page')
  });

  // Event handlers
  const handleDragStart = (e, template) => {
    const { icon, ...serializableTemplate } = template;
    e.dataTransfer.setData('application/json', JSON.stringify(serializableTemplate));
  };


  const handleSectionDelete = (sectionId) => {
    if (!selectedLandingPage) return;

    // Keep a reference to the current landing page for optimistic UI update
    const previousLandingPage = selectedLandingPage;
    
    // Optimistically update the UI
    const updatedLandingPage = {
      ...selectedLandingPage,
      landingpagesection_set: selectedLandingPage.landingpagesection_set.filter(
        lpSection => lpSection.section.id !== sectionId
      )
    };
    
    // Update local state immediately
    setSelectedLandingPage(updatedLandingPage);
    
    // Then call the backend
    removeSectionFromLandingPageMutation.mutate({
      landingPageId: selectedLandingPage.id,
      sectionId
    }, {
      onError: () => {
        // Revert to previous state if there's an error
        setSelectedLandingPage(previousLandingPage);
      }
    });

    setSelectedSection(null);
  };

  const handleSectionUpdate = (sectionId, updates) => {
    if (!selectedLandingPage) return;

    // Update landing page sections
    const updatedLandingPage = {
      ...selectedLandingPage,
      landingpagesection_set: selectedLandingPage.landingpagesection_set.map(lpSection => {
        if (lpSection.section.id === sectionId) {
          return {
            ...lpSection,
            section: {
              ...lpSection.section,
              ...updates
            }
          };
        }
        return lpSection;
      })
    };

    setSelectedLandingPage(updatedLandingPage);

    // Also update selectedSection if it matches
    if (selectedSection && selectedSection.section.id === sectionId) {
      setSelectedSection({
        ...selectedSection,
        section: {
          ...selectedSection.section,
          ...updates
        }
      });
    }
  };

  const handleOpenContentManager = (section) => {
    setSelectedSection(section);
    setShowContentManager(true);
  };

  const handleContentUpdate = () => {
    queryClient.invalidateQueries(['landing-pages']);
    setShowContentManager(false);
  };

  const handleRemoveContent = (sectionId, contentId) => {
    removeContentMutation.mutate({ sectionId, itemId: contentId });
  };

  // Drag-and-drop handlers for section reordering

  // Sidebar drag handlers
  const handleSidebarDragOver = (e) => {
    e.preventDefault();
  };
  const handleSidebarDrop = async (e) => {
    e.preventDefault();
    setIsSidebarDragging(false);
    const template = JSON.parse(e.dataTransfer.getData('application/json'));
    if (!selectedLandingPage) {
      toast.error('Please select a landing page first');
      return;
    }
    try {
      // Create new section in backend
      const newSection = await createSectionMutation.mutateAsync({
        name: template.name,
        section_type: template.id,
        content_selection_type: 'manual'
      });
      // Add section to landing page
      await addSectionToLandingPageMutation.mutateAsync({
        landingPageId: selectedLandingPage.id,
        sectionId: newSection.id
      });
      // Refetch landing pages and update selectedLandingPage
      const landingPages = await queryClient.fetchQuery({
        queryKey: ['landing-pages'],
        queryFn: endpoints.landingPages,
      });
      const updated = landingPages.find(lp => lp.id === selectedLandingPage.id);
      setSelectedLandingPage(updated);
      toast.success('Section added!');
    } catch (error) {
      console.error('Error adding section:', error);
      toast.error('Failed to add section');
    }
  };

  // Persist selectedLandingPage to localStorage
  useEffect(() => {
    if (selectedLandingPage?.id) {
      localStorage.setItem('selectedLandingPageId', selectedLandingPage.id);
    }
  }, [selectedLandingPage]);

  // Restore selectedLandingPage from localStorage on mount/landingPages load
  useEffect(() => {
    const savedId = localStorage.getItem('selectedLandingPageId');
    if (savedId && landingPages.length > 0) {
      const found = landingPages.find(lp => lp.id === parseInt(savedId));
      if (found) setSelectedLandingPage(found);
    }
  }, [landingPages]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Top Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold text-gray-900">Page Builder</h1>
          
          {/* Landing Page Selector */}
          <LandingPageSelector
            landingPages={landingPages}
            selectedLandingPage={selectedLandingPage}
            setSelectedLandingPage={setSelectedLandingPage}
          />
        </div>

        {/* Canvas Toolbar */}
        {!isPreviewMode && (
          <CanvasToolbar
            viewport={viewport}
            setViewport={setViewport}
            isPreviewMode={isPreviewMode}
            setIsPreviewMode={setIsPreviewMode}
          />
        )}
      </div>

      <div className="flex-1 flex">
        {/* Left Sidebar - Elements Library */}
        {!isPreviewMode && (
          <SectionSidebar onDragStart={handleDragStart} setIsSidebarDragging={setIsSidebarDragging} />
        )}

        {/* Main Canvas */}
        <PageCanvas
          selectedLandingPage={selectedLandingPage}
          setSelectedLandingPage={setSelectedLandingPage}
          selectedSection={selectedSection}
          setSelectedSection={setSelectedSection}
          isSidebarDragging={isSidebarDragging}
          handleSidebarDragOver={handleSidebarDragOver}
          handleSidebarDrop={handleSidebarDrop}
          getSectionType={getSectionType}
          handleOpenContentManager={handleOpenContentManager}
          handleSectionDelete={handleSectionDelete}
          handleRemoveContent={handleRemoveContent}
          viewport={viewport}
        />

        {/* Right Sidebar - Properties Panel */}
        {!isPreviewMode && selectedSection && (
          <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Properties</h2>
              
              <SectionProperties
                section={selectedSection}
                onUpdate={(updates) => handleSectionUpdate(selectedSection.section.id, updates)}
              />
            </div>
          </div>
        )}
      </div>

      {/* Content Manager Modal */}
      {showContentManager && selectedSection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Manage Content - {selectedSection.section.name}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Add, remove, and reorder movies and series in this section
                </p>
              </div>
              <button
                onClick={() => setShowContentManager(false)}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ContentManager
                section={selectedSection.section}
                onClose={() => setShowContentManager(false)}
                onContentUpdate={handleContentUpdate}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 