from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .users_db import insert_user, authenticate_user, remove_user
from .models import AppUser
from .dbComplaints import insert_complaint, list_complaints
from .models import Complaint
from django.conf import settings
from django.core.files.storage import default_storage

def render_index(request):
    return render(request, "accounts/index.html")

def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        
        result = authenticate_user(user_id, password)
        
        if result['authenticated'] and result['user']['role'] in ["moderator", "user"]:
            # Store user in session (optional)
            request.session['user_id'] = user_id
            request.session['role'] = result['user']['role']
            return redirect('user_page')  
        elif result['authenticated'] and result['user']['role'] in ["admin"]:
            request.session['user_id'] = user_id
            request.session['role'] = result['user']['role']
            return redirect('admin_page')  # Redirect to admin page
        else:
            return render(request, 'accounts/login.html', {'error': result['message']})
    
    return render(request, "accounts/login.html")

def register_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'user')
        
        # Check if passwords match
        if password != confirm_password:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})
        
        # Call insert_user
        result = insert_user(user_id, password, role)
        
        if result['success']:
            return redirect('login')  # Redirect to login after success
        else:
            return render(request, 'accounts/register.html', {'error': result['message']})
    
    return render(request, "accounts/register.html")

def user_page_view(request):
    """Display the user's personal page"""
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    
    if not user_id:
        return redirect('login')  # Redirect to login if not authenticated
    
    context = {
        'user_id': user_id,
        'role': role
    }
    return render(request, 'accounts/user_page.html', context)

def admin_page_view(request):
    """Admin dashboard - only accessible to admins"""
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    
    if not user_id or role != 'admin':
        return redirect('login')  # Redirect if not admin
    
    context = {
        'user_id': user_id,
        'role': role
    }
    return render(request, 'accounts/admin.html', context)

@require_http_methods(["GET"])
def api_list_users(request):
    """API: Get all users (JSON) - Admin only"""
    role = request.session.get('role')
    
    if role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    users = AppUser.objects.all().values('user_id', 'role')
    return JsonResponse(list(users), safe=False)

@require_http_methods(["POST"])
def api_delete_user(request):
    """API: Delete a user - Admin only"""
    role = request.session.get('role')
    
    if role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    user_id = request.POST.get('user_id')
    result = remove_user(user_id)
    
    if result['success']:
        return JsonResponse({'success': True, 'message': result['message']})
    else:
        return JsonResponse({'success': False, 'error': result['message']})

@require_http_methods(["POST"])
def api_add_user(request):
    """API: Add a new user - Admin only"""
    role = request.session.get('role')
    
    if role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    user_id = request.POST.get('user_id')
    password = request.POST.get('password')
    user_role = request.POST.get('role', 'user')
    
    result = insert_user(user_id, password, user_role)
    
    if result['success']:
        return JsonResponse({'success': True, 'message': result['message']})
    else:
        return JsonResponse({'success': False, 'error': result['message']})

def adduser_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        role = request.POST.get('role')
        result = insert_user(user_id, password, role)
        return HttpResponse(result['message'])
    return HttpResponse("Only POST allowed")


@require_http_methods(["GET"])
def api_list_complaints(request):
    """Return recent complaints as JSON."""
    # pagination params optional
    try:
        limit = int(request.GET.get('limit', 50))
    except ValueError:
        limit = 50
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0

    data = list_complaints(limit=limit, offset=offset)
    return JsonResponse(data, safe=False)


@require_http_methods(["POST"])
def api_add_complaint(request):
    """Accept multipart form data and create a Complaint record."""
    user_id = request.session.get('user_id')
    # allow anonymous reports if you prefer; here we accept empty user
    image = request.FILES.get('image')
    location = request.POST.get('location', '')
    description = request.POST.get('description', '')
    severity = request.POST.get('severity', 'low')

    result = insert_complaint(user_id, image, location, description, severity)
    if result.get('success'):
        return JsonResponse({'success': True, 'id': result.get('id')})
    else:
        return JsonResponse({'success': False, 'error': result.get('error')}, status=400)

