import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'HOME' },
    { path: '/loan-analysis', label: 'LOAN ANALYSIS' },
    { path: '/deposit-analysis', label: 'DEPOSIT ANALYSIS' },
    { path: '/summary', label: 'SUMMARY' },
  ];

  return (
    <nav className="bg-[#1e3a5f] text-white p-4">
      <div className="container mx-auto flex items-center justify-between">
        <h1 className="text-xl font-bold">Banking Dashboard</h1>
        <div className="flex gap-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                location.pathname === item.path
                  ? 'bg-white text-[#1e3a5f]'
                  : 'hover:bg-white/20'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
