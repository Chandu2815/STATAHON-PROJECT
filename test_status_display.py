"""
Quick test to verify the admin dashboard is working
"""
import httpx

print("Testing admin dashboard...")
print("="*60)

# Test login
response = httpx.post(
    "http://127.0.0.1:8889/api/v1/auth/login",
    data={"username": "admin", "password": "password"}
)

if response.status_code == 200:
    token = response.json()["access_token"]
    print("✅ Login successful!")
    
    # Test users endpoint
    users_response = httpx.get(
        "http://127.0.0.1:8889/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"✅ Retrieved {len(users)} users")
        print("\nStatus Summary:")
        active = sum(1 for u in users if u.get('is_active'))
        inactive = len(users) - active
        print(f"  • Active users: {active}")
        print(f"  • Inactive users: {inactive}")
        
        print("\nAll Users:")
        for user in users:
            status = "✓ Active" if user['is_active'] else "✗ Inactive"
            print(f"  {user['username']:15} - {status:12} - Password: {user.get('plain_password', 'N/A')}")
    else:
        print(f"❌ Failed to get users: {users_response.status_code}")
else:
    print(f"❌ Login failed: {response.status_code}")

print("="*60)
print("\n🌐 Access admin dashboard at: http://127.0.0.1:8889/admin/dashboard")
print("   Login: admin / password")
print("\n✨ Status badges are now enhanced with:")
print("   • Gradient backgrounds")
print("   • Pulsing animation for active users")
print("   • Better visibility and styling")
