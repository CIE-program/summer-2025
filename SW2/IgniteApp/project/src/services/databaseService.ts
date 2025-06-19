/* eslint-disable @typescript-eslint/no-unused-vars */
// Database service for storing team data
// Includes both direct MongoDB connection and API-based approaches

interface TeamDataOld {
  teamName: string;
  idea: string;
  ideaDescription: string;
  captain: {
    srn: string;
    name: string;
    email: string;
  };
  members: Array<{
    srn: string;
    name: string;
    email: string;
  }>;
  walletAddress: string;
  createdAt: string;
}

interface TeamData {
  teamName: string;
  idea: string;
  ideaDescription: string;
  captain: {
    srn: string;
    name: string;
    email: string;
    walletAddress: string;
  };
  members: Array<{
    srn: string;
    name: string;
    email: string;
    walletAddress: string;
  }>;
  createdAt: string;
}

interface DatabaseResult {
  success: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: any;
  message?: string;
}

interface DuplicateCheckResult {
  hasDuplicates: boolean;
  duplicates:{
    teamName?: boolean;
    emails: string[];
    srns: string[];
  };
  message?: string;
}

// Method 1: API-based approach (Recommended for production)
export const saveTeamToDatabase = async (teamData: TeamData): Promise<DatabaseResult> => {
  console.log("saveTeamToDatabase called")
  try {
    // TODO: Replace with your actual API endpoint
    const response = await fetch('http://localhost:4000/add_team', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(teamData),
    });

    if (response.ok) {
      console.log("Saving to Database is OK")
      const data = await response.json();
      return {
        success: true,
        data
      };
    } else if (response.status === 409){
        const errorData:DatabaseResult = await response.json();
        console.warn('Duplicates detected: ', errorData);
        return errorData;
    } else {
      console.log("Saving to Database failed")
      const errorData = await response.json();
      return {
        success: false,
        message: errorData.message || 'Failed to save team data'
      };
    }
  } catch (error) {
    console.error('Database save error:', error);
    return {
      success: false,
      message: 'Error creating Team'
    };
  }
};