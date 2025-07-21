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
  X
} from 'lucide-react';

// Import our new components
import SectionSidebar from '../components/SectionSidebar';
import PageCanvas from '../components/PageCanvas';
import SectionProperties from '../components/SectionProperties';

export default function PageBuilder() {
  // Core state
  const [selectedLandingPage, setSelectedLandingPage] = useState(null);
  const [selectedSection, setSelectedSection] = useState(null);
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [viewport, setViewport] = useState('desktop');
  const [showContentManager, setShowContentManager] = useState(false);
  
  const queryClient = useQueryClient();

  // Queries
  const { data: landingPages = [], isLoading } = useQuery({
    queryKey: ['landing-pages'],
    queryFn: endpoints.landingPages,
  });
  console.log('LandingPages:', landingPages, 'isLoading:', isLoading);

  const { data: sections = [] } = useQuery({
    queryKey: ['sections'],
    queryFn: endpoints.sections,
  });

  const { data: pageData = {} } = useQuery({
    queryKey: ['page-data', selectedLandingPage?.id],
    queryFn: () => endpoints.getPageData(selectedLandingPage?.id),
    enabled: !!selectedLandingPage?.id,
  });

  // Mutations
  const updateSectionNameMutation = useMutation({
    mutationFn: ({ id, data }) => endpoints.updateSectionName(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['sections']);
      toast.success('Section name updated!');
    },
    onError: () => toast.error('Failed to update section name')
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
      queryClient.invalidateQueries(['page-data']);
      toast.success('Content removed from section!');
    },
    onError: () => toast.error('Failed to remove content')
  });

  const removeSectionFromLandingPageMutation = useMutation({
    mutationFn: ({ landingPageId, sectionId }) => endpoints.removeSectionFromLandingPage(landingPageId, sectionId),
    onSuccess: () => {
      queryClient.invalidateQueries(['landing-pages']);
      queryClient.invalidateQueries(['page-data']);
      queryClient.refetchQueries(['landing-pages']);
      queryClient.refetchQueries(['page-data']);
      toast.success('Section removed from page!');
    },
    onError: () => toast.error('Failed to remove section from page')
  });

  // Event handlers
  const handleDragStart = (e, template) => {
    const { icon, ...serializableTemplate } = template;
    e.dataTransfer.setData('application/json', JSON.stringify(serializableTemplate));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
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

  const handleSectionSelect = (section) => {
    setSelectedSection(section);
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
          <select
            value={selectedLandingPage?.id || ''}
            onChange={(e) => {
              const page = landingPages.find(p => p.id === parseInt(e.target.value));
              setSelectedLandingPage(page);
            }}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value="">Select a landing page</option>
            {landingPages.map((page) => (
              <option key={page.id} value={page.id}>
                {page.name} {page.is_active && '(Active)'}
              </option>
            ))}
          </select>
        </div>

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
      </div>

      <div className="flex-1 flex">
        {/* Left Sidebar - Elements Library */}
        {!isPreviewMode && (
          <SectionSidebar onDragStart={handleDragStart} />
        )}

        {/* Main Canvas */}
        <div className="flex-1 flex flex-col">
          {/* Canvas Toolbar */}
          {!isPreviewMode && (
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
          )}

          {/* Canvas Area */}
          <PageCanvas
            selectedLandingPage={selectedLandingPage}
            selectedSection={selectedSection}
            viewport={viewport}
            isPreviewMode={isPreviewMode}
            onSectionSelect={handleSectionSelect}
            onOpenContentManager={handleOpenContentManager}
            onSectionDelete={handleSectionDelete}
            onRemoveContent={handleRemoveContent}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          />
        </div>

        {/* Right Sidebar - Properties Panel */}
        {!isPreviewMode && selectedSection && (
          <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Properties</h2>
              
              <SectionProperties
                section={selectedSection}
                onUpdate={(updates) => handleSectionUpdate(selectedSection.section.id, updates)}
                updateSectionNameMutation={updateSectionNameMutation}
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