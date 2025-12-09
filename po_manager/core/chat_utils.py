import google.generativeai as genai
from django.conf import settings
from .models import ProgramOutcome, Student, LoToPoMapping, AssessmentToLoMapping, Grade

def get_all_po_stats():
    """
    Calculates average PO scores across all students.
    Returns a dictionary with PO codes and their average scores.
    """
    students = Student.objects.all()
    pos = ProgramOutcome.objects.all()
    
    po_totals = {po.code: {'total_score': 0, 'count': 0, 'description': po.description} for po in pos}
    
    for student in students:
        # Calculate PO scores for this student (reusing logic from views.py)
        # Ideally this logic should be centralized, but for now I'll duplicate/adapt it for batch processing
        
        for po in pos:
            lo_mappings = LoToPoMapping.objects.filter(program_outcome=po)
            
            total_weighted_score = 0
            total_weight_sum = 0
            
            for lo_map in lo_mappings:
                lo = lo_map.learning_outcome
                lo_po_weight = lo_map.contribution_weight
                
                assess_mappings = AssessmentToLoMapping.objects.filter(learning_outcome=lo)
                
                for assess_map in assess_mappings:
                    assessment = assess_map.assessment
                    assess_lo_weight = assess_map.contribution_weight
                    
                    try:
                        grade = Grade.objects.get(assessment=assessment, student=student)
                        score = grade.percentage
                        
                        contribution = score * assess_lo_weight * lo_po_weight
                        weight_factor = assess_lo_weight * lo_po_weight
                        
                        total_weighted_score += contribution
                        total_weight_sum += weight_factor
                        
                    except Grade.DoesNotExist:
                        continue
            
            if total_weight_sum > 0:
                normalized_score = total_weighted_score / total_weight_sum
                po_totals[po.code]['total_score'] += float(normalized_score)
                po_totals[po.code]['count'] += 1
    
    # Calculate averages
    po_stats = []
    for code, data in po_totals.items():
        avg = data['total_score'] / data['count'] if data['count'] > 0 else 0
        po_stats.append({
            'code': code,
            'description': data['description'],
            'average_score': round(avg, 2),
            'student_count': data['count']
        })
        
    return po_stats

def chat_with_gemini(user_message, api_key):
    """
    Sends the user message and context to Gemini.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Gather context
    po_stats = get_all_po_stats()
    
    context_prompt = f"""
    You are an AI assistant for an Outcome Based Education (OBS) system.
    Here is the current data for Program Outcomes (PO) based on student performance:
    
    {po_stats}
    
    The user asks: "{user_message}"
    
    Please analyze the data and answer the user's question. 
    If they ask about low averages, identify the POs with the lowest scores.
    If they ask for a summary, provide a brief overview.
    Keep your answer concise and helpful.
    """
    
    response = model.generate_content(context_prompt)
    return response.text
