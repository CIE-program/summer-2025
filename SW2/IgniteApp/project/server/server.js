require('dotenv').config();
const express = require('express');
const { MongoClient } = require('mongodb');
const cors = require('cors');
const checkForTeamDuplicates = require('./services/checkTeamDuplicates');

// Replace this with your actual MongoDB Atlas URI
const MONGO_URI = process.env.MONGO_URI;

const app = express();
const PORT = process.env.SERVER_PORT;

app.use(cors());
app.use(express.json()); // For parsing JSON in POST requests

let db;

// Connect to MongoDB Atlas
MongoClient.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(client => {
    db = client.db('CIEIgniteDB');
    console.log('Connected to CIEIgniteDB MongoDB Atlas');
  })
  .catch(err => console.error('MongoDB connection error:', err));


// Define a POST route for Adding a New Team
app.post('/add_team', async (req, res) => {
    console.log('add_team API is called')
  try{
    const teamData = req.body;
    if (!teamData) {
        return res.status(400).json({ error: 'No Team Data Provided' });
    }
    console.log('Perform Duplicate Checks...');
    const duplicates = await checkForTeamDuplicates(db, {
      teamName: teamData.teamName,
      captain: teamData.captain,
      members: teamData.members
    });

    if (duplicates && duplicates.hasDuplicates) {
      console.log('Duplicate Email, SRN, or Team Name found');
      return res.status(409).json({
        success: false,
        message: 'Duplicate Email, SRN or Team Name found. Team not created.',
        data: duplicates
      });
    }    
    console.log('No Duplicates found...');
    const result = await db.collection('teams').insertOne(teamData);
    return res.status(200).json({ message: 'Team successfully added.', teamID: result.insertedId });
  } catch (err) {
    console.error('Insert failed:', err);
    res.status(500).json({ error: 'Insert failed' });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
