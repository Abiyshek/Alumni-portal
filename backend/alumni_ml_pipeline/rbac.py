"""
Role-Based Access Control (RBAC) Module
Manages user roles and permissions for the alumni platform.
"""

import logging
import json
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

log = logging.getLogger("alumni_pipeline")


class Role(Enum):
    """User roles in the alumni system."""
    ADMIN = "admin"                          # Full access
    ALUMNI_OFFICER = "alumni_officer"        # View and manage alumni data
    DATA_ANALYST = "data_analyst"            # View reports and scores
    FINANCE = "finance"                      # View donation data
    EXECUTIVE = "executive"                  # View high-level reports
    VIEWER = "viewer"                        # Read-only access
    SYSTEM = "system"                        # Lambda/automation


class Permission(Enum):
    """Permissions in the alumni system."""
    # Data operations
    VIEW_ALUMNI_DATA = "view:alumni_data"
    EDIT_ALUMNI_DATA = "edit:alumni_data"
    DELETE_ALUMNI_DATA = "delete:alumni_data"
    
    # Donation data
    VIEW_DONATIONS = "view:donations"
    EDIT_DONATIONS = "edit:donations"
    EXPORT_DONATIONS = "export:donations"
    
    # Engagement data
    VIEW_ENGAGEMENT = "view:engagement"
    VIEW_SCORES = "view:scores"
    
    # Reports
    VIEW_REPORTS = "view:reports"
    GENERATE_REPORTS = "generate:reports"
    EXPORT_REPORTS = "export:reports"
    
    # Admin functions
    MANAGE_USERS = "admin:users"
    MANAGE_ROLES = "admin:roles"
    VIEW_AUDIT_LOGS = "admin:audit_logs"
    MANAGE_SYSTEM = "admin:system"


# Role to Permission mappings
ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],  # All permissions
    
    Role.ALUMNI_OFFICER: [
        Permission.VIEW_ALUMNI_DATA,
        Permission.EDIT_ALUMNI_DATA,
        Permission.VIEW_ENGAGEMENT,
        Permission.VIEW_DONATIONS,
        Permission.VIEW_SCORES,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
    ],
    
    Role.DATA_ANALYST: [
        Permission.VIEW_ALUMNI_DATA,
        Permission.VIEW_ENGAGEMENT,
        Permission.VIEW_SCORES,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.EXPORT_REPORTS,
    ],
    
    Role.FINANCE: [
        Permission.VIEW_DONATIONS,
        Permission.EXPORT_DONATIONS,
        Permission.VIEW_REPORTS,
    ],
    
    Role.EXECUTIVE: [
        Permission.VIEW_REPORTS,
        Permission.VIEW_SCORES,
    ],
    
    Role.VIEWER: [
        Permission.VIEW_ALUMNI_DATA,
        Permission.VIEW_REPORTS,
    ],
    
    Role.SYSTEM: [
        Permission.VIEW_ALUMNI_DATA,
        Permission.EDIT_ALUMNI_DATA,
        Permission.VIEW_DONATIONS,
        Permission.VIEW_ENGAGEMENT,
        Permission.VIEW_SCORES,
    ],
}


class User:
    """Represents an authenticated user."""

    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        roles: List[Role],
        department: Optional[str] = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.roles = roles
        self.department = department
        self.created_at = datetime.now().isoformat()
        self.last_login = None

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        for role in self.roles:
            if permission in ROLE_PERMISSIONS.get(role, []):
                return True
        return False

    def has_role(self, role: Role) -> bool:
        """Check if user has a specific role."""
        return role in self.roles

    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "roles": [r.value for r in self.roles],
            "department": self.department,
            "created_at": self.created_at,
            "last_login": self.last_login,
        }


class RBACManager:
    """Manages RBAC operations."""

    def __init__(self):
        self.users: Dict[str, User] = {}
        log.info("✓ RBAC Manager initialized")

    def create_user(
        self,
        user_id: str,
        username: str,
        email: str,
        roles: List[Role],
        department: Optional[str] = None
    ) -> User:
        """Create a new user."""
        user = User(user_id, username, email, roles, department)
        self.users[user_id] = user
        log.info(f"✓ User created: {username} with roles {[r.value for r in roles]}")
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    def update_user_roles(self, user_id: str, roles: List[Role]) -> bool:
        """Update user roles."""
        user = self.users.get(user_id)
        if user:
            user.roles = roles
            log.info(f"✓ User roles updated: {user.username}")
            return True
        return False

    def check_access(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission."""
        user = self.users.get(user_id)
        if not user:
            log.warning(f"User not found: {user_id}")
            return False
        
        has_access = user.has_permission(permission)
        action = "✓ ALLOWED" if has_access else "✗ DENIED"
        log.info(f"{action}: {user.username} → {permission.value}")
        return has_access

    def list_users(self, role: Optional[Role] = None) -> List[User]:
        """List users, optionally filtered by role."""
        users = list(self.users.values())
        if role:
            users = [u for u in users if role in u.roles]
        return users

    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user."""
        user = self.users.get(user_id)
        if not user:
            return []
        
        permissions = set()
        for role in user.roles:
            permissions.update(ROLE_PERMISSIONS.get(role, []))
        return list(permissions)


# ── Default RBAC Manager Instance ────────────────────────────────────────────
rbac_manager = RBACManager()

# ── Example: Create default users ────────────────────────────────────────────
def initialize_default_users():
    """Initialize default users for testing."""
    rbac_manager.create_user(
        "admin-001",
        "john_admin",
        "john@alumni.edu",
        [Role.ADMIN],
        "Administration"
    )
    
    rbac_manager.create_user(
        "officer-001",
        "sarah_officer",
        "sarah@alumni.edu",
        [Role.ALUMNI_OFFICER],
        "Alumni Relations"
    )
    
    rbac_manager.create_user(
        "analyst-001",
        "mike_analyst",
        "mike@alumni.edu",
        [Role.DATA_ANALYST],
        "Analytics"
    )
    
    rbac_manager.create_user(
        "finance-001",
        "jane_finance",
        "jane@alumni.edu",
        [Role.FINANCE],
        "Finance"
    )
    
    log.info("✓ Default users initialized")
