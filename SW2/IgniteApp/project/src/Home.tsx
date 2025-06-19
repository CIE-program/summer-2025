import React, { useState } from 'react'
import TeamManagement from './components/TeamManagement';

const Home = () => {
  const [selectedSection, setSelectedSection] = useState('TeamManagement')

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-center">Innovation Dashboard</h1>

      {/* Section Selector */}
      <div className="flex justify-center gap-4 mb-8">
        <button
          onClick={() => setSelectedSection('TeamManagement')}
          className={`px-4 py-2 rounded ${
            selectedSection === 'TeamManagement' ? 'bg-indigo-600 text-white' : 'bg-white border'
          }`}
        >
          Team Management
        </button>
        <button
          onClick={() => setSelectedSection('IdeaSummary')}
          className={`px-4 py-2 rounded ${
            selectedSection === 'IdeaSummary' ? 'bg-indigo-600 text-white' : 'bg-white border'
          }`}
        >
          Idea Summary
        </button>
        <button
          onClick={() => setSelectedSection('Leaderboard')}
          className={`px-4 py-2 rounded ${
            selectedSection === 'Leaderboard' ? 'bg-indigo-600 text-white' : 'bg-white border'
          }`}
        >
          Leaderboard & Points
        </button>
      </div>

      {/* Section Renderer */}
      {selectedSection === 'TeamManagement' && <TeamManagement />}
      {selectedSection === 'IdeaSummary' && <p>🚧 Idea Summary - Coming Soon</p>}
      {selectedSection === 'Leaderboard' && <p>🚧 Leaderboard - Coming Soon</p>}
    </div>
  )
}

export default Home
