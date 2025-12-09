#!/usr/bin/env python
"""
Öğrenci ve not verileri oluşturur
"""

import os
import django
import random
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'po_manager.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Course, Student, Assessment, Grade

def create_student_data():
    print("🌱 Öğrenci ve not verileri oluşturuluyor...")
    
    # 1. Öğrencileri oluştur
    student_names = [
        ('Ali', 'Yılmaz'), ('Ayşe', 'Demir'), ('Mehmet', 'Kaya'), ('Zeynep', 'Çelik'),
        ('Can', 'Öztürk'), ('Elif', 'Arslan'), ('Burak', 'Doğan'), ('Selin', 'Koç'),
        ('Emre', 'Yıldız'), ('Gamze', 'Şahin'), ('Mert', 'Aydın'), ('Esra', 'Özkan'),
        ('Kerem', 'Tekin'), ('Buse', 'Yavuz'), ('Onur', 'Kurt'), ('Derya', 'Eren'),
        ('Volkan', 'Aksoy'), ('Seda', 'Polat'), ('Tolga', 'Güler'), ('Gizem', 'Uçar')
    ]
    
    students = []
    for i, (first, last) in enumerate(student_names):
        username = f"{first.lower()}.{last.lower()}{i+1}"
        email = f"{username}@student.edu.tr"
        student_no = f"2024{str(i+1).zfill(4)}"
        
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={'first_name': first, 'last_name': last, 'email': email}
        )
        
        student, created = Student.objects.get_or_create(
            student_no=student_no,
            defaults={'user': user, 'department': 'CSE'}
        )
        students.append(student)
        if created:
            print(f"   ✓ Student created: {first} {last} ({student_no})")

    # 2. Dersleri ve Assessmentları al
    courses = Course.objects.all()
    
    if not courses.exists():
        print("   ! Hiç ders bulunamadı. Lütfen önce seed_cse311.py çalıştırın.")
        return

    # 3. Notları oluştur
    for course in courses:
        assessments = course.assessments.all()
        if not assessments.exists():
            print(f"   ! {course.code} için assessment bulunamadı.")
            continue
            
        print(f"   📝 {course.code} için notlar giriliyor...")
        
        for student in students:
            # Öğrenci profili belirle (Başarılı, Orta, Zayıf)
            profile = random.choice(['high', 'mid', 'low'])
            
            for assessment in assessments:
                # Profile göre not aralığı belirle
                if profile == 'high':
                    base_score = random.uniform(0.80, 1.00)
                elif profile == 'mid':
                    base_score = random.uniform(0.50, 0.85)
                else:
                    base_score = random.uniform(0.20, 0.60)
                
                # Puanı hesapla (Total points üzerinden)
                points = round(assessment.total_points * base_score, 1)
                
                # Notu kaydet
                Grade.objects.update_or_create(
                    assessment=assessment,
                    student=student,
                    defaults={'points': points}
                )
                
    print("✅ Tüm veriler başarıyla oluşturuldu!")

if __name__ == '__main__':
    create_student_data()
