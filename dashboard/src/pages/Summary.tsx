import React, { useEffect, useState } from 'react';
import KPICard from '../components/KPICard';
import { loadCleanedBanking, filterData, calculateKPIs } from '../utils/dataLoader';
import type { FilterState, BankingRecord } from '../utils/dataLoader';

const Summary: React.FC = () => {
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

  const kpiList = [
    { name: 'Total Clients', icon: '👥' },
    { name: 'Total Loan', icon: '💰' },
    { name: 'Bank Loan', icon: '🏦' },
    { name: 'Business Lending', icon: '🏢' },
    { name: 'Credit Cards Balance', icon: '💳' },
    { name: 'Total Deposit', icon: '📥' },
    { name: 'Bank Deposit', icon: '🏛️' },
    { name: 'Checking Account Amount', icon: '📝' },
    { name: 'Saving Account Amount', icon: '📊' },
    { name: 'Foreign Currency Amount', icon: '🌍' },
    { name: 'Total CC Amount', icon: '🔢' },
    { name: 'Total Fees', icon: '💵' },
    { name: 'Average Risk Score', icon: '⚠️' },
  ];

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-[#1e3a5f] mb-4">Summary Dashboard - All KPIs</h2>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex gap-2">
            <span className="text-sm font-medium text-gray-600">Engagement:</span>
            {['All', '< 5 Years', '< 10 Years', '< 20 Years', '> 20 Years'].map((period) => (
              <button
                key={period}
                onClick={() => setFilters(f => ({ ...f, timePeriod: period }))}
                className={`px-3 py-1 text-xs rounded transition-colors ${
                  filters.timePeriod === period ? 'bg-[#1e3a5f] text-white' : 'bg-gray-100 hover:bg-gray-200'
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

          <div className="flex gap-2 items-center">
            <span className="text-sm font-medium text-gray-600">Relationship:</span>
            <select
              value={filters.relationship}
              onChange={(e) => setFilters(f => ({ ...f, relationship: e.target.value }))}
              className="px-2 py-1 text-sm border rounded"
            >
              <option value="All">All</option>
              <option value="1">Retail</option>
              <option value="2">Institutional</option>
              <option value="3">Private Bank</option>
              <option value="4">Commercial</option>
            </select>
          </div>

          <div className="flex gap-2 items-center">
            <span className="text-sm font-medium text-gray-600">Advisor:</span>
            <select
              value={filters.advisor}
              onChange={(e) => setFilters(f => ({ ...f, advisor: e.target.value }))}
              className="px-2 py-1 text-sm border rounded"
            >
              <option value="All">All</option>
              <option value="1">Victor Dean</option>
              <option value="2">Jeremy Porter</option>
              <option value="3">Ernest Knight</option>
              <option value="4">Eric Shaw</option>
              <option value="5">Kevin Kim</option>
              <option value="6">Victor Rogers</option>
              <option value="7">Eugene Cunningham</option>
              <option value="8">Joe Carroll</option>
              <option value="9">Steve Sanchez</option>
              <option value="10">Lawrence Sanchez</option>
              <option value="11">Peter Castillo</option>
              <option value="12">Victor Gutierrez</option>
              <option value="13">Daniel Carroll</option>
              <option value="14">Carl Anderson</option>
              <option value="15">Nicholas Ward</option>
              <option value="16">Fred Bryant</option>
              <option value="17">Ryan Taylor</option>
              <option value="18">Sean Vasquez</option>
              <option value="19">Nicholas Morrison</option>
              <option value="20">Jack Phillips</option>
              <option value="21">Juan Ramirez</option>
              <option value="22">Gregory Boyd</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {kpiList.map((kpi) => (
          <KPICard
            key={kpi.name}
            title={kpi.name}
            value={getKPI(kpi.name)}
            icon={kpi.icon}
          />
        ))}
      </div>
    </div>
  );
};

export default Summary;
