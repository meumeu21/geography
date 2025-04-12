from django.shortcuts import render, redirect
from django.core.cache import cache
from datetime import datetime
import random
from . import geography_utils

def index(request):
    return render(request, "index.html")

def stats(request):
    db_countries, user_countries, total_countries = geography_utils.get_countries_stats()
    return render(request, "stats.html", {"db_countries": db_countries, 
                                          "user_countries": user_countries,
                                          "total_countries": total_countries})

def countries_table(request):
    countries = geography_utils.get_countries_for_table()
    return render(request, "countries_table.html", {"countries": countries})

def add_country(request):
    return render(request, "add_country.html")

def send_country(request):
    if request.method == "POST":
        cache.clear() 
        country = request.POST.get("country", "").strip()
        capital = request.POST.get("capital", "").strip()
        user = request.POST.get("added_by", "").strip() or "-"
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M")

        context = {}
        if not country:
            context["success"] = False
            context["comment"] = "Название страны не может быть пустым"
        elif not capital:
            context["success"] = False
            context["comment"] = "Название столицы не может быть пустым"
        else:
            try:
                geography_utils.add_country(country, capital, user, date_added)
                context["success"] = True
                context["comment"] = f"Пара '{country} — {capital}' успешно добавлена!"
            except Exception as e:
                context["success"] = False
                context["comment"] = f"Ошибка при сохранении: {e}"
        return render(request, "add_country_request.html", context)
    return redirect("add_country")



# Викторина
def quiz_settings(request):
    max_questions = geography_utils.get_countries_count()
    if request.method == 'POST':
        if max_questions == 0:
            return render(request, 'quiz_settings.html', {
                'error': 'Нет данных для викторины. Сначала добавьте страны.',
                'max_questions': max_questions
            })
        question_count = min(int(request.POST.get('question_count', 1)), max_questions)
        request.session['quiz_started'] = True
        request.session['total_questions'] = question_count
        request.session['time_per_question'] = int(request.POST.get('time_limit', 30))
        request.session['current_question'] = 1
        request.session['correct_answers'] = 0
        request.session['used_countries'] = []
        return redirect('quiz_question')
    
    return render(request, 'quiz_settings.html', {
        'max_questions': max_questions
    })

def quiz_question(request):
    if not request.session.get('quiz_started'):
        return redirect('quiz_settings')
    countries = geography_utils.get_countries_for_table()
    unused_countries = [c for c in countries if c['country'] not in request.session['used_countries']]
    if not unused_countries or request.session['current_question'] > request.session['total_questions']:
        return redirect('quiz_results')
    current_country = random.choice(unused_countries)
    request.session['current_country'] = current_country
    request.session['question_start_time'] = datetime.now().timestamp()
    ask_country = random.choice([True, False])
    request.session['ask_country'] = ask_country
    context = {
        'ask_country': ask_country,
        'country': current_country['country'] if not ask_country else None,
        'capital': current_country['capital'] if ask_country else None,
        'current_question': request.session['current_question'],
        'total_questions': request.session['total_questions'],
        'time_limit': request.session['time_per_question']
    }
    return render(request, 'quiz_question.html', context)

def check_answer(request):
    if request.method == 'POST':
        current_country = request.session.get('current_country')
        if not current_country:
            return redirect('quiz_settings')
        
        user_answer = request.POST.get('answer', '').strip().lower()
        is_correct = False
        correct_answer = ''
        
        if request.session['ask_country']:
            correct_answer = current_country['country'].lower()
            is_correct = user_answer == correct_answer
        else:
            correct_answer = current_country['capital'].lower()
            is_correct = user_answer == correct_answer
        
        request.session['used_countries'].append(current_country['country'])
        request.session['current_question'] += 1
        if is_correct:
            request.session['correct_answers'] += 1
        
        time_spent = datetime.now().timestamp() - request.session['question_start_time']
        time_ok = time_spent <= request.session['time_per_question']
        
        context = {
            'is_correct': is_correct and time_ok,
            'correct_answer': current_country['country'] if request.session['ask_country'] else current_country['capital'],
            'user_answer': user_answer,
            'time_ok': time_ok,
            'time_spent': round(time_spent, 1),
            'current_question': request.session['current_question'],
            'total_questions': request.session['total_questions']
        }
        return render(request, 'quiz_feedback.html', context)
    
    return redirect('quiz_question')

def skip_question(request):
    current_country = request.session.get('current_country')
    if current_country:
        request.session['used_countries'].append(current_country['country'])
        request.session['current_question'] += 1
        
        context = {
            'skipped': True,
            'correct_answer': current_country['country'] if request.session['ask_country'] else current_country['capital'],
            'current_question': request.session['current_question'],
            'total_questions': request.session['total_questions']
        }
        return render(request, 'quiz_feedback.html', context)
    return redirect('quiz_question')

def quiz_results(request):
    if not request.session.get('quiz_started'):
        return redirect('quiz_settings')
    
    total = request.session['total_questions']
    correct = request.session['correct_answers']
    request.session['quiz_started'] = False
    
    context = {
        'total_questions': total,
        'correct_answers': correct,
        'percentage': round((correct / total) * 100) if total > 0 else 0
    }
    return render(request, 'quiz_results.html', context)