import React, { useState } from 'react';
import TeamOnboardingForm from './TeamOnboardingForm';
import WalletManagement from './WalletManagement';

const TeamManagement = () => {
  const [activeView, setActiveView] = useState<'menu' | 'onboarding' | 'walletmanagement'>('menu');

  return (
    <div className="bg-white p-6 rounded shadow">
      {activeView === 'menu' && (
        <>
          <h2 className="text-xl font-semibold mb-4">Team Management Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={() => setActiveView('onboarding')}
              className="p-4 bg-indigo-50 border border-indigo-200 rounded hover:shadow-md cursor-pointer transition text-left"
            >
              <h3 className="text-lg font-medium">Onboard Team</h3>
              <p className="text-sm text-gray-600">Create a new team</p>
            </button>

            <button
              onClick={() => setActiveView('walletmanagement')}
              className="p-4 bg-indigo-50 border border-indigo-200 rounded hover:shadow-md cursor-pointer transition text-left"
            >
              <h3 className="text-lg font-medium">Wallet Management</h3>
              <p className="text-sm text-gray-600">View or create wallets</p>
            </button>

            <button
              onClick={() => alert('Coming Soon')}
              className="p-4 bg-indigo-50 border border-indigo-200 rounded hover:shadow-md cursor-pointer transition text-left"
            >
              <h3 className="text-lg font-medium">View Team</h3>
              <p className="text-sm text-gray-600">See team details</p>
            </button>

            <button
              onClick={() => alert('Coming Soon')}
              className="p-4 bg-indigo-50 border border-indigo-200 rounded hover:shadow-md cursor-pointer transition text-left"
            >
              <h3 className="text-lg font-medium">Member Management</h3>
              <p className="text-sm text-gray-600">Manage team members</p>
            </button>

          </div>
        </>
      )}

      {activeView === 'onboarding' && (
        <>
          <div className="mb-4">
            <button
              onClick={() => setActiveView('menu')}
              className="text-sm text-blue-600 hover:underline"
            >
              ← Back to Team Management
            </button>
          </div>
          <TeamOnboardingForm />
        </>
      )}
      {activeView === 'walletmanagement' && (
        <>
          <div className="mb-4">
            <button
              onClick={() => setActiveView('menu')}
              className="text-sm text-blue-600 hover:underline"
            >
              ← Back to Team Management
            </button>
          </div>
          <WalletManagement />
        </>
      )}

    </div>
  );
};

export default TeamManagement;
