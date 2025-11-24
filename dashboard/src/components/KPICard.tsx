import React from 'react';

interface KPICardProps {
  title: string;
  value: string;
  icon?: string;
  color?: string;
}

const KPICard: React.FC<KPICardProps> = ({ title, value, icon, color = '#1e3a5f' }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 flex flex-col items-center justify-center min-h-[120px]">
      {icon && <span className="text-2xl mb-2">{icon}</span>}
      <h3 className="text-sm text-gray-600 text-center mb-1">{title}</h3>
      <p className="text-xl font-bold" style={{ color }}>{value}</p>
    </div>
  );
};

export default KPICard;
