import yaml
from datetime import datetime

def is_expired(expiry_date):
    current_date = datetime.now().date()
    expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    return current_date > expiry_date

try:
    # Load the YAML content from the file
    with open('.checkovignore', 'r') as file:
        data = yaml.safe_load(file)

    # Extract the 'id' values from the ignore list that are not expired
    ids = [rule['id'] for rule in data['ignore'] if not is_expired(rule['expiry'])]

    if ids:
        # Join the ids into a comma-separated string
        skip_checks = ','.join(ids)
    else:
        skip_checks = "null"

    # Get the total number of ids
    total_ids = len(ids)

    # Print the results in a way that can be captured by the shell script
    print(f"SKIP_CHECKS: {skip_checks}")
    print(f"TOTAL_SKIPPED: {total_ids}")

    # Set the pipeline variable for other tasks
    print(f"##vso[task.setvariable variable=SKIP_CHECKS]{skip_checks}")

except FileNotFoundError:
    # Handle the case where the file is not found
    skip_checks = "null"
    print("[INFO], Checkov ignore file not found, assign SKIP_CHECKS as null, for error handling when running checkov scan...")
    print(f"##vso[task.setvariable variable=SKIP_CHECKS]{skip_checks}")
