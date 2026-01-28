# API Reference

## Overview

This section documents the main modules and classes in aiqso-seo-service.

## `main`

**Source:** `src/cli/main.py`

### Functions

- `format_score()`
- `format_check_result()`
- `print_audit_result()`
- `cli()`
- `audit()`
- `compare()`
- `site()`
- `tiers()`
- `main()`

## `auditor`

**Source:** `src/core/auditor.py`

### Classes

#### `CheckResult`

```python
from src.auditor import CheckResult

# Usage
instance = CheckResult()
```

#### `AuditResult`

```python
from src.auditor import AuditResult

# Usage
instance = AuditResult()
```

#### `SEOAuditor`

```python
from src.auditor import SEOAuditor

# Usage
instance = SEOAuditor()
```

## `tiers`

**Source:** `src/core/tiers.py`

### Classes

#### `RateLimits`

```python
from src.tiers import RateLimits

# Usage
instance = RateLimits()
```

#### `Features`

```python
from src.tiers import Features

# Usage
instance = Features()
```

#### `AuditSettings`

```python
from src.tiers import AuditSettings

# Usage
instance = AuditSettings()
```

#### `Tier`

```python
from src.tiers import Tier

# Usage
instance = Tier()
```

#### `TierManager`

```python
from src.tiers import TierManager

# Usage
instance = TierManager()
```

### Functions

- `get_tier_manager()`

