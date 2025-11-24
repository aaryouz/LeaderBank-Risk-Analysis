import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import KPICard from '../components/KPICard';
import { loadCleanedBanking, filterData, calculateKPIs } from '../utils/dataLoader';
import type { FilterState, BankingRecord } from '../utils/dataLoader';

const Home: React.FC = () => {
  const [rawData, setRawData] = useState<BankingRecord[]>([]);
  const [kpis, setKpis] = useState<Record<string, { value: number; formatted: string }>>({});
  const [filters, setFilters] = useState<FilterState>({
    gender: 'All',
    relationship: 'All',
    advisor: 'All',
    timePeriod: 'All',
  });

  useEffect(() => {
    loadCleanedBanking().then(data => {
      setRawData(data.filter(d => d['Client ID']));
    });
  }, []);

  useEffect(() => {
    if (rawData.length > 0) {
      const filtered = filterData(rawData, filters);
      const calculated = calculateKPIs(filtered);
      setKpis(calculated);
    }
  }, [rawData, filters]);

  const getKPI = (name: string) => kpis[name]?.formatted || '...';

  return (
    <div className="p-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex gap-2">
            <span className="text-sm font-medium text-gray-600">Engagement:</span>
            {['All', '< 5 Years', '< 10 Years', '< 20 Years', '> 20 Years'].map((period) => (
              <button
                key={period}
                onClick={() => setFilters(f => ({ ...f, timePeriod: period }))}
                className={`px-3 py-1 text-xs rounded transition-colors ${
                  filters.timePeriod === period
                    ? 'bg-[#1e3a5f] text-white'
                    : 'bg-gray-100 hover:bg-gray-200'
                }`}
              >
                {period}
              </button>
            ))}
          </div>

          <div className="flex gap-2 items-center">
            <span className="text-sm font-medium text-gray-600">Gender:</span>
            <select
              value={filters.gender}
              onChange={(e) => setFilters(f => ({ ...f, gender: e.target.value as FilterState['gender'] }))}
              className="px-2 py-1 text-sm border rounded"
            >
              <option>All</option>
              <option>Male</option>
              <option>Female</option>
            </select>
          </div>
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Link
          to="/loan-analysis"
          className="bg-[#1e3a5f] text-white p-6 rounded-lg text-center font-bold hover:bg-[#2a4a6f] transition-colors"
        >
          LOAN ANALYSIS
        </Link>
        <Link
          to="/deposit-analysis"
          className="bg-[#1e3a5f] text-white p-6 rounded-lg text-center font-bold hover:bg-[#2a4a6f] transition-colors"
        >
          DEPOSIT ANALYSIS
        </Link>
        <Link
          to="/summary"
          className="bg-[#1e3a5f] text-white p-6 rounded-lg text-center font-bold hover:bg-[#2a4a6f] transition-colors"
        >
          SUMMARY
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
        <KPICard title="Total Clients" value={getKPI('Total Clients')} icon="👥" />
        <KPICard title="Total Loan" value={getKPI('Total Loan')} icon="💰" />
        <KPICard title="Total Deposit" value={getKPI('Total Deposit')} icon="🏦" />
        <KPICard title="Total Fees" value={getKPI('Total Fees')} icon="💵" />
        <KPICard title="Total CC Amount" value={getKPI('Total CC Amount')} icon="💳" />
        <KPICard title="Saving Account" value={getKPI('Saving Account Amount')} icon="📊" />
        <KPICard title="Avg Risk Score" value={getKPI('Average Risk Score')} icon="⚠️" />
      </div>
    </div>
  );
};

export default Home;
