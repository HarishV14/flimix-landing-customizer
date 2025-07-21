import { Plus, Settings, Trash2 } from 'lucide-react';

/**
 * Carousel Section Widget Component
 * Renders a horizontal scrolling carousel of movies or series
 */
export default function CarouselSectionWidget({ 
  section, 
  sectionContent = [], 
  isSelected, 
  onOpenContentManager,
  onRemoveContent,
  isContentLoading
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold">{section.section.name}</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{sectionContent.length} items</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onOpenContentManager(section);
            }}
            className="p-1 text-gray-400 hover:text-gray-600"
            title="Manage Content"
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {isContentLoading ? (
          <div className="flex items-center justify-center h-32 w-full text-gray-400">Loading...</div>
        ) : sectionContent.length > 0 ? (
          sectionContent.map((item) => (
            <div 
              key={item.id} 
              className="flex-shrink-0 w-48 h-64 bg-gradient-to-br from-gray-200 to-gray-300 rounded-lg flex flex-col items-center justify-center overflow-hidden"
            >
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
                    e.stopPropagation();
                    onRemoveContent(item.id);
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
                e.stopPropagation();
                onOpenContentManager(section);
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
  );
} 