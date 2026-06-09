"""
Admin permission checks and utilities
"""
from functools import wraps
from fastapi import HTTPException, status
from app.models.user import User, UserRole


class AdminPermissions:
    """Admin permission levels and checks"""
    
    # Permission matrix
    PERMISSIONS = {
        UserRole.SUPER_ADMIN: {
            'manage_users': True,
            'manage_admins': True,
            'manage_datasets': True,
            'view_audit_logs': True,
            'system_config': True,
            'view_all_data': True,
            'delete_users': True,
            'upload_datasets': True,
        },
        UserRole.ADMIN: {  # Legacy admin role
            'manage_users': True,
            'manage_admins': True,
            'manage_datasets': True,
            'view_audit_logs': True,
            'system_config': True,
            'view_all_data': True,
            'delete_users': True,
            'upload_datasets': True,
        },
        UserRole.DATA_ADMIN: {
            'manage_users': False,
            'manage_admins': False,
            'manage_datasets': True,
            'view_audit_logs': False,
            'system_config': False,
            'view_all_data': True,
            'delete_users': False,
            'upload_datasets': True,
        },
        UserRole.USER_ADMIN: {
            'manage_users': True,
            'manage_admins': False,
            'manage_datasets': False,
            'view_audit_logs': True,
            'system_config': False,
            'view_all_data': False,
            'delete_users': True,
            'upload_datasets': False,
        },
        UserRole.SUPPORT_ADMIN: {
            'manage_users': False,
            'manage_admins': False,
            'manage_datasets': False,
            'view_audit_logs': False,
            'system_config': False,
            'view_all_data': True,
            'delete_users': False,
            'upload_datasets': False,
        },
    }
    
    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        if user.role not in AdminPermissions.PERMISSIONS:
            return False
        return AdminPermissions.PERMISSIONS[user.role].get(permission, False)
    
    @staticmethod
    def require_permission(permission: str):
        """Decorator to require specific permission"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get current_user from kwargs
                current_user = kwargs.get('current_user')
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                if not AdminPermissions.has_permission(current_user, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required: {permission}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def get_role_display(role: UserRole) -> dict:
        """Get human-readable role information"""
        role_info = {
            UserRole.SUPER_ADMIN: {
                'name': 'Super Administrator',
                'icon': '👑',
                'color': '#e94560',
                'description': 'Full system access and control'
            },
            UserRole.ADMIN: {
                'name': 'Administrator',
                'icon': '⚙️',
                'color': '#e94560',
                'description': 'Full system access (legacy)'
            },
            UserRole.DATA_ADMIN: {
                'name': 'Data Manager',
                'icon': '📊',
                'color': '#3498db',
                'description': 'Manage datasets and uploads'
            },
            UserRole.USER_ADMIN: {
                'name': 'User Manager',
                'icon': '👥',
                'color': '#9b59b6',
                'description': 'Manage user accounts'
            },
            UserRole.SUPPORT_ADMIN: {
                'name': 'Support Staff',
                'icon': '🎧',
                'color': '#95a5a6',
                'description': 'View-only access for support'
            },
        }
        return role_info.get(role, {
            'name': role.value,
            'icon': '👤',
            'color': '#95a5a6',
            'description': 'Standard user'
        })
