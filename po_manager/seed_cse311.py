#!/usr/bin/env python
"""
CSE 311 Software Engineering dersi için örnek data oluşturur
Assessment → LO → PO mapping örneği
"""

import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'po_manager.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Course, LearningOutcome, Assessment, AssessmentToLoMapping, ProgramOutcome, LoToPoMapping

def create_cse311_sample_data():
    """CSE 311 Software Engineering dersi için örnek data"""
    
    print("🌱 CSE 311 Software Engineering örnek data oluşturuluyor...")
    
    # 1. Course oluştur veya al
    instructor, _ = User.objects.get_or_create(
        username='ahmet.bulut',
        defaults={
            'first_name': 'Ahmet',
            'last_name': 'Bulut',
            'email': 'ahmet.bulut@acibadem.edu.tr'
        }
    )
    
    course, created = Course.objects.get_or_create(
        code='CSE 311',
        defaults={
            'name': 'Software Engineering',
            'semester': 'Fall',
            'department': 'CSE',
            'instructor': instructor
        }
    )
    
    if created:
        print(f"   ✓ Course created: {course.code}")
    else:
        print(f"   ↻ Course exists: {course.code}")
    
    # 2. Learning Outcomes oluştur
    learning_outcomes_data = [
        {
            'code': 'LO1',
            'description': 'Learn design choices & philosophy behind widely popular SD practices.',
            'weight': 1.0
        },
        {
            'code': 'LO2',
            'description': 'Learn agile-SD methodology & best practices & the soft skill-set.',
            'weight': 1.0
        },
        {
            'code': 'LO3',
            'description': 'Apply the skill-set on a team project.',
            'weight': 1.2
        },
        {
            'code': 'LO4',
            'description': 'Write a term report detailing your experience and exposure.',
            'weight': 0.8
        }
    ]
    
    los = {}
    for lo_data in learning_outcomes_data:
        lo, created = LearningOutcome.objects.get_or_create(
            course=course,
            code=lo_data['code'],
            defaults={
                'description': lo_data['description'],
                'weight': lo_data['weight']
            }
        )
        los[lo_data['code']] = lo
        status = "✓ Created" if created else "↻ Exists"
        print(f"   {status} LO: {lo.code}")
    
    # 3. Assessments oluştur
    assessments_data = [
        {
            'name': 'Midterm I',
            'assessment_type': 'midterm',
            'total_points': 100,
            'weight': 25
        },
        {
            'name': 'Midterm II',
            'assessment_type': 'midterm',
            'total_points': 100,
            'weight': 25
        },
        {
            'name': 'Attendance & Participation',
            'assessment_type': 'homework',
            'total_points': 100,
            'weight': 10
        },
        {
            'name': 'Project (Presentations, Demo) - Final',
            'assessment_type': 'project',
            'total_points': 100,
            'weight': 40
        }
    ]
    
    assessments = {}
    for assess_data in assessments_data:
        weight = assess_data.pop('weight')
        assess, created = Assessment.objects.get_or_create(
            course=course,
            name=assess_data['name'],
            defaults=assess_data
        )
        assessments[assess.name] = (assess, weight)
        status = "✓ Created" if created else "↻ Exists"
        print(f"   {status} Assessment: {assess.name} ({weight}%)")
    
    # 4. Assessment → LO Mappings (resimden)
    assessment_lo_mappings = [
        # Midterm I
        ('Midterm I', 'LO1', 60),
        ('Midterm I', 'LO2', 40),
        
        # Midterm II (örnek ekledim)
        ('Midterm II', 'LO1', 40),
        ('Midterm II', 'LO2', 60),
        
        # Project
        ('Project (Presentations, Demo) - Final', 'LO2', 100),
        ('Project (Presentations, Demo) - Final', 'LO3', 100),
        ('Project (Presentations, Demo) - Final', 'LO4', 100),
    ]
    
    for assess_name, lo_code, weight in assessment_lo_mappings:
        if assess_name not in assessments or lo_code not in los:
            continue
            
        assess = assessments[assess_name][0]
        lo = los[lo_code]
        
        mapping, created = AssessmentToLoMapping.objects.get_or_create(
            assessment=assess,
            learning_outcome=lo,
            defaults={'contribution_weight': weight}
        )
        
        if not created and mapping.contribution_weight != weight:
            mapping.contribution_weight = weight
            mapping.save()
            print(f"   ↻ Updated: {assess.name} → {lo.code} ({weight}%)")
        elif created:
            print(f"   ✓ Created mapping: {assess.name} → {lo.code} ({weight}%)")
    
    # 5. LO → PO Mappings (resimden)
    # LO1 → PO1 (100%), LO1 → PO2 (50%)
    # LO2 → PO2 (100%)
    lo_po_mappings = [
        ('LO1', 'PO1', 100),
        ('LO1', 'PO2', 50),
        ('LO2', 'PO2', 100),
        # Ekstra örnekler
        ('LO3', 'PO3', 80),
        ('LO3', 'PO4', 60),
        ('LO4', 'PO7', 100),
    ]
    
    for lo_code, po_code, weight in lo_po_mappings:
        if lo_code not in los:
            continue
            
        try:
            po = ProgramOutcome.objects.get(code=po_code)
            lo = los[lo_code]
            
            mapping, created = LoToPoMapping.objects.get_or_create(
                learning_outcome=lo,
                program_outcome=po,
                defaults={'contribution_weight': weight}
            )
            
            if not created and mapping.contribution_weight != weight:
                mapping.contribution_weight = weight
                mapping.save()
                print(f"   ↻ Updated: {lo.code} → {po.code} ({weight}%)")
            elif created:
                print(f"   ✓ Created mapping: {lo.code} → {po.code} ({weight}%)")
        except ProgramOutcome.DoesNotExist:
            print(f"   ⚠️  PO {po_code} not found, skipping")
    
    print(f"\n✅ CSE 311 örnek data oluşturuldu!")
    print(f"   📚 Course: {course.code} - {course.name}")
    print(f"   📝 Learning Outcomes: {len(los)}")
    print(f"   📊 Assessments: {len(assessments)}")

if __name__ == '__main__':
    create_cse311_sample_data()
