"""
Alumni Donation & Engagement Prediction System
Production-Ready ML Pipeline with full CPPE Support
Version 3.0.0: Cloud + Data + GenAI + Security Integration
"""

__version__ = "3.0.0"
__author__ = "Senior ML Engineer"

# Core ML Pipeline Modules
from . import config
from . import data_loader
from . import eda
from . import features
from . import models
from . import ensemble
from . import evaluation
from . import audit
from . import genai

# AWS Cloud Integration Modules (NEW)
from . import aws_config
from . import s3_storage
from . import lambda_handlers
from . import glue_etl
from . import api_gateway

# Security & Compliance Modules (NEW)
from . import security
from . import rbac
from . import enhanced_audit

__all__ = [
    # Core
    "config", "data_loader", "eda", "features",
    "models", "ensemble", "evaluation", "audit", "genai",
    # AWS
    "aws_config", "s3_storage", "lambda_handlers", "glue_etl", "api_gateway",
    # Security
    "security", "rbac", "enhanced_audit",
]
