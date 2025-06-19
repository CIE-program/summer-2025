async function checkForTeamDuplicates(db, input) {
  const teamsCollection = db.collection('teams');

  const allEmails = [input.captain.email, ...input.members.map(m => m.email)];
  const allSrns = [input.captain.srn, ...input.members.map(m => m.srn)];

  const query = {
    $or: [
      { teamName: input.teamName },
      { 'captain.email': { $in: allEmails } },
      { 'captain.srn': { $in: allSrns } },
      { 'members.email': { $in: allEmails } },
      { 'members.srn': { $in: allSrns } }
    ]
  };

  const results = await teamsCollection.find(query).toArray();
  console.log(results)

  const duplicateEmails = new Set();
  const duplicateSrns = new Set();
  let teamNameConflict = false;

  for (const team of results) {
    if (team.teamName === input.teamName) {
      teamNameConflict = true;
    }

    const emailsToCheck = [
      team.captain.email,
      ...(team.members || []).map(m => m.email)
    ];
    emailsToCheck.forEach(email => {
      if (allEmails.includes(email)) {
        duplicateEmails.add(email);
      }
    });

    const srnsToCheck = [
      team.captain.srn,
      ...(team.members || []).map(m => m.srn)
    ];
    srnsToCheck.forEach(srn => {
      if (allSrns.includes(srn)) {
        duplicateSrns.add(srn);
      }
    });
  }

  return {
    hasDuplicates: teamNameConflict || duplicateEmails.size > 0 || duplicateSrns.size > 0,
    duplicates: {
      teamName: teamNameConflict || undefined,
      emails: Array.from(duplicateEmails),
      srns: Array.from(duplicateSrns)
    }
  };
}

module.exports = checkForTeamDuplicates;
