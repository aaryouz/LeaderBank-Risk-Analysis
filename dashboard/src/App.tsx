import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Home from './pages/Home';
import LoanAnalysis from './pages/LoanAnalysis';
import DepositAnalysis from './pages/DepositAnalysis';
import Summary from './pages/Summary';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navigation />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/loan-analysis" element={<LoanAnalysis />} />
            <Route path="/deposit-analysis" element={<DepositAnalysis />} />
            <Route path="/summary" element={<Summary />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
