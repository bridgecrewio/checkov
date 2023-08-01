const { danger, fail, schedule } = require('danger');

async function failOnPTTitle() {
  console.log('Running Danger...');
  if (danger.github?.pr.title.length < 1000) {
    fail('PR title is too short. Please provide a descriptive title.');
  }
}
schedule(failOnPTTitle);
