# API Key Warning System

## Overview

The API key warning system alerts users when they use CLI parameters that require connection to Bridgecrew/Prisma Cloud platform but no API key is provided. This helps users understand why certain features may not work as expected.

## Parameters Requiring API Key

### Severity-Based Filtering
When using severity codes (CRITICAL, HIGH, MEDIUM, MODERATE, LOW, INFO, NONE) with the following parameters:
- `--check <severity>`
- `--skip-check <severity>`
- `--hard-fail-on <severity>`
- `--soft-fail-on <severity>`

**Warning Message:**
```
⚠️ Severity-based filtering was used without an API key: --check HIGH

Without an API key, Checkov uses estimated defaults based on check categories rather than 
official severities from the platform. Results may differ from the Prisma Cloud platform.

To use official policy severities, provide a Bridgecrew or Prisma Cloud API key using 
the --bc-api-key flag.
```

**Note:** The severity codes must match exactly (case-insensitive). Check IDs like `CKV_AWS_1` will not trigger warnings.

### Policy Metadata Filter
When using `--policy-metadata-filter <filter>`:

**Warning Message:**
```
⚠️ Parameter --policy-metadata-filter requires an API key to function properly. 
Reason: Filter policies by metadata from Prisma Cloud platform. 
Use --bc-api-key to provide a Bridgecrew or Prisma Cloud API key.
```

### Enforcement Rules
When using `--use-enforcement-rules`:

**Warning Message:**
```
⚠️ Parameter --use-enforcement-rules requires an API key to function properly. 
Reason: Apply enforcement rules from Prisma Cloud platform. 
Use --bc-api-key to provide a Bridgecrew or Prisma Cloud API key.
```

### Docker Image Scanning
When using `--docker-image <image>`:

**Warning Message:**
```
⚠️ Parameter --docker-image requires an API key to function properly. 
Reason: Upload container scan results to platform. 
Use --bc-api-key to provide a Bridgecrew or Prisma Cloud API key.
```

### Support/Debug Mode
When using `--support`:

**Warning Message:**
```
⚠️ Parameter --support requires an API key to function properly. 
Reason: Debug log upload requires platform integration. 
Use --bc-api-key to provide a Bridgecrew or Prisma Cloud API key.
```

## Implementation Details

### Module: `checkov/common/util/api_key_warnings.py`

#### Key Functions:

1. **`check_for_severity_filtering_without_api_key(config, has_api_key)`**
   - Detects severity codes in filtering parameters
   - Returns `True` if warning was issued
   - Called before scan execution

2. **`check_for_api_key_usage_warnings(config, has_api_key)`**
   - Main function checking all API-dependent parameters
   - Calls severity filtering check
   - Checks other parameters requiring API key

3. **`warn_about_missing_metadata_without_api_key()`**
   - General informational message about limited metadata
   - Called when no API key is present

### Severity Codes Set:
```python
SEVERITY_CODES = {'CRITICAL', 'HIGH', 'MEDIUM', 'MODERATE', 'LOW', 'INFO', 'NONE'}
```

### Integration Point:
Warnings are triggered in `checkov/main.py` in the `run()` method, immediately after API key configuration:

```python
# Check for API key warnings
check_for_api_key_usage_warnings(self.config, bool(self.config.bc_api_key))
```

## Examples

### Example 1: Severity Filtering Without API Key
```bash
checkov -f main.tf --check HIGH
```
Output:
```
⚠️ Severity-based filtering was used without an API key: --check HIGH
[scan continues with estimated severity defaults]
```

### Example 2: Multiple Severity Parameters
```bash
checkov -f main.tf --check HIGH --hard-fail-on CRITICAL
```
Output:
```
⚠️ Severity-based filtering was used without an API key: --check HIGH, --hard-fail-on CRITICAL
[scan continues with estimated severity defaults]
```

### Example 3: Combined with Other Parameters
```bash
checkov -f main.tf --check HIGH --policy-metadata-filter policy.label=security
```
Output:
```
⚠️ Severity-based filtering was used without an API key: --check HIGH
⚠️ Parameter --policy-metadata-filter requires an API key to function properly
[scan continues with limited functionality]
```

### Example 4: With API Key (No Warnings)
```bash
checkov -f main.tf --check HIGH --bc-api-key xxxx-yyyy-zzzz
```
Output:
```
[scan runs normally without warnings]
```

## Fallback Behavior

When severity-based filtering is used without an API key:
1. Checkov continues scanning normally
2. Uses default severities based on check categories (see `checkov/common/checks/default_severities.py`)
3. Results may differ from platform-based severities
4. Users are warned about the limitation

## Testing

Unit tests are available in `tests/common/util/test_api_key_warnings.py`:
- Test severity filtering with various parameters
- Test API key presence/absence
- Test multiple warnings simultaneously
- Test that check IDs don't trigger warnings

Run tests:
```bash
python -m unittest tests.common.util.test_api_key_warnings -v
```

## Benefits

1. **User Awareness**: Users understand when features require API key
2. **Clear Guidance**: Messages explain how to enable full functionality
3. **Non-Breaking**: Scans continue with warnings, not errors
4. **Comprehensive**: Covers all API-dependent parameters
5. **Maintainable**: Centralized warning logic in one module
