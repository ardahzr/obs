#!/usr/bin/env python
"""
Program Outcomes (PO) için seed data script'i
11 adet PO eklenir
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'po_manager.settings')
django.setup()

from core.models import ProgramOutcome

# 11 Program Outcome
PROGRAM_OUTCOMES = [
    {
        'code': 'PO1',
        'description': 'Gain adequate knowledge in mathematics, science and related engineering discipline subjects; ability to use theoretical and applied knowledge in these fields in complex engineering problems.'
    },
    {
        'code': 'PO2',
        'description': 'Gain ability to identify, formulate and solve complex engineering problems; gain ability to choose and apply appropriate analysis and modeling methods for this purpose.'
    },
    {
        'code': 'PO3',
        'description': 'Gain ability to design a complex system, process, device or product to meet certain requirements under realistic constraints and conditions; ability to apply modern design methods for this purpose.'
    },
    {
        'code': 'PO4',
        'description': 'Analyze and create solutions to complex problems encountered in engineering applications of modern techniques and tools for development, have skills, gain the ability to use information technology effectively.'
    },
    {
        'code': 'PO5',
        'description': 'Gain ability to design experiments, conduct experiments, collect data, analyze and interpret results for the study of complex engineering problems or discipline-specific research topics.'
    },
    {
        'code': 'PO6',
        'description': 'Gain ability to work effectively in interdisciplinary and multidisciplinary teams; work individually.'
    },
    {
        'code': 'PO7',
        'description': 'Gain ability to communicate effectively in Turkish oral and written; knowledge of at least one foreign language; ability to write effective reports and understand written report, design and production reports, make effective presentations, give and receive clear and understandable instructions.'
    },
    {
        'code': 'PO8',
        'description': 'Gain awareness of of the need for lifelong learning; the ability to access information, monitor developments in science and technology, and constantly renew oneself.'
    },
    {
        'code': 'PO9',
        'description': 'Act in accordance with ethical principles, awareness of professional and ethical responsibility; gain knowledge of standards used in engineering applications'
    },
    {
        'code': 'PO10',
        'description': 'Gain knowledge of business practices such as Project Management, risk Management and change management; gain awareness about entrepreneurship, innovation; have information about sustainable development.'
    },
    {
        'code': 'PO11',
        'description': 'Gain knowledge of the effects of engineering practices on health, environment and safety in Universal and social dimensions and the problems reflected in the field of engineering of the era; gain awareness of the legal consequences of engineering solutions.'
    }
]

def seed_program_outcomes():
    """11 Program Outcome'ı veritabanına ekle"""
    print("🌱 Program Outcomes ekleniyor...")
    
    created_count = 0
    updated_count = 0
    
    for po_data in PROGRAM_OUTCOMES:
        po, created = ProgramOutcome.objects.get_or_create(
            code=po_data['code'],
            defaults={'description': po_data['description']}
        )
        
        if created:
            print(f"   ✓ {po.code} oluşturuldu")
            created_count += 1
        else:
            # Varolan PO'yu güncelle
            po.description = po_data['description']
            po.save()
            print(f"   ↻ {po.code} güncellendi")
            updated_count += 1
    
    print(f"\n✅ Toplam: {created_count} yeni, {updated_count} güncellendi")
    print(f"📊 Veritabanında toplam {ProgramOutcome.objects.count()} PO var")

if __name__ == '__main__':
    seed_program_outcomes()
