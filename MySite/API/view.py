from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .users_db import insert_user, authenticate_user, remove_user
from .models import AppUser
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
        
        if password != confirm_password:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})

        result = insert_user(user_id, password, role)
        
        if result['success']:
            return redirect('login')
        else:
            return render(request, 'accounts/register.html', {'error': result['message']})
    
    return render(request, "accounts/register.html")

def user_page_view(request):
    """Display the user's personal page"""
    user_id = request.session.get('user_id', 'guest')
    role = request.session.get('role', 'user')
    
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
        return redirect('login')  
    
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
    """Return recent complaints as JSON (public endpoint)."""
    # pagination params optional
    try:
        limit = int(request.GET.get('limit', 50))
    except ValueError:
        limit = 50
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0

    complaints = Complaint.objects.all().order_by('-created_at')[offset:offset+limit]
    data = []
    for complaint in complaints:
        image_url = None
        if complaint.image_path:
            image_url = f'/media/{complaint.image_path}'
        data.append({
            'id': complaint.id,
            'user_id': complaint.user_id,
            'location': complaint.location,
            'description': complaint.description,
            'severity': complaint.severity,
            'status': complaint.status,
            'created_at': complaint.created_at.isoformat(),
            'image_path': complaint.image_path,
            'image_url': image_url
        })
    print(f"[DEBUG] api_list_complaints returning {len(data)} complaints")
    return JsonResponse(data, safe=False)


@require_http_methods(["POST"])
def api_add_complaint(request):
    """Accept multipart form data and create a Complaint record."""
    try:
        user_id = request.session.get('user_id')
        image = request.FILES.get('image')
        location = request.POST.get('location', '')
        description = request.POST.get('description', '')
        severity = request.POST.get('severity', 'low')

        # Save image if provided
        image_path = None
        if image:
            # Save the image to media folder
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_name = f'complaints/{timestamp}_{image.name}'
            # Use Django's file storage
            image_path = default_storage.save(image_name, image)

        # Create complaint using Django ORM
        complaint = Complaint.objects.create(
            user_id=user_id,
            image_path=image_path,
            location=location,
            description=description,
            severity=severity,
            status='pending'
        )
        return JsonResponse({'success': True, 'id': complaint.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

