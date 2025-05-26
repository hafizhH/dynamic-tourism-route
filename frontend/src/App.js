import { useState } from 'react';
import './App.css';
import MainPage from './pages/MainPage';
import StartPage from './pages/StartPage';
import Loading from './components/Loading';


function App() {
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);

  const [mainData, setMainData] = useState(null);
  const [mainConfig, setMainConfig] = useState(null);

  return (
    <>
      {/* { (currentPage === 0) ? <StartPage setCurrentPage={setCurrentPage} /> : '' } */}
      <div className={(currentPage === 0) ? '' : 'hidden'}>
        <StartPage setCurrentPage={setCurrentPage} mainData={mainData} setMainData={setMainData} setMainConfig={setMainConfig} loading={loading} setLoading={setLoading} />
      </div>
      { (currentPage === 1) ? <MainPage setCurrentPage={setCurrentPage} mainData={mainData} setMainData={setMainData} mainConfig={mainConfig} loading={loading} setLoading={setLoading} /> : '' }
      <Loading show={loading} />
    </>
  );
}

export default App;
