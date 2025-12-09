# Demo veri oluşturma scripti
# python manage.py shell < create_demo_data.py

from django.contrib.auth.models import User
from core.models import *

print("Demo veriler oluşturuluyor...")

# Program Outcomes oluştur
po_data = [
    ("PO1", "Matematik, fen bilimleri ve mühendislik alanlarında edinilen bilgileri uygulayabilme"),
    ("PO2", "Mühendislik problemlerini saptama, tanımlama, formüle etme ve çözme becerisi"),
    ("PO3", "Bir sistemi, sistem bileşenini veya süreci analiz ve tasarlama becerisi"),
    ("PO4", "Disiplinler arası takımlarda çalışabilme becerisi"),
    ("PO5", "Mühendislik problemlerini belirleme, formüle etme ve çözme becerisi"),
]

for code, desc in po_data:
    po, created = ProgramOutcome.objects.get_or_create(code=code, defaults={'description': desc})
    if created:
        print(f"✓ {code} oluşturuldu")

# Instructor user oluştur
instructor, created = User.objects.get_or_create(
    username='instructor1',
    defaults={
        'first_name': 'Ahmet',
        'last_name': 'Yılmaz',
        'email': 'ahmet@acibadem.edu.tr'
    }
)
if created:
    instructor.set_password('password123')
    instructor.save()
    print("✓ Instructor oluşturuldu")

# Course oluştur
course1, created = Course.objects.get_or_create(
    code='CSE311',
    defaults={
        'name': 'Algorithms',
        'semester': '2024-Fall',
        'department': 'CSE',
        'instructor': instructor
    }
)
if created:
    print(f"✓ {course1.code} dersi oluşturuldu")

course2, created = Course.objects.get_or_create(
    code='CSE321',
    defaults={
        'name': 'Database Systems',
        'semester': '2024-Fall',
        'department': 'CSE',
        'instructor': instructor
    }
)
if created:
    print(f"✓ {course2.code} dersi oluşturuldu")

# Learning Outcomes oluştur
lo1, created = LearningOutcome.objects.get_or_create(
    course=course1,
    code='LO1',
    defaults={
        'description': 'Algoritma karmaşıklığını analiz edebilme',
        'weight': 1.0
    }
)
if created:
    print(f"✓ {course1.code}-{lo1.code} oluşturuldu")

lo2, created = LearningOutcome.objects.get_or_create(
    course=course1,
    code='LO2',
    defaults={
        'description': 'Veri yapılarını kullanabilme',
        'weight': 1.0
    }
)
if created:
    print(f"✓ {course1.code}-{lo2.code} oluşturuldu")

lo3, created = LearningOutcome.objects.get_or_create(
    course=course2,
    code='LO1',
    defaults={
        'description': 'SQL sorguları yazabilme',
        'weight': 1.0
    }
)
if created:
    print(f"✓ {course2.code}-{lo3.code} oluşturuldu")

# LO to PO Mappings oluştur
mappings = [
    (lo1, ProgramOutcome.objects.get(code='PO1'), 3.0),
    (lo1, ProgramOutcome.objects.get(code='PO2'), 4.0),
    (lo2, ProgramOutcome.objects.get(code='PO1'), 4.0),
    (lo2, ProgramOutcome.objects.get(code='PO3'), 3.0),
    (lo3, ProgramOutcome.objects.get(code='PO1'), 3.0),
    (lo3, ProgramOutcome.objects.get(code='PO5'), 4.0),
]

for lo, po, weight in mappings:
    mapping, created = LoToPoMapping.objects.get_or_create(
        learning_outcome=lo,
        program_outcome=po,
        defaults={'contribution_weight': weight}
    )
    if created:
        print(f"✓ {lo.code} → {po.code} mapping oluşturuldu")

# Öğrenci oluştur
student_user, created = User.objects.get_or_create(
    username='student1',
    defaults={
        'first_name': 'Mehmet',
        'last_name': 'Demir',
        'email': 'mehmet@student.acibadem.edu.tr'
    }
)
if created:
    student_user.set_password('password123')
    student_user.save()

student, created = Student.objects.get_or_create(
    user=student_user,
    defaults={
        'student_no': '2020123456',
        'department': 'CSE'
    }
)
if created:
    print(f"✓ Öğrenci {student.student_no} oluşturuldu")

# Assessment oluştur
assessment1, created = Assessment.objects.get_or_create(
    course=course1,
    name='Midterm Exam',
    defaults={
        'assessment_type': 'midterm',
        'total_points': 100.0,
        'date': '2024-11-01'
    }
)
if created:
    assessment1.learning_outcomes.add(lo1, lo2)
    print(f"✓ {assessment1.name} oluşturuldu")

# Grade oluştur
grade, created = Grade.objects.get_or_create(
    assessment=assessment1,
    student=student,
    defaults={'points': 85.0}
)
if created:
    print(f"✓ Not kaydı oluşturuldu: {grade.points}/{assessment1.total_points}")

print("\n✅ Demo veriler başarıyla oluşturuldu!")
print("\nKullanıcılar:")
print(f"  Instructor: username='instructor1', password='password123'")
print(f"  Student: username='student1', password='password123'")
