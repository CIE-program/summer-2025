import React from 'react';
import { Flame, GraduationCap } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-orange-400 to-red-500 rounded-lg">
                <Flame className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">CIE Ignite</h1>
                <p className="text-sm text-gray-600">Innovation Platform</p>
              </div>
            </div>
            
            <div className="hidden md:flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg">
                <GraduationCap className="h-8 w-8 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">PES University</h2>
                <p className="text-sm text-gray-600">Center for Innovation and Entrepreneurship</p>
              </div>
            </div>
          </div>
          
          <div className="text-right">
            <h3 className="text-lg font-semibold text-gray-900">Student Corner</h3>
            <p className="text-sm text-gray-600">Dream Build Repeat</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;