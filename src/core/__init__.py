"""
AIQSO SEO Service - Core Module

This module contains the shared SEO engine used by all tiers:
- Internal (unlimited access for AIQSO team)
- Demo (limited public access)
- Paid (customer tiers: Starter, Pro, Enterprise, Agency)
"""

from .tiers import TierManager, Tier
from .auditor import SEOAuditor

__all__ = ["TierManager", "Tier", "SEOAuditor"]
