from google import genai
from django.conf import settings
from .models import ProgramOutcome, Student, LoToPoMapping, AssessmentToLoMapping, Grade, Course, Assessment, LearningOutcome, Enrollment

def get_all_students_info():
    """
    Get all students with their grades and performance data.
    """
    try:
        students = Student.objects.all().select_related('user')
        students_data = []
        
        for student in students:
            # Get enrollments
            enrollments = Enrollment.objects.filter(student=student).select_related('course')
            enrolled_courses = [e.course.code for e in enrollments]
            
            # Get grades
            grades = Grade.objects.filter(student=student).select_related('assessment', 'assessment__course')
            grade_data = []
            total_percentage = 0
            grade_count = 0
            
            for grade in grades:
                grade_data.append({
                    'assessment': grade.assessment.name,
                    'course': grade.assessment.course.code,
                    'points': grade.points,
                    'max_points': grade.assessment.total_points,
                    'percentage': round(grade.percentage, 1)
                })
                total_percentage += grade.percentage
                grade_count += 1
            
            avg_grade = round(total_percentage / grade_count, 1) if grade_count > 0 else 0
            
            students_data.append({
                'student_no': student.student_no,
                'name': f"{student.user.first_name} {student.user.last_name}".strip(),
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'enrolled_courses': enrolled_courses,
                'total_grades': grade_count,
                'average_grade': avg_grade,
                'grades': grade_data[:10]  # Limit to 10 most recent
            })
        
        return students_data
    except Exception as e:
        print(f"Error in get_all_students_info: {e}")
        return []

def get_courses_info():
    """
    Get all courses with their statistics.
    """
    try:
        courses = Course.objects.all()
        courses_data = []
        
        for course in courses:
            los = LearningOutcome.objects.filter(course=course)
            assessments = Assessment.objects.filter(course=course)
            enrollments = Enrollment.objects.filter(course=course)
            
            courses_data.append({
                'code': course.code,
                'name': course.name,
                'semester': course.semester,
                'learning_outcomes_count': los.count(),
                'assessments_count': assessments.count(),
                'students_count': enrollments.count(),
                'assessments': [{'name': a.name, 'type': a.assessment_type, 'max_points': a.total_points} for a in assessments]
            })
        
        return courses_data
    except Exception as e:
        print(f"Error in get_courses_info: {e}")
        return []

def get_all_po_stats():
    """
    Calculates average PO scores across all students.
    Returns a dictionary with PO codes and their average scores.
    """
    try:
        students = Student.objects.all()
        pos = ProgramOutcome.objects.all()
        
        if not students.exists() or not pos.exists():
            return []
        
        po_totals = {po.code: {'total_score': 0, 'count': 0, 'description': po.description} for po in pos}
        
        for student in students:
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
    except Exception as e:
        print(f"Error in get_all_po_stats: {e}")
        return []

def chat_with_gemini(user_message, api_key):
    """
    Sends the user message and context to Gemini using new google-genai package.
    """
    try:
        # Initialize the client with API key
        client = genai.Client(api_key=api_key)
        
        # Gather comprehensive context
        po_stats = get_all_po_stats()
        students_info = get_all_students_info()
        courses_info = get_courses_info()
        
        context_prompt = f"""
        You are an AI assistant for an Outcome Based Education (OBS) system called "PO Manager".
        You have access to the following data:
        
        === STUDENTS DATA ===
        Total Students: {len(students_info)}
        Students List (with grades and performance):
        {students_info}
        
        === COURSES DATA ===
        Total Courses: {len(courses_info)}
        Courses:
        {courses_info}
        
        === PROGRAM OUTCOMES (PO) STATISTICS ===
        {po_stats}
        
        === USER QUESTION ===
        "{user_message}"
        
        === INSTRUCTIONS ===
        - Answer the user's question based on the data provided above.
        - If asked about a specific student, search by name (first name, last name) or student number.
        - Names may be in Turkish, handle case-insensitive matching.
        - Provide detailed statistics when asked about performance.
        - If data is not available, say so clearly.
        - Answer in the SAME LANGUAGE as the user's question (Turkish or English).
        - Be concise but informative.
        - Use bullet points and formatting for clarity.
        """
        
        # Generate content using the new API - try gemini-2.5-flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=context_prompt
        )
        
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise Exception(f"AI yanıt veremedi: {str(e)}")
