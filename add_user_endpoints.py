"""
Add these endpoints to app/api/users.py at the end before the last line
"""

# Add to the end of app/api/users.py

@router.patch("/{user_id}")
def update_user(
    user_id: int,
    updates: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user details (Admin only)"""
    # Check if user is admin
    if not current_user.can_manage_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user to update
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update allowed fields
    if 'full_name' in updates:
        user.full_name = updates['full_name']
    if 'role' in updates:
        from app.models.user import UserRole
        try:
            user.role = UserRole(updates['role'])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {updates['role']}"
            )
    if 'is_active' in updates:
        user.is_active = updates['is_active']
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Admin {current_user.username} updated user {user_id}")
    return {"message": "User updated successfully", "user": user}


@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    password_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset user password (Admin only)"""
    # Check if user is admin
    if not current_user.can_manage_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get new password
    new_password = password_data.get('new_password')
    if not new_password or len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Update password
    from app.auth import get_password_hash
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    logger.info(f"Admin {current_user.username} reset password for user {user_id}")
    return {"message": "Password reset successfully"}
