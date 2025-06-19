import React, { useState } from 'react';
import { Copy, RefreshCcw } from 'lucide-react';
import { Magic } from 'magic-sdk';

type ViewMode = 'wallet' | 'create' | 'transfer';

const WalletManagement: React.FC = () => {
  const [view, setView] = useState<ViewMode>('wallet');
  const [network] = useState('Polygon (Amoy Testnet)');
  const [address, setUserAddress] = useState<string>('');
  const [balance, setBalance] = useState<number>(12); // Adjust for testing
  const [copied, setCopied] = useState(false);
  const [email, setEmail] = useState('');
  const [receiver, setReceiver] = useState('');
  const [amount, setAmount] = useState('');

  const magic = new Magic('pk_live_6788B52AA093D198');

  const copyAddress = async () => {
    await navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const refreshBalance = () => {
    setBalance(prev => prev); // Replace with fetchBalance logic
  };

  const handleCreateWallet = async() => {
    try{
    console.log('Create wallet for', email);
    const accounts: string[] = await magic.wallet.connectWithUI();
    setUserAddress(accounts[0]);
    console.log("Created Wallet with address:", accounts[0]);
    }catch (error) {
      console.error("Wallet Creation error:", error);
    }
  };

  const handleSendTokens = () => {
    console.log('Send', amount, 'POL to', receiver);
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-lg space-y-6">
      {/* Top Buttons */}
      <div className="flex justify-between mb-4">
        <button
          onClick={() => setView('create')}
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
        >
          Create Wallet
        </button>
        <button
          onClick={() => setView('transfer')}
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          Transfer Tokens
        </button>
      </div>

      {/* Wallet Info */}
      {view === 'wallet' && (
        <div className="border rounded-lg p-4 bg-purple-50">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-semibold">Wallet</h2>
            <button className="text-red-600 text-sm">Disconnect</button>
          </div>
          <p className="text-sm text-green-600 mb-2">● Connected to {network}</p>

          <div className="mb-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <div className="flex items-center justify-between bg-gray-100 p-2 rounded">
              <span className="truncate text-xs">{address}</span>
              <button
                onClick={copyAddress}
                className="text-blue-600 text-xs hover:underline"
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Balance</label>
            <div className="flex items-center justify-between bg-gray-100 p-2 rounded">
              <span className="text-sm">{balance} POL </span>
              <button
                onClick={refreshBalance}
                className="text-blue-600 text-xs hover:underline flex items-center"
              >
                <RefreshCcw className="w-3 h-3 mr-1" /> Refresh
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Wallet Form */}
      {view === 'create' && (
        <div className="border rounded-lg p-4 bg-blue-50">
          <h3 className="text-md font-semibold mb-4">Create Wallet</h3>
          <div className="mb-4">
            <input
              type="email"
              placeholder="Enter email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded text-sm"
            />
          </div>
          <button
            onClick={handleCreateWallet}
            className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700"
          >
            Submit
          </button>
        </div>
      )}

      {/* Transfer Tokens */}
      {view === 'transfer' && (
        <div className="border rounded-lg p-4 bg-purple-50">
          <h3 className="text-md font-semibold mb-4">Send Transaction</h3>

          <div className="mb-4">
            <input
              type="text"
              placeholder="Receiving Address"
              value={receiver}
              onChange={(e) => setReceiver(e.target.value)}
              className="w-full px-3 py-2 border rounded text-sm"
            />
          </div>

          <div className="mb-4">
            <input
              type="number"
              placeholder="Amount (MATIC)"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-3 py-2 border rounded text-sm"
            />
          </div>

          <button
            onClick={handleSendTokens}
            disabled={balance < 10}
            className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
          >
            Send Transaction
          </button>
        </div>
      )}

      {/* Go back to wallet view */}
      {view !== 'wallet' && (
        <div className="text-center pt-2">
          <button
            onClick={() => setView('wallet')}
            className="text-sm text-blue-600 hover:underline"
          >
            ← Back to Wallet
          </button>
        </div>
      )}
    </div>
  );
};

export default WalletManagement;
