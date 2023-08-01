const { danger, fail } = require('danger');

module.exports = async () => {
  // Add your Danger rules and checks here
  // For example, you can fail the build if the PR title is too short
  if (danger.github?.pr.title.length < 10) {
    fail('PR title is too short. Please provide a descriptive title.');
  }
};
