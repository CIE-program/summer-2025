import React from 'react';
import { Trash2, User } from 'lucide-react';
import FormField from './FormField';

interface TeamMember {
  id: number;
  srn: string;
  name: string;
  email: string;
}

interface TeamMemberCardProps {
  member: TeamMember;
  onUpdate: (id: number, field: keyof Omit<TeamMember, 'id'>, value: string) => void;
  onRemove: (id: number) => void;
  errors: {
    srn?: string;
    name?: string;
    email?: string;
  };
}

const TeamMemberCard: React.FC<TeamMemberCardProps> = ({
  member,
  onUpdate,
  onRemove,
  errors
}) => {
  return (
    <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <User className="h-5 w-5 text-gray-600" />
          <h3 className="font-medium text-gray-900">Team Member</h3>
        </div>
        
        <button
          type="button"
          onClick={() => onRemove(member.id)}
          className="text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded-lg transition-colors duration-200"
          title="Remove team member"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <FormField
          label="SRN"
          value={member.srn}
          onChange={(value) => onUpdate(member.id, 'srn', value)}
          placeholder="PES1UG20CS002"
          maxLength={20}
          error={errors.srn}
        />
        
        <FormField
          label="Name"
          value={member.name}
          onChange={(value) => onUpdate(member.id, 'name', value)}
          placeholder="Full name"
          maxLength={50}
          error={errors.name}
        />
        
        <FormField
          label="Email"
          value={member.email}
          onChange={(value) => onUpdate(member.id, 'email', value)}
          placeholder="name@pes.edu"
          maxLength={30}
          error={errors.email}
          type="email"
        />
      </div>
    </div>
  );
};

export default TeamMemberCard;