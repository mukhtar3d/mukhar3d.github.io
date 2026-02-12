from .models import AppUser
from django.db import IntegrityError

def insert_user(user_id, raw_password, role):
    if not (isinstance(user_id, str) and user_id.isdigit() and len(user_id) == 12):
        return {'success': False, 'message': 'User ID must be 12 digits'}
    
    valid_roles = ['admin', 'moderator', 'user']
    if role not in valid_roles:
        return {'success': False, 'message': f'Role must be one of: {", ".join(valid_roles)}'}
    
    if not raw_password or len(raw_password) < 4:
        return {'success': False, 'message': 'Password must be at least 4 characters'}
    
    try:
        u = AppUser(user_id=user_id, role=role)
        u.set_password(raw_password)
        u.save()
        return {'success': True, 'message': f'User {user_id} inserted successfully'}
    except IntegrityError:
        return {'success': False, 'message': 'User ID already exists'}


def authenticate_user(user_id, raw_password):
    try:
        u = AppUser.objects.get(pk=user_id)
    except AppUser.DoesNotExist:
        return {'authenticated': False, 'message': 'User ID not found', 'user': None}
    
    ok = u.check_password(raw_password)
    if ok:
        return {
            'authenticated': True,
            'message': 'Authentication successful',
            'user': {'id': u.user_id, 'role': u.role}
        }
    else:
        return {'authenticated': False, 'message': 'Invalid password', 'user': None}


def remove_user(user_id):
    deleted, _ = AppUser.objects.filter(pk=user_id).delete()
    if deleted:
        return {'success': True, 'message': f'User {user_id} removed successfully'}
    else:
        return {'success': False, 'message': f'User {user_id} not found'}
