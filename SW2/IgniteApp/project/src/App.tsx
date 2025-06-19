import React from 'react';
import TeamOnboardingForm from './components/TeamOnboardingForm';
import Home from './Home'
import Header from './components/Header';


function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Home />
      </main>
    </div>
  );
}

export default App;