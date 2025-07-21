import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { endpoints } from '../lib/api'
import { toast } from 'react-hot-toast'
import ContentManager from '../components/ContentManager'
import { 
  Plus, 
  Trash2, 
  Eye, 
  Settings,
  Save,
  Image,
  Video,
  Film,
  X,
  Smartphone,
  Tablet,
  Monitor as Desktop,
  Layers
} from 'lucide-react'

// Only Hero Section and Carousel
const sectionTemplates = [
  {
    id: 'hero',
    name: 'Hero Section',
    icon: <Image className="h-5 w-5" />,
    description: 'Full-width hero with background image',
    contentTypes: ['movie', 'series'],
    maxContent: 1
  },
  {
    id: 'carousel',
    name: 'Carousel',
    icon: <Video className="h-5 w-5" />,
    description: 'Horizontal scrolling carousel',
    contentTypes: ['movie', 'series'],
    maxContent: 20
  }
]

export default function PageBuilder() {
  // Core state
  const [selectedLandingPage, setSelectedLandingPage] = useState(null)
  const [selectedSection, setSelectedSection] = useState(null)
  const [isPreviewMode, setIsPreviewMode] = useState(false)
  const [viewport, setViewport] = useState('desktop')
  const [showContentManager, setShowContentManager] = useState(false)
  
  const queryClient = useQueryClient()
  const canvasRef = useRef(null)

  // Queries
  const { data: landingPages = [], isLoading } = useQuery({
    queryKey: ['landing-pages'],
    queryFn: endpoints.landingPages,
  })

  const { data: sections = [] } = useQuery({
    queryKey: ['sections'],
    queryFn: endpoints.sections,
  })

  const { data: pageData = {} } = useQuery({
    queryKey: ['page-data', selectedLandingPage?.id],
    queryFn: () => endpoints.getPageData(selectedLandingPage?.id),
    enabled: !!selectedLandingPage?.id,
  })

  // Mutations
  const updateLandingPageMutation = useMutation({
    mutationFn: ({ id, data }) => endpoints.updateLandingPage(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['landing-pages'])
      toast.success('Page saved successfully!')
    },
    onError: () => toast.error('Failed to save page')
  })

  const updateSectionNameMutation = useMutation({
    mutationFn: ({ id, data }) => endpoints.updateSectionName(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['sections'])
      toast.success('Section name updated!')
    },
    onError: () => toast.error('Failed to update section name')
  })

  const createSectionMutation = useMutation({
    mutationFn: (data) => endpoints.createSection(data),
    onSuccess: (newSection) => {
      queryClient.invalidateQueries(['sections'])
      toast.success('Section created successfully!')
      return newSection
    },
    onError: () => toast.error('Failed to create section')
  })

  const addSectionToLandingPageMutation = useMutation({
    mutationFn: ({ landingPageId, sectionId }) => endpoints.addSectionToLandingPage(landingPageId, sectionId),
    onSuccess: () => {
      queryClient.invalidateQueries(['landing-pages'])
      toast.success('Section added to page!')
    },
    onError: () => toast.error('Failed to add section to page')
  })

  const removeContentMutation = useMutation({
    mutationFn: ({ sectionId, itemId }) => endpoints.removeContentFromSection(sectionId, itemId),
    onSuccess: () => {
      queryClient.invalidateQueries(['sections'])
      queryClient.invalidateQueries(['landing-pages'])
      queryClient.invalidateQueries(['page-data'])
      toast.success('Content removed from section!')
    },
    onError: () => toast.error('Failed to remove content')
  })

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
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

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
    setSelectedSection(section)
  }

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
    if (!selectedLandingPage) return

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
          }
        }
        return lpSection
      })
    }

    setSelectedLandingPage(updatedLandingPage)

    // Also update selectedSection if it matches
    if (selectedSection && selectedSection.section.id === sectionId) {
      setSelectedSection({
        ...selectedSection,
        section: {
          ...selectedSection.section,
          ...updates
        }
      })
    }
  }

  const handleSave = () => {
    if (!selectedLandingPage) return
    updateLandingPageMutation.mutate({
      id: selectedLandingPage.id,
      data: selectedLandingPage
    })
  }

  const handleOpenContentManager = (section) => {
    setSelectedSection(section)
    setShowContentManager(true)
  }

  const handleContentUpdate = () => {
    queryClient.invalidateQueries(['landing-pages'])
    setShowContentManager(false)
  }

  // Render section preview
  function SectionPreview({ section, isSelected, template, onSectionSelect, onOpenContentManager, onSectionDelete, onRemoveContent }) {
    const { data: sectionContent = [], isLoading: isContentLoading } = useQuery({
      queryKey: ['section-content', section.section.id],
      queryFn: () => endpoints.getSectionContent(section.section.id),
    });

    return (
      <div
        key={section.section.id}
        className={`relative group cursor-pointer transition-all duration-200 ${
          isSelected ? 'ring-2 ring-blue-500' : 'hover:ring-2 hover:ring-gray-300'
        }`}
        onClick={() => onSectionSelect(section)}
      >
        {/* Section Header */}
        <div className="absolute top-0 left-0 right-0 bg-gray-800 text-white p-2 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity z-10">
          <span className="text-sm font-medium">{section.section.name}</span>
          <div className="flex items-center gap-1">
            {template?.contentTypes?.length > 0 && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onOpenContentManager(section)
                }}
                className="p-1 hover:bg-gray-700 rounded flex items-center gap-1"
                title="Manage Content"
              >
                <Film className="h-3 w-3" />
                <span className="text-xs">{sectionContent.length}</span>
              </button>
            )}
            <button
              onClick={(e) => {
                e.stopPropagation()
                onSectionDelete(section.section.id)
              }}
              className="p-1 hover:bg-red-600 rounded"
            >
              <Trash2 className="h-3 w-3" />
            </button>
          </div>
        </div>

        {/* Section Content */}
        <div className="py-8 max-w-7xl mx-auto">
          {isContentLoading ? (
            <div className="flex items-center justify-center h-32 text-gray-400">Loading...</div>
          ) : (
            <>
              {section.section.section_type === 'hero' && (
                <div className="relative h-64 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  {sectionContent.length > 0 ? (
                    <>
                      <img
                        src={sectionContent[0].content?.background_image_url || sectionContent[0].content?.poster_url || 'https://placehold.co/600x300?text=No+Image'}
                        alt={sectionContent[0].content?.title}
                        className="absolute inset-0 w-full h-full object-cover rounded-lg opacity-40"
                        style={{ zIndex: 0 }}
                        onError={e => { e.target.src = 'https://placehold.co/600x300?text=No+Image' }}
                      />
                      <div className="relative z-10 text-center text-white">
                        <h2 className="text-2xl font-bold mb-2">{sectionContent[0].content?.title}</h2>
                        <p className="text-lg opacity-90">{sectionContent[0].content?.description}</p>
                      </div>
                    </>
                  ) : (
                    <div className="text-center text-white">
                      <h2 className="text-2xl font-bold mb-2">{section.section.name}</h2>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation()
                          onOpenContentManager(section)
                        }}
                        className="mt-4 px-6 py-2 bg-white text-blue-600 rounded-lg font-medium hover:bg-gray-100 flex items-center gap-2"
                      >
                        <Plus className="h-4 w-4" />
                        Add Content
                      </button>
                    </div>
                  )}
                </div>
              )}

              {section.section.section_type === 'carousel' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold">{section.section.name}</h3>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">{sectionContent.length} items</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onOpenContentManager(section)
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600"
                        title="Manage Content"
                      >
                        <Settings className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  <div className="flex gap-4 overflow-x-auto pb-4">
                    {sectionContent.length > 0 ? (
                      sectionContent.map((item) => (
                        <div key={item.id} className="flex-shrink-0 w-48 h-64 bg-gradient-to-br from-gray-200 to-gray-300 rounded-lg flex flex-col items-center justify-center overflow-hidden">
                          <img
                            src={item.content?.poster_url || 'https://placehold.co/200x300?text=No+Image'}
                            alt={item.content?.title}
                            className="w-full h-40 object-cover rounded-t"
                            onError={e => { e.target.src = 'https://placehold.co/200x300?text=No+Image' }}
                          />
                          <div className="p-2 text-center">
                            <span className="text-gray-700 text-sm font-medium block truncate">{item.content?.title}</span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                onRemoveContent(item.id)
                              }}
                              className="text-red-500 text-xs hover:text-red-700"
                              title="Remove item"
                            >
                              <Trash2 className="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="flex-shrink-0 w-full h-32 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            onOpenContentManager(section)
                          }}
                          className="text-gray-500 hover:text-gray-700 flex items-center gap-2"
                        >
                          <Plus className="h-4 w-4" />
                          Add Movies/Series
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
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
              const page = landingPages.find(p => p.id === parseInt(e.target.value))
              setSelectedLandingPage(page)
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

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={!selectedLandingPage}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Save className="h-4 w-4" />
            Save
          </button>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Left Sidebar - Elements Library */}
        {!isPreviewMode && (
          <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Elements</h2>
              
              <div className="space-y-3">
                {sectionTemplates.map((template) => (
                  <div
                    key={template.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, template)}
                    className="border border-gray-200 rounded-lg p-3 cursor-move hover:border-blue-300 hover:shadow-sm transition-all"
                  >
                    <div className="flex items-center gap-3 mb-2">
                      {template.icon}
                      <h3 className="font-medium text-gray-900">{template.name}</h3>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                    <div className="w-full h-20 bg-gray-100 rounded border flex items-center justify-center">
                      <span className="text-gray-500 text-sm">{template.name}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
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
          <div 
            ref={canvasRef}
            className={`flex-1 overflow-y-auto ${
              isPreviewMode ? 'bg-white' : 'bg-gray-50'
            }`}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            {!selectedLandingPage ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <Layers className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No page selected</h3>
                  <p className="text-gray-600">Select a landing page from the dropdown above to start building</p>
                </div>
              </div>
            ) : (
              <div className={`mx-auto transition-all duration-300 ${
                viewport === 'desktop' ? 'max-w-none' :
                viewport === 'tablet' ? 'max-w-2xl' :
                'max-w-sm'
              }`}>
                {selectedLandingPage.landingpagesection_set?.map((section) => (
                  <SectionPreview
                    key={section.section.id}
                    section={section}
                    isSelected={selectedSection?.section.id === section.section.id}
                    template={sectionTemplates.find(t => t.id === section.section.section_type)}
                    onSectionSelect={handleSectionSelect}
                    onOpenContentManager={handleOpenContentManager}
                    onSectionDelete={handleSectionDelete}
                    onRemoveContent={(contentId) => {
                      removeContentMutation.mutate({ sectionId: section.section.id, itemId: contentId });
                    }}
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
            )}
          </div>
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
  )
}

// Section Properties Component
function SectionProperties({ section, onUpdate, updateSectionNameMutation }) {
  const [name, setName] = useState(section.section.name || "")
  const [dirty, setDirty] = useState(false)
  
  // Reset state when selected section changes
  useEffect(() => {
    setName(section.section.name || "")
    setDirty(false)
  }, [section.section.id, section.section.name])

  const handleNameChange = (e) => {
    const newName = e.target.value;
    setName(newName)
    onUpdate({ name: newName })
    setDirty(true);
  }

  const handleSave = () => {
    updateSectionNameMutation.mutate({ id: section.section.id, data: { name } })
    setDirty(false)
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Section Name
        </label>
        <input
          type="text"
          value={name}
          onChange={handleNameChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <button
        onClick={handleSave}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Save
      </button>
    </div>
  )
} 