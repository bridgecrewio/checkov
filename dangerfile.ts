const { danger, fail, schedule } = require('danger');

async function runDanger() {
  console.log('Running Danger...');
}
schedule(runDanger);
