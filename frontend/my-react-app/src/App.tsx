import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ControlPanel from './components/ControlPanel/ControlPanel';
import LoginPage from './pages/LoginPage/LoginPage';
import AuthGuard from './components/AuthGuard/AuthGuard';
import PingTest from './components/PingTest/PingTest';

const App: React.FC = () => {
  return (
    <PingTest></PingTest>
  );
};

export default App;
