import { Plus } from 'lucide-react';

/**
 * Hero Section Widget Component
 * Renders a hero section with background image, title, and description
 */
export default function HeroSectionWidget({ 
  section, 
  sectionContent = [], 
  isSelected, 
  onOpenContentManager,
  isContentLoading
}) {
  return (
    <div className="relative h-64 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
      {isContentLoading ? (
        <div className="flex items-center justify-center h-32 text-gray-400">Loading...</div>
      ) : sectionContent.length > 0 ? (
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
              e.stopPropagation();
              onOpenContentManager(section);
            }}
            className="mt-4 px-6 py-2 bg-white text-blue-600 rounded-lg font-medium hover:bg-gray-100 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Content
          </button>
        </div>
      )}
    </div>
  );
} 