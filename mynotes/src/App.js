import {
  HashRouter as Router,
  Routes,
  Route,
} from "react-router-dom";

import './App.css';
import Header from './components/header';
import NotesListPage from './pages/NotesListPage';
import NotePage from './pages/NotePage';
import AskPage from './pages/AskPage';

function App() {
  return (
    <Router>
      <div className="container dark">
        <div className="app">
        <Header />
        <Routes>
          <Route path='/' element={ <NotesListPage/> } />
          <Route path='/note/:id' element={ <NotePage/> } />
          <Route path='/ask' element={ <AskPage/> } />
        </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
