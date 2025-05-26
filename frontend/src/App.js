import { useState } from 'react';
import './App.css';
import MainPage from './pages/MainPage';
import StartPage from './pages/StartPage';


function App() {
  const [currentPage, setCurrentPage] = useState(0);

  return (
    <>
      {/* { (currentPage === 0) ? <StartPage setCurrentPage={setCurrentPage} /> : '' } */}
      <div className={(currentPage === 0) ? '' : 'hidden'}>
        <StartPage setCurrentPage={setCurrentPage} />
      </div>
      { (currentPage === 1) ? <MainPage setCurrentPage={setCurrentPage} /> : '' }
      {/* <div className={(currentPage === 1) ? '' : 'hidden'}>
        <MainPage setCurrentPage={setCurrentPage} />
      </div> */}
    </>
  );
}

export default App;
