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
  error?: string;
}

interface DuplicateCheckResult {
  hasDuplicates: boolean;
  duplicateEmails: string[];
  message?: string;
}

// Check if email IDs already exist with wallet associations
export const checkForDuplicateEmails = async (emails: string[]): Promise<DuplicateCheckResult> => {
  try {
    // TODO: Replace with your actual API endpoint
    const response = await fetch('/api/teams/check-duplicates', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ emails }),
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const errorData = await response.json();
      return {
        hasDuplicates: false,
        duplicateEmails: [],
        message: errorData.message || 'Failed to check for duplicates'
      };
    }
  } catch (error) {
    console.error('Duplicate check error:', error);
    
    // For demonstration purposes, simulate the check
    // TODO: Remove this when actual API is implemented
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Simulate some emails already existing (for testing)
    const existingEmails = ['test@pes.edu', 'existing@pes.edu'];
    const duplicates = emails.filter(email => existingEmails.includes(email.toLowerCase()));
    
    return {
      hasDuplicates: duplicates.length > 0,
      duplicateEmails: duplicates,
      message: duplicates.length > 0 
        ? `The following email(s) are already registered with wallet IDs: ${duplicates.join(', ')}`
        : undefined
    };
  }
};


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
    } else {
      console.log("Saving to Database failed")
      const errorData = await response.json();
      return {
        success: false,
        error: errorData.message || 'Failed to save team data'
      };
    }
  } catch (error) {
    console.error('Database save error:', error);
    return {
      success: false,
      error: 'Error creating Team'
    };
  }
};


// Method 2: Direct MongoDB connection scaffolding (for backend implementation)
/*
// This code would typically be in your backend/server file

import { MongoClient, Db, Collection } from 'mongodb';

class DatabaseService {
  private client: MongoClient;
  private db: Db;
  private teamsCollection: Collection;

  constructor(connectionString: string, databaseName: string) {
    this.client = new MongoClient(connectionString);
  }

  async connect(): Promise<void> {
    try {
      await this.client.connect();
      this.db = this.client.db('ignite_teams');
      this.teamsCollection = this.db.collection('teams');
      console.log('Connected to MongoDB');
    } catch (error) {
      console.error('MongoDB connection error:', error);
      throw error;
    }
  }

  // Check for duplicate emails with wallet associations
  async checkDuplicateEmails(emails: string[]): Promise<DuplicateCheckResult> {
    try {
      const duplicates = await this.teamsCollection.find({
        $or: [
          { 'captain.email': { $in: emails } },
          { 'members.email': { $in: emails } }
        ],
        walletAddress: { $exists: true, $ne: null }
      }).toArray();

      const duplicateEmails: string[] = [];
      
      duplicates.forEach(team => {
        if (emails.includes(team.captain.email)) {
          duplicateEmails.push(team.captain.email);
        }
        team.members.forEach(member => {
          if (emails.includes(member.email)) {
            duplicateEmails.push(member.email);
          }
        });
      });

      const uniqueDuplicates = [...new Set(duplicateEmails)];

      return {
        hasDuplicates: uniqueDuplicates.length > 0,
        duplicateEmails: uniqueDuplicates,
        message: uniqueDuplicates.length > 0 
          ? `The following email(s) are already registered with wallet IDs: ${uniqueDuplicates.join(', ')}`
          : undefined
      };
    } catch (error) {
      console.error('Error checking duplicate emails:', error);
      return {
        hasDuplicates: false,
        duplicateEmails: [],
        message: 'Error checking for duplicate emails'
      };
    }
  }

  async saveTeam(teamData: TeamData): Promise<any> {
    try {
      const result = await this.teamsCollection.insertOne({
        ...teamData,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      
      return {
        success: true,
        data: {
          _id: result.insertedId,
          ...teamData
        }
      };
    } catch (error) {
      console.error('Error saving team:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async getTeamByEmail(email: string): Promise<any> {
    try {
      const team = await this.teamsCollection.findOne({
        $or: [
          { 'captain.email': email },
          { 'members.email': email }
        ]
      });
      return team;
    } catch (error) {
      console.error('Error fetching team by email:', error);
      return null;
    }
  }

  async getTeamByName(teamName: string): Promise<any> {
    try {
      const team = await this.teamsCollection.findOne({ teamName });
      return team;
    } catch (error) {
      console.error('Error fetching team:', error);
      return null;
    }
  }

  async getAllTeams(): Promise<any[]> {
    try {
      const teams = await this.teamsCollection.find({}).toArray();
      return teams;
    } catch (error) {
      console.error('Error fetching teams:', error);
      return [];
    }
  }

  async updateTeam(teamId: string, updateData: Partial<TeamData>): Promise<any> {
    try {
      const result = await this.teamsCollection.updateOne(
        { _id: teamId },
        { 
          $set: {
            ...updateData,
            updatedAt: new Date()
          }
        }
      );
      
      return {
        success: result.modifiedCount > 0,
        data: result
      };
    } catch (error) {
      console.error('Error updating team:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async disconnect(): Promise<void> {
    await this.client.close();
  }
}

// Usage example:
const dbService = new DatabaseService(
  'mongodb://localhost:27017', // or your MongoDB connection string
  'ignite_teams'
);

// Initialize connection
await dbService.connect();

// Express.js API endpoint example for duplicate check:
app.post('/api/teams/check-duplicates', async (req, res) => {
  try {
    const { emails } = req.body;
    const result = await dbService.checkDuplicateEmails(emails);
    res.json(result);
  } catch (error) {
    res.status(500).json({
      hasDuplicates: false,
      duplicateEmails: [],
      message: 'Internal server error'
    });
  }
});

// Express.js API endpoint example:
app.post('/api/teams', async (req, res) => {
  try {
    const teamData = req.body;
    const result = await dbService.saveTeam(teamData);
    
    if (result.success) {
      res.status(201).json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

app.get('/api/teams', async (req, res) => {
  try {
    const teams = await dbService.getAllTeams();
    res.json({
      success: true,
      data: teams
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

export default DatabaseService;
*/

