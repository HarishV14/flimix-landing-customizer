import React from 'react';

export default function LandingPageSelector({ landingPages, selectedLandingPage, setSelectedLandingPage }) {
  return (
    <select
      value={selectedLandingPage?.id || ''}
      onChange={e => {
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
  );
} 