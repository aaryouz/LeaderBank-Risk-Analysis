import React from 'react';

interface FilterBarProps {
  showGender?: boolean;
  showRelationship?: boolean;
  showAdvisor?: boolean;
}

const FilterBar: React.FC<FilterBarProps> = ({
  showGender = true,
  showRelationship = false,
  showAdvisor = false
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex gap-2">
          <span className="text-sm font-medium text-gray-600">Time Period:</span>
          {['All Time', '30D', '90D', '6M', '12M'].map((period) => (
            <button
              key={period}
              className="px-3 py-1 text-xs rounded bg-gray-100 hover:bg-[#1e3a5f] hover:text-white transition-colors"
            >
              {period}
            </button>
          ))}
        </div>

        {showGender && (
          <div className="flex gap-2 items-center">
            <span className="text-sm font-medium text-gray-600">Gender:</span>
            <select className="px-2 py-1 text-sm border rounded">
              <option>All</option>
              <option>Male</option>
              <option>Female</option>
            </select>
          </div>
        )}

        {showRelationship && (
          <div className="flex gap-2 items-center">
            <span className="text-sm font-medium text-gray-600">Relationship:</span>
            <select className="px-2 py-1 text-sm border rounded">
              <option>All</option>
            </select>
          </div>
        )}

        {showAdvisor && (
          <div className="flex gap-2 items-center">
            <span className="text-sm font-medium text-gray-600">Advisor:</span>
            <select className="px-2 py-1 text-sm border rounded">
              <option>All</option>
            </select>
          </div>
        )}
      </div>
    </div>
  );
};

export default FilterBar;