// Method 3: MongoDB Atlas/Cloud connection example with duplicate check
/*
const MONGODB_URI = process.env.MONGODB_URI || 'your-mongodb-atlas-connection-string';

const connectToMongoDB = async () => {
  try {
    const client = new MongoClient(MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    
    await client.connect();
    return client.db('ignite_teams');
  } catch (error) {
    console.error('MongoDB connection failed:', error);
    throw error;
  }
};

export const checkDuplicateEmailsInMongoDB = async (emails: string[]): Promise<DuplicateCheckResult> => {
  const db = await connectToMongoDB();
  const collection = db.collection('teams');
  
  const duplicates = await collection.find({
    $or: [
      { 'captain.email': { $in: emails } },
      { 'members.email': { $in: emails } }
    ],
    walletAddress: { $exists: true, $ne: null }
  }).toArray();

  const duplicateEmails: string[] = [];
  
  duplicates.forEach(team => {
    if (emails.includes(team.captain.email)) {
      duplicateEmails.push(team.captain.email);
    }
    team.members.forEach(member => {
      if (emails.includes(member.email)) {
        duplicateEmails.push(member.email);
      }
    });
  });

  const uniqueDuplicates = [...new Set(duplicateEmails)];

  return {
    hasDuplicates: uniqueDuplicates.length > 0,
    duplicateEmails: uniqueDuplicates,
    message: uniqueDuplicates.length > 0 
      ? `The following email(s) are already registered with wallet IDs: ${uniqueDuplicates.join(', ')}`
      : undefined
  };
};

export const saveTeamToMongoDB = async (teamData: TeamData) => {
  const db = await connectToMongoDB();
  const collection = db.collection('teams');
  
  const result = await collection.insertOne({
    ...teamData,
    _id: new ObjectId(),
    createdAt: new Date(),
    updatedAt: new Date()
  });
  
  return result;
};
*/