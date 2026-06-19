"""
Utility to strip common build log prefixes from file content.

When scanning build logs for secrets, each line may be prefixed with timestamps
and log metadata (e.g., "2026-01-07 09:41:37.553 | DEBUG | crypto      | ").
These prefixes break multiline regex matching for secrets (like private keys)
because the detectors expect clean content between markers.

This module provides functions to detect and strip such prefixes, enabling
secret detection across all detectors when scanning build log files.
"""
from __future__ import annotations

import re
from typing import Optional

# Common build log prefix patterns:
# - Timestamps: 2026-01-07 09:41:37.553, 2026-01-07T09:41:37.553Z
# - Log levels: INFO, DEBUG, WARN, ERROR, TRACE, FATAL
# - Separators: |, -, [], etc.
# - Module names: crypto, main, etc.
# Examples:
#   "2026-01-07 09:41:37.553 | DEBUG | crypto      | actual content"
#   "[2026-01-07 09:41:37] [INFO] actual content"
#   "2026-01-07T09:41:37.553Z INFO  actual content"
#   "09:41:37.553 DEBUG actual content"

# Pattern for pipe-separated log prefixes (most common in CI/CD logs)
# e.g., "2026-01-07 09:41:37.553 | DEBUG | crypto      | "
_PIPE_LOG_PREFIX = re.compile(
    r'^'
    r'(?:'
    # Date-time with various separators
    r'\d{4}[-/]\d{2}[-/]\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?'
    r'|'
    # Time-only prefix
    r'\d{2}:\d{2}:\d{2}(?:[.,]\d+)?'
    r')'
    # Pipe-separated fields (log level, module, etc.)
    r'(?:\s*\|\s*\w[\w./\- ]*)*'
    # Final pipe separator before actual content
    r'\s*\|\s*'
)

# Pattern for space-separated log prefixes
# e.g., "2026-01-07 09:41:37.553 DEBUG crypto - "
_SPACE_LOG_PREFIX = re.compile(
    r'^'
    r'(?:'
    r'\d{4}[-/]\d{2}[-/]\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?'
    r'|'
    r'\d{2}:\d{2}:\d{2}(?:[.,]\d+)?'
    r')'
    r'\s+'
    # Log level (required for space-separated to avoid false positives)
    r'(?:TRACE|DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|SEVERE|FINE|FINER|FINEST)\s+'
    # Optional module/category and separator
    r'(?:[\w./-]+\s+(?:[-:]\s+)?)?'
)

# Pattern for bracket-style log prefixes
# e.g., "[2026-01-07 09:41:37] [INFO] [crypto] "
_BRACKET_LOG_PREFIX = re.compile(
    r'^'
    r'(?:\[[\d\-/:T., +Z]+\]\s*)'
    r'(?:\[(?:TRACE|DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|SEVERE)\]\s*)?'
    r'(?:\[[\w./-]+\]\s*)*'
)

_LOG_PREFIX_PATTERNS = [_PIPE_LOG_PREFIX, _SPACE_LOG_PREFIX, _BRACKET_LOG_PREFIX]


def strip_log_prefix(line: str) -> str:
    """Strip common build log prefixes from a single line.

    Removes timestamp, log level, and module prefixes commonly found in build logs.
    Returns the line content after the prefix.
    """
    for pattern in _LOG_PREFIX_PATTERNS:
        stripped = pattern.sub('', line)
        if stripped != line:
            return stripped
    return line


def has_log_prefixes(content: str) -> bool:
    """Check if file content appears to be a build log with line prefixes.

    Samples non-empty lines and checks if a significant portion have log prefixes.
    Returns True if the file appears to be a log file with prefixes.
    """
    lines = content.split('\n')
    prefix_count = 0
    checked = 0
    sample_size = min(len(lines), 30)  # Check up to 30 non-empty lines

    for line in lines:
        if not line.strip():
            continue
        stripped = strip_log_prefix(line)
        if stripped != line:
            prefix_count += 1
        checked += 1
        if checked >= sample_size:
            break

    # Require at least 2 lines with prefixes and at least 30% of sampled lines
    return checked > 0 and prefix_count >= 2 and (prefix_count / checked) >= 0.3


def strip_log_prefixes_from_content(content: str) -> str:
    """Strip log prefixes from all lines in file content.

    Returns the content with log prefixes removed from each line.
    """
    lines = content.split('\n')
    stripped_lines = [strip_log_prefix(line) for line in lines]
    return '\n'.join(stripped_lines)


def create_stripped_content(file_path: str) -> Optional[str]:
    """Read a file and return its content with log prefixes stripped.

    Returns a string of the stripped content, or None if the file doesn't appear to have log prefixes.
    """
    try:
        # To avoid reading large files entirely into memory just for a check,
        # we first read a sample of the file to check for log prefixes.
        with open(file_path, 'r') as f:
            sample = f.read(8000)  # Read first 8KB, should be enough for several lines
    except (OSError, UnicodeDecodeError):
        return None

    if not has_log_prefixes(sample):
        return None

    # Prefixes were found in the sample, so now we process the whole file.
    # The runner that calls this already limits the file size, so we don't
    # expect to be reading huge files here.
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return strip_log_prefixes_from_content(content)
    except (OSError, UnicodeDecodeError):
        return None
