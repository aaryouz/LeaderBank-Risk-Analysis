import Papa from 'papaparse';

export interface KPISummary {
  KPI: string;
  Value: number;
  Formatted: string;
}

export interface KPIByDimension {
  [key: string]: string | number;
}

export interface BankingRecord {
  'Client ID': string;
  Name: string;
  Age: number;
  Nationality: string;
  'Fee Structure': string;
  'Loyalty Classification': string;
  'Estimated Income': number;
  'Amount of Credit Cards': number;
  'Credit Card Balance': number;
  'Bank Loans': number;
  'Bank Deposits': number;
  'Checking Accounts': number;
  'Saving Accounts': number;
  'Foreign Currency Account': number;
  'Business Lending': number;
  'Risk Weighting': number;
  BRId: number;
  GenderId: number;
  IAId: number;
  'Engagement Days': number;
  'Engagement Timeframe': string;
  'Income Band': string;
  'Total Loan': number;
  'Total Deposit': number;
  'Total Fees': number;
  'Joined Bank': string;
}

export async function loadCSV<T>(filename: string): Promise<T[]> {
  const response = await fetch(`/${filename}`);
  const text = await response.text();

  return new Promise((resolve) => {
    Papa.parse(text, {
      header: true,
      dynamicTyping: true,
      complete: (results) => {
        resolve(results.data as T[]);
      },
    });
  });
}

export async function loadKPISummary(): Promise<Map<string, { value: number; formatted: string }>> {
  const data = await loadCSV<KPISummary>('kpi_summary.csv');
  const kpiMap = new Map();

  data.forEach((row) => {
    if (row.KPI) {
      kpiMap.set(row.KPI, {
        value: row.Value,
        formatted: row.Formatted,
      });
    }
  });

  return kpiMap;
}

export async function loadKPIByNationality(): Promise<KPIByDimension[]> {
  return loadCSV('kpi_by_nationality.csv');
}

export async function loadKPIByIncomeBand(): Promise<KPIByDimension[]> {
  return loadCSV('kpi_by_income_band.csv');
}

export async function loadKPIByEngagement(): Promise<KPIByDimension[]> {
  return loadCSV('kpi_by_engagement_timeframe.csv');
}

export async function loadCleanedBanking(): Promise<BankingRecord[]> {
  return loadCSV('cleaned_banking.csv');
}

export function formatCurrency(value: number): string {
  if (value >= 1000000000) {
    return `$${(value / 1000000000).toFixed(2)}B`;
  } else if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(2)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(2)}K`;
  }
  return `$${value.toFixed(2)}`;
}

export function formatNumber(value: number): string {
  return value.toLocaleString();
}

export interface FilterState {
  gender: 'All' | 'Male' | 'Female';
  relationship: string;
  advisor: string;
  timePeriod: string;
}

export function filterData(data: BankingRecord[], filters: FilterState): BankingRecord[] {
  return data.filter(record => {
    if (filters.gender !== 'All') {
      const genderId = filters.gender === 'Male' ? 1 : 2;
      if (record.GenderId !== genderId) return false;
    }

    if (filters.relationship !== 'All') {
      if (record.BRId !== parseInt(filters.relationship)) return false;
    }

    if (filters.advisor !== 'All') {
      if (record.IAId !== parseInt(filters.advisor)) return false;
    }

    if (filters.timePeriod !== 'All') {
      if (record['Engagement Timeframe'] !== filters.timePeriod) return false;
    }

    return true;
  });
}

export function calculateKPIs(data: BankingRecord[]) {
  const totalClients = data.length;
  const totalLoan = data.reduce((sum, r) => sum + (r['Total Loan'] || 0), 0);
  const bankLoan = data.reduce((sum, r) => sum + (r['Bank Loans'] || 0), 0);
  const businessLending = data.reduce((sum, r) => sum + (r['Business Lending'] || 0), 0);
  const creditCards = data.reduce((sum, r) => sum + (r['Credit Card Balance'] || 0), 0);
  const totalDeposit = data.reduce((sum, r) => sum + (r['Total Deposit'] || 0), 0);
  const bankDeposit = data.reduce((sum, r) => sum + (r['Bank Deposits'] || 0), 0);
  const checking = data.reduce((sum, r) => sum + (r['Checking Accounts'] || 0), 0);
  const savings = data.reduce((sum, r) => sum + (r['Saving Accounts'] || 0), 0);
  const foreign = data.reduce((sum, r) => sum + (r['Foreign Currency Account'] || 0), 0);
  const totalCC = data.reduce((sum, r) => sum + (r['Amount of Credit Cards'] || 0), 0);
  const totalFees = data.reduce((sum, r) => sum + (r['Total Fees'] || 0), 0);
  const avgRisk = data.length > 0 ? data.reduce((sum, r) => sum + (r['Risk Weighting'] || 0), 0) / data.length : 0;

  return {
    'Total Clients': { value: totalClients, formatted: formatNumber(totalClients) },
    'Total Loan': { value: totalLoan, formatted: formatCurrency(totalLoan) },
    'Bank Loan': { value: bankLoan, formatted: formatCurrency(bankLoan) },
    'Business Lending': { value: businessLending, formatted: formatCurrency(businessLending) },
    'Credit Cards Balance': { value: creditCards, formatted: formatCurrency(creditCards) },
    'Total Deposit': { value: totalDeposit, formatted: formatCurrency(totalDeposit) },
    'Bank Deposit': { value: bankDeposit, formatted: formatCurrency(bankDeposit) },
    'Checking Account Amount': { value: checking, formatted: formatCurrency(checking) },
    'Saving Account Amount': { value: savings, formatted: formatCurrency(savings) },
    'Foreign Currency Amount': { value: foreign, formatted: formatCurrency(foreign) },
    'Total CC Amount': { value: totalCC, formatted: formatNumber(totalCC) },
    'Total Fees': { value: totalFees, formatted: formatCurrency(totalFees) },
    'Average Risk Score': { value: avgRisk, formatted: `${avgRisk.toFixed(1)}/100` },
  };
}
