from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .models import Student, BehaviorHistory
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from django.utils import timezone
import traceback
import json


@ensure_csrf_cookie
def home(request):
    query = request.GET.get('search', '')
    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) | Q(student_id__icontains=query)
        )
    else:
        students = Student.objects.all()
    
    context = {
        'students': students,
        'search_query': query
    }
    return render(request, 'home.html', context)


@csrf_exempt
def update_behavior(request, student_id):
    if request.method == 'POST':
        try:
            student = get_object_or_404(Student, id=student_id)
            
            
            try:
                data = json.loads(request.body)
                merits = data.get('merits')
                behavior_points = data.get('behavior_points')
            except json.JSONDecodeError:
                merits = request.POST.get('merits')
                behavior_points = request.POST.get('behavior_points')
            
            if merits is not None:
                student.merits = int(merits)
            if behavior_points is not None:
                student.behaviour_points = int(behavior_points)
            
            student.save()
            
            
            BehaviorHistory.objects.create(
                student=student,
                behavior_score=student.behavior_score
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_behavior_prediction(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        history = student.behavior_history.all().order_by('date')
        
        if history.count() < 2:
            return JsonResponse({
                'error': 'Not enough data for prediction. Please record at least 2 behavior points.'
            }, status=400)
        

        dates = [(h.date - history.first().date).days for h in history]
        scores = [h.behavior_score for h in history]
        
        
        X = np.array(dates).reshape(-1, 1)
        X_poly = np.column_stack([X, np.square(X)])  
        y = np.array(scores)
        
        
        model = LinearRegression()
        model.fit(X_poly, y)
        
        
        last_date = max(dates)
        future_days = list(range(last_date + 1, last_date + 31))
        future_X = np.array(future_days).reshape(-1, 1)
        future_X_poly = np.column_stack([future_X, np.square(future_X)])
        
        
        raw_predictions = model.predict(future_X_poly)
        
        
        if len(scores) >= 3: 
            recent_trend = (scores[-1] - scores[-3]) / 2  
            trend_factor = 0.7  
            adjusted_predictions = []
            
            for i, pred in enumerate(raw_predictions):
                days_from_last = i + 1
                trend_adjustment = recent_trend * days_from_last * trend_factor
                adjusted_pred = pred + trend_adjustment
                

                min_score = max(min(scores) - 5, 0)   
                max_score = max(scores) + 5  
                adjusted_predictions.append(max(min(adjusted_pred, max_score), min_score))
        else:
            adjusted_predictions = raw_predictions.tolist() 
        
        
        prediction_data = {
            'dates': [(history.first().date + timedelta(days=d)).strftime('%Y-%m-%d') for d in future_days],
            'predictions': adjusted_predictions,
            'historical_dates': [h.date.strftime('%Y-%m-%d') for h in history],
            'historical_scores': scores
        }
        
        return JsonResponse(prediction_data)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=400)
