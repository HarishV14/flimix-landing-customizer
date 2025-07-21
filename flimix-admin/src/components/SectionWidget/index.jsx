import { useQuery } from '@tanstack/react-query';
import { endpoints } from '../../lib/api';
import { Film, Trash2 } from 'lucide-react';
import HeroSectionWidget from './HeroSectionWidget';
import CarouselSectionWidget from './CarouselSectionWidget';

/**
 * Section Widget Component
 * Acts as a switch to render the appropriate section widget based on section type
 */
export default function SectionWidget({ 
  section, 
  isSelected, 
  template, 
  onSectionSelect, 
  onOpenContentManager, 
  onSectionDelete,
  onRemoveContent
}) {
  // Fetch section content
  const { data: sectionContent = [], isLoading: isContentLoading } = useQuery({
    queryKey: ['section-content', section.section.id],
    queryFn: () => endpoints.getSectionContent(section.section.id),
  });

  // Render the appropriate section widget based on section type
  const renderSectionContent = () => {
    switch(section.section.section_type) {
      case 'hero':
        return (
          <HeroSectionWidget
            section={section}
            sectionContent={sectionContent}
            isSelected={isSelected}
            onOpenContentManager={onOpenContentManager}
            isContentLoading={isContentLoading}
          />
        );
      case 'carousel':
        return (
          <CarouselSectionWidget
            section={section}
            sectionContent={sectionContent}
            isSelected={isSelected}
            onOpenContentManager={onOpenContentManager}
            onRemoveContent={onRemoveContent}
            isContentLoading={isContentLoading}
          />
        );
      default:
        return (
          <div className="p-4 bg-gray-100 rounded-lg text-gray-500 text-center">
            Unknown section type: {section.section.section_type}
          </div>
        );
    }
  };

  return (
    <div
      className={`relative group cursor-pointer transition-all duration-200`}
      onClick={() => onSectionSelect(section)}
    >
      {/* Section Header - always visible */}
      <div className="bg-gray-100 text-black p-2 flex items-center justify-between z-10 rounded-t-lg">
        <span className="text-sm font-medium">{section.section.name}</span>
        <div className="flex items-center gap-1">
          {template?.contentTypes?.length > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onOpenContentManager(section);
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
              e.stopPropagation();
              onSectionDelete(section.section.id);
            }}
            className="p-1 hover:bg-red-600 rounded"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* Section Content */}
      <div className="py-8 max-w-7xl mx-auto">
        {renderSectionContent()}
      </div>
    </div>
  );
} 