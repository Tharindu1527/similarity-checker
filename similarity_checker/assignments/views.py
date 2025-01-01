from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Assignment
from .utils import calculate_similarity, extract_text_from_file
import json
import os

@csrf_exempt
def upload_assignment(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            file = request.FILES.get('file')
            
            if not title or not file:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Both title and file are required'
                }, status=400)
            
            # Validate file extension
            allowed_extensions = ['txt', 'doc', 'docx', 'pdf']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
                }, status=400)
            
            # Validate file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                return JsonResponse({
                    'status': 'error',
                    'message': 'File size should not exceed 10MB'
                }, status=400)
            
            assignment = Assignment.objects.create(title=title, file=file)
            
            return JsonResponse({
                'status': 'success',
                'assignment_id': assignment.id,
                'title': assignment.title,
                'file_url': assignment.file.url if assignment.file else None
            })
            
        except ValidationError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'An unexpected error occurred'
            }, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def compare_assignments(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            assignment_ids = data.get('assignment_ids', [])
            
            if len(assignment_ids) < 2:
                return JsonResponse({
                    'error': 'Please select at least 2 assignments'
                }, status=400)
            
            assignments = Assignment.objects.filter(id__in=assignment_ids)
            
            # Verify all assignments were found
            if len(assignments) != len(assignment_ids):
                return JsonResponse({
                    'status': 'error',
                    'message': 'One or more assignments not found'
                }, status=404)
            
            results = []
            
            # Compare each pair of assignments
            for i in range(len(assignments)):
                for j in range(i + 1, len(assignments)):
                    try:
                        similarity = calculate_similarity(
                            assignments[i].file.path,
                            assignments[j].file.path
                        )
                        
                        results.append({
                            'assignment1_id': assignments[i].id,
                            'assignment1_title': assignments[i].title,
                            'assignment2_id': assignments[j].id,
                            'assignment2_title': assignments[j].title,
                            'similarity_score': similarity
                        })
                    except Exception as e:
                        results.append({
                            'assignment1_id': assignments[i].id,
                            'assignment1_title': assignments[i].title,
                            'assignment2_id': assignments[j].id,
                            'assignment2_title': assignments[j].title,
                            'error': f'Failed to compare: {str(e)}',
                            'similarity_score': None
                        })
            
            return JsonResponse({
                'status': 'success',
                'results': results
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def get_assignments(request):
    if request.method == 'GET':
        try:
            assignments = Assignment.objects.all().order_by('-uploaded_at')
            return JsonResponse({
                'status': 'success',
                'assignments': [{
                    'id': assignment.id,
                    'title': assignment.title,
                    'file_url': assignment.file.url if assignment.file else None,
                    'uploaded_at': assignment.uploaded_at.isoformat()
                } for assignment in assignments]
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)