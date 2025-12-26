"""
Demo kullanıcılar oluşturma scripti
Admin ve Instructor kullanıcıları oluşturur
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'po_manager.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

def create_demo_users():
    # Admin kullanıcı
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@university.edu',
            'first_name': 'System',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        UserProfile.objects.create(
            user=admin_user,
            user_type='admin',
            department='CSE'
        )
        print('✅ Admin kullanıcı oluşturuldu: admin / admin123')
    else:
        print('ℹ️  Admin kullanıcı zaten mevcut')
        # Profil yoksa oluştur
        if not hasattr(admin_user, 'profile'):
            UserProfile.objects.create(
                user=admin_user,
                user_type='admin',
                department='CSE'
            )
            print('   Admin profili oluşturuldu')

    # Instructor 1
    instructor1, created = User.objects.get_or_create(
        username='ahmet.yilmaz',
        defaults={
            'email': 'ahmet.yilmaz@university.edu',
            'first_name': 'Ahmet',
            'last_name': 'Yılmaz'
        }
    )
    if created:
        instructor1.set_password('hoca123')
        instructor1.save()
        UserProfile.objects.create(
            user=instructor1,
            user_type='instructor',
            department='CSE'
        )
        print('✅ Instructor oluşturuldu: ahmet.yilmaz / hoca123')
    else:
        print('ℹ️  ahmet.yilmaz kullanıcı zaten mevcut')
        if not hasattr(instructor1, 'profile'):
            UserProfile.objects.create(
                user=instructor1,
                user_type='instructor',
                department='CSE'
            )

    # Instructor 2
    instructor2, created = User.objects.get_or_create(
        username='elif.kaya',
        defaults={
            'email': 'elif.kaya@university.edu',
            'first_name': 'Elif',
            'last_name': 'Kaya'
        }
    )
    if created:
        instructor2.set_password('hoca123')
        instructor2.save()
        UserProfile.objects.create(
            user=instructor2,
            user_type='instructor',
            department='CSE'
        )
        print('✅ Instructor oluşturuldu: elif.kaya / hoca123')
    else:
        print('ℹ️  elif.kaya kullanıcı zaten mevcut')
        if not hasattr(instructor2, 'profile'):
            UserProfile.objects.create(
                user=instructor2,
                user_type='instructor',
                department='CSE'
            )

    print('\n📋 Demo Kullanıcılar:')
    print('=' * 50)
    print('Admin:')
    print('  Kullanıcı adı: admin')
    print('  Şifre: admin123')
    print('')
    print('Instructor 1:')
    print('  Kullanıcı adı: ahmet.yilmaz')
    print('  Şifre: hoca123')
    print('')
    print('Instructor 2:')
    print('  Kullanıcı adı: elif.kaya')
    print('  Şifre: hoca123')
    print('=' * 50)

if __name__ == '__main__':
    create_demo_users()
