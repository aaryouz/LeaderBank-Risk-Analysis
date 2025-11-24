import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import KPICard from '../components/KPICard';
import { loadCleanedBanking, filterData, calculateKPIs } from '../utils/dataLoader';
import type { FilterState, BankingRecord } from '../utils/dataLoader';

const DepositAnalysis: React.FC = () => {
  const [rawData, setRawData] = useState<BankingRecord[]>([]);
  const [kpis, setKpis] = useState<Record<string, { value: number; formatted: string }>>({});
  const [nationalityData, setNationalityData] = useState<any[]>([]);
  const [incomeData, setIncomeData] = useState<any[]>([]);
  const [engagementData, setEngagementData] = useState<any[]>([]);
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

      // Group by nationality
      const natMap = new Map<string, { deposit: number; checking: number; savings: number; foreign: number }>();
      filtered.forEach(r => {
        const nat = r.Nationality || 'Unknown';
        const existing = natMap.get(nat) || { deposit: 0, checking: 0, savings: 0, foreign: 0 };
        natMap.set(nat, {
          deposit: existing.deposit + (r['Bank Deposits'] || 0),
          checking: existing.checking + (r['Checking Accounts'] || 0),
          savings: existing.savings + (r['Saving Accounts'] || 0),
          foreign: existing.foreign + (r['Foreign Currency Account'] || 0),
        });
      });
      setNationalityData(Array.from(natMap.entries()).map(([name, vals]) => ({
        name,
        bankDeposit: vals.deposit / 1000000,
        checking: vals.checking / 1000000,
        savings: vals.savings / 1000000,
        foreign: vals.foreign / 1000000,
      })));

      // Group by income band
      const incMap = new Map<string, number>();
      filtered.forEach(r => {
        const inc = r['Income Band'] || 'Unknown';
        incMap.set(inc, (incMap.get(inc) || 0) + (r['Bank Deposits'] || 0));
      });
      setIncomeData(Array.from(incMap.entries()).map(([name, bankDeposit]) => ({
        name,
        bankDeposit: bankDeposit / 1000000
      })));

      // Group by engagement
      const engMap = new Map<string, number>();
      filtered.forEach(r => {
        const eng = r['Engagement Timeframe'] || 'Unknown';
        engMap.set(eng, (engMap.get(eng) || 0) + (r['Total Deposit'] || 0));
      });
      setEngagementData(Array.from(engMap.entries()).map(([name, totalDeposit]) => ({
        name,
        totalDeposit: totalDeposit / 1000000
      })));
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

      {/* KPI Cards */}
      <div className="grid grid-cols-6 gap-4 mb-6">
        <KPICard title="Total Deposit" value={getKPI('Total Deposit')} icon="🏦" />
        <KPICard title="Bank Deposit" value={getKPI('Bank Deposit')} icon="💰" />
        <KPICard title="Foreign Currency" value={getKPI('Foreign Currency Amount')} icon="🌍" />
        <KPICard title="Saving Account" value={getKPI('Saving Account Amount')} icon="📊" />
        <KPICard title="Checking Account" value={getKPI('Checking Account Amount')} icon="📝" />
        <KPICard title="Avg Risk" value={getKPI('Average Risk Score')} icon="⚠️" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-sm font-bold text-gray-700 mb-4">Bank Deposit by Income Band (M)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={incomeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="bankDeposit" fill="#1e3a5f" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-sm font-bold text-gray-700 mb-4">Total Deposit by Engagement Timeframe (M)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={engagementData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={60} />
              <Tooltip />
              <Bar dataKey="totalDeposit" fill="#1e3a5f" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 col-span-2">
          <h3 className="text-sm font-bold text-gray-700 mb-4">Total Deposit by Nationality (M)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={nationalityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="bankDeposit" stackId="a" fill="#1e3a5f" name="Bank Deposit" />
              <Bar dataKey="checking" stackId="a" fill="#2563eb" name="Checking" />
              <Bar dataKey="savings" stackId="a" fill="#3b82f6" name="Savings" />
              <Bar dataKey="foreign" stackId="a" fill="#60a5fa" name="Foreign Currency" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default DepositAnalysis;
