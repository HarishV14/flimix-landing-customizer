import { useState, useEffect } from 'react';

/**
 * Section Properties Component
 * Only section name change is allowed now
 */
export default function SectionProperties({ section, onUpdate, updateSectionNameMutation }) {
  const [name, setName] = useState(section.section.name || "");
  const [dirty, setDirty] = useState(false);
  
  // Reset state when selected section changes
  useEffect(() => {
    setName(section.section.name || "");
    setDirty(false);
  }, [section.section.id, section.section.name]);

  const handleNameChange = (e) => {
    const newName = e.target.value;
    setName(newName);
    onUpdate({ name: newName });
    setDirty(true);
  };

  const handleSave = () => {
    updateSectionNameMutation.mutate({ id: section.section.id, data: { name } });
    setDirty(false);
  };

  return (
    <div className="space-y-6">
      {/* Section Name (common for all section types) */}
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
      {/* No additional properties for any section type */}
      {/* Save Button */}
      <button
        onClick={handleSave}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Save
      </button>
    </div>
  );
} 