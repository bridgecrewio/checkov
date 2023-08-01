import { danger, warn, fail, schedule } from 'danger';

// Add your Danger rules and checks here
export default async () => {
  // For example, you can fail the build if the PR title is too short
  if (danger.github?.pr.title.length < 10) {
    warn('PR title is too short. Please provide a descriptive title.');
  }
};