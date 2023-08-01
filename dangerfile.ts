import { danger, warn } from 'danger';

const DEFAULT_MR_LENGTH_THRESHOLD = 10;

/**
 * warns when the MR contains too many files
 * @param threshold
 */
export function warnThatMRIsTooBig(threshold: number = DEFAULT_MR_LENGTH_THRESHOLD) {
    if (parseInt(danger.gitlab.mr.changes_count, 10) < threshold) {
        warn(
            ':exclamation: Merge Request size seems relatively large.'
            + ' If Merge Request contains multiple changes, split each into separate PR will helps faster, easier review'
        );
    }
}

warnThatMRIsTooBig();
