# Branch Pattern Configuration

## Overview

The branch protection pattern is configurable and can be updated to match different naming conventions.

## Current Configuration

The branch pattern is currently set to `safe` by default, meaning any branch containing "safe" in its name will be automatically protected.

## How to Update the Pattern

### Method 1: Environment Variable (Recommended)

1. Open your `.env` file
2. Add or update the `SAFE_BRANCH_PATTERN` variable:
   ```bash
   SAFE_BRANCH_PATTERN=your_pattern_here
   ```
3. Save the file

### Method 2: Direct Code Change

1. Open `config.py`
2. Update the default value in line 20:
   ```python
   SAFE_BRANCH_PATTERN = os.getenv('SAFE_BRANCH_PATTERN', 'your_pattern_here').lower()
   ```

## Examples

- `SAFE_BRANCH_PATTERN=safe` - Matches branches like `safe-feature`, `hotfix-safe`, `safe`
- `SAFE_BRANCH_PATTERN=protected` - Matches branches like `protected-feature`, `hotfix-protected`
- `SAFE_BRANCH_PATTERN=prod` - Matches branches like `prod-feature`, `hotfix-prod`

## How It Works

- The pattern matching is case-insensitive
- Any branch containing the pattern anywhere in its name will be protected
- The pattern is checked during:
  - Repository creation (for future branches)
  - Branch creation via `create-branch` command
  - Manual protection via `protect-safe-branches` command

## Testing

After updating the pattern, test it by:

1. Creating a new branch with the pattern in its name
2. Running `python3 main.py protect-safe-branches <repo_name>` to see which branches match
3. Checking the protection status in GitHub
