from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg, Sum, F, Q
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone
from collections import Counter

from .models import (
    Course, ProgramOutcome, LearningOutcome, 
    LoToPoMapping, Student, Assessment, AssessmentToLoMapping, Grade, UserProfile, Notification, Enrollment
)
from .serializers import (
    CourseSerializer, CourseDetailSerializer, ProgramOutcomeSerializer,
    LearningOutcomeSerializer, LoToPoMappingSerializer, StudentSerializer,
    AssessmentSerializer, AssessmentToLoMappingSerializer, GradeSerializer,
    LoginSerializer, RegisterSerializer, UserSerializer, NotificationSerializer
)
from .chat_utils import chat_with_gemini
from .email_utils import send_notification_email


# Create your views here.

@api_view(['GET'])
def test_api(request):
    return Response({"message": "Hello from Django API!"})


# ============ AUTH VIEWS ============

import requests as http_requests
from django.conf import settings as django_settings

def verify_recaptcha(token):
    """Verify reCAPTCHA token with Google"""
    if not token:
        return False
    
    secret_key = django_settings.RECAPTCHA_SECRET_KEY
    if not secret_key:
        # If no secret key configured, skip verification (development mode)
        return True
    
    try:
        response = http_requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret_key,
                'response': token
            },
            timeout=5
        )
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        return False


@api_view(['POST'])
def login_view(request):
    """User login"""
    # Verify reCAPTCHA
    recaptcha_token = request.data.get('recaptcha_token')
    if not verify_recaptcha(recaptcha_token):
        return Response({
            'success': False,
            'message': 'reCAPTCHA doğrulaması başarısız. Lütfen tekrar deneyin.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Get profile info
        try:
            profile = user.profile
            user_type = profile.user_type
        except UserProfile.DoesNotExist:
            user_type = 'instructor'
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user_type
            }
        })
    return Response({
        'success': False,
        'message': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    """User logout"""
    try:
        # Delete token
        if request.auth:
            request.auth.delete()
    except:
        pass
    
    return Response({
        'success': True,
        'message': 'Logout successful'
    })


@api_view(['POST'])
def register_view(request):
    """New user registration (admin only)"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'User created successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'message': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def me_view(request):
    """Mevcut kullanıcı bilgisi"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Token '):
        return Response({
            'success': False,
            'message': 'Token gerekli'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    token_key = auth_header.split(' ')[1]
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
        
        try:
            profile = user.profile
            user_type = profile.user_type
        except UserProfile.DoesNotExist:
            user_type = 'instructor'
        
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user_type
            }
        })
    except Token.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Geçersiz token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def create_instructor(request):
    """
    Admin tarafından instructor hesabı oluştur.
    Rastgele şifre oluşturur ve email ile gönderir.
    """
    import secrets
    import string
    
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Yetkilendirme gerekli'}, status=401)
    
    # Admin kontrolü
    try:
        if user.profile.user_type != 'admin':
            return Response({'success': False, 'message': 'Admin yetkisi gerekli'}, status=403)
    except UserProfile.DoesNotExist:
        return Response({'success': False, 'message': 'Admin yetkisi gerekli'}, status=403)
    
    # Gerekli alanları al
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    first_name = request.data.get('first_name', '').strip()
    last_name = request.data.get('last_name', '').strip()
    
    if not username or not email:
        return Response({
            'success': False,
            'message': 'Kullanıcı adı ve email zorunludur'
        }, status=400)
    
    # Kullanıcı adı veya email zaten var mı kontrol et
    if User.objects.filter(username=username).exists():
        return Response({
            'success': False,
            'message': 'Bu kullanıcı adı zaten kullanılıyor'
        }, status=400)
    
    if User.objects.filter(email=email).exists():
        return Response({
            'success': False,
            'message': 'Bu email adresi zaten kullanılıyor'
        }, status=400)
    
    # Rastgele şifre oluştur (12 karakter)
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    # Kullanıcı oluştur
    new_user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # UserProfile oluştur (instructor olarak)
    UserProfile.objects.create(user=new_user, user_type='instructor')
    
    # Email gönder
    from django.core.mail import send_mail
    from django.conf import settings as django_settings
    
    try:
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9fafb; padding: 25px; border: 1px solid #e5e7eb; }}
                .credentials {{ background: #1a1a2e; color: #fff; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .credentials p {{ margin: 10px 0; }}
                .label {{ color: #a0aec0; font-size: 12px; }}
                .value {{ font-size: 18px; font-weight: bold; color: #667eea; }}
                .footer {{ background: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px; }}
                .warning {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 12px; border-radius: 8px; margin-top: 15px; color: #92400e; font-size: 13px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🎓 PO Manager</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Program Outcome Management System</p>
                </div>
                <div class="content">
                    <h2>Hoş Geldiniz, {first_name or username}!</h2>
                    <p>PO Manager sistemine instructor olarak kaydınız oluşturulmuştur. Aşağıdaki bilgilerle giriş yapabilirsiniz:</p>
                    
                    <div class="credentials">
                        <p><span class="label">KULLANICI ADI</span><br><span class="value">{username}</span></p>
                        <p><span class="label">ŞİFRE</span><br><span class="value">{password}</span></p>
                    </div>
                    
                    <div class="warning">
                        ⚠️ Güvenliğiniz için ilk girişten sonra şifrenizi değiştirmenizi öneririz.
                    </div>
                </div>
                <div class="footer">
                    <p>Bu email PO Manager sistemi tarafından otomatik olarak gönderilmiştir.</p>
                    <p>© 2025 PO Manager - Program Outcome Management System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_mail(
            subject='🎓 PO Manager - Hesap Bilgileriniz',
            message=f'Kullanıcı adı: {username}\nŞifre: {password}',
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        email_sent = True
    except Exception as e:
        print(f"Email gönderme hatası: {e}")
        email_sent = False
    
    return Response({
        'success': True,
        'message': 'Instructor hesabı başarıyla oluşturuldu',
        'email_sent': email_sent,
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'user_type': 'instructor'
        }
    }, status=201)


class CourseViewSet(viewsets.ModelViewSet):
    """Ders CRUD işlemleri"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Detaylı ders bilgisi (LO'lar ve assessments dahil)"""
        course = self.get_object()
        serializer = CourseDetailSerializer(course)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def learning_outcomes(self, request, pk=None):
        """Dersin learning outcomes listesi"""
        course = self.get_object()
        los = course.learning_outcomes.all()
        serializer = LearningOutcomeSerializer(los, many=True)
        return Response(serializer.data)


class ProgramOutcomeViewSet(viewsets.ModelViewSet):
    """Program Outcome CRUD işlemleri"""
    queryset = ProgramOutcome.objects.all()
    serializer_class = ProgramOutcomeSerializer


class LearningOutcomeViewSet(viewsets.ModelViewSet):
    """Learning Outcome CRUD işlemleri"""
    queryset = LearningOutcome.objects.all()
    serializer_class = LearningOutcomeSerializer
    
    @action(detail=True, methods=['get', 'post'])
    def mappings(self, request, pk=None):
        """LO'nun PO mappings'leri"""
        lo = self.get_object()
        
        if request.method == 'GET':
            mappings = lo.po_mappings.all()
            serializer = LoToPoMappingSerializer(mappings, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Yeni mapping oluştur
            data = request.data.copy()
            data['learning_outcome'] = lo.id
            serializer = LoToPoMappingSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoToPoMappingViewSet(viewsets.ModelViewSet):
    """LO to PO Mapping CRUD işlemleri"""
    queryset = LoToPoMapping.objects.all()
    serializer_class = LoToPoMappingSerializer


class AssessmentToLoMappingViewSet(viewsets.ModelViewSet):
    """Assessment to LO Mapping CRUD işlemleri"""
    queryset = AssessmentToLoMapping.objects.all()
    serializer_class = AssessmentToLoMappingSerializer


class StudentViewSet(viewsets.ModelViewSet):
    """Öğrenci CRUD işlemleri"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get_queryset(self):
        """Ders bazında filtreleme desteği"""
        queryset = Student.objects.all()
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(enrollments__course_id=course_id)
        return queryset.distinct()
    
    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """Öğrencinin notları"""
        student = self.get_object()
        grades = student.grades.all()
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def po_scores(self, request, pk=None):
        """
        Öğrencinin PO skorlarını hesapla
        Formül: (Assessment_Score * Assessment_Weight * LO_Weight) / Total_Weight
        """
        student = self.get_object()
        
        # Tüm PO'ları al
        pos = ProgramOutcome.objects.all()
        results = []
        
        for po in pos:
            # Bu PO'ya bağlı tüm LO mappinglerini bul
            lo_mappings = LoToPoMapping.objects.filter(program_outcome=po)
            
            total_weighted_score = 0
            total_weight_sum = 0
            
            for lo_map in lo_mappings:
                lo = lo_map.learning_outcome
                lo_po_weight = lo_map.contribution_weight  # LO -> PO ağırlığı (0-1 arası)
                
                # Bu LO'ya bağlı assessment mappinglerini bul
                assess_mappings = AssessmentToLoMapping.objects.filter(learning_outcome=lo)
                
                for assess_map in assess_mappings:
                    assessment = assess_map.assessment
                    assess_lo_weight = assess_map.contribution_weight  # Assessment -> LO ağırlığı (0-1 arası)
                    
                    # Öğrencinin bu assessment'taki notunu bul
                    try:
                        grade = Grade.objects.get(assessment=assessment, student=student)
                        # Notu 100 üzerinden al
                        score = grade.percentage
                        
                        # Katkıyı hesapla: Not * (Assess->LO) * (LO->PO)
                        contribution = score * assess_lo_weight * lo_po_weight
                        
                        # Toplam ağırlık paydası için: (Assess->LO) * (LO->PO)
                        weight_factor = assess_lo_weight * lo_po_weight
                        
                        total_weighted_score += contribution
                        total_weight_sum += weight_factor
                        
                    except Grade.DoesNotExist:
                        continue
            
            # Normalize et: Toplam Puan / Toplam Ağırlık
            if total_weight_sum > 0:
                normalized_score = total_weighted_score / total_weight_sum
            else:
                normalized_score = 0
            
            results.append({
                'po_code': po.code,
                'po_description': po.description,
                'score': round(normalized_score, 2)
            })
        
        return Response({
            'student': student.student_no,
            'po_scores': results
        })


class AssessmentViewSet(viewsets.ModelViewSet):
    """Değerlendirme CRUD işlemleri"""
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer


class GradeViewSet(viewsets.ModelViewSet):
    """Not CRUD işlemleri"""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


@api_view(['POST'])
def chat_view(request):
    """Chatbot endpoint"""
    user_message = request.data.get('message')
    if not user_message:
        return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # API Key provided by user
    api_key = "AIzaSyAj7cQxoREu3UEv-JU5jllTLYk6U9E6pM8"
    
    try:
        response_text = chat_with_gemini(user_message, api_key)
        return Response({"response": response_text})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============ NOTIFICATION & APPROVAL VIEWS ============

def get_user_from_token(request):
    """Token'dan kullanıcıyı al"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Token '):
        return None
    token_key = auth_header.split(' ')[1]
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return None


@api_view(['GET'])
def get_notifications(request):
    """Get user notifications"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Authorization required'}, status=401)
    
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    
    unread_count = notifications.filter(is_read=False).count()
    
    return Response({
        'success': True,
        'notifications': serializer.data,
        'unread_count': unread_count
    })


@api_view(['POST'])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Authorization required'}, status=401)
    
    try:
        notification = Notification.objects.get(id=notification_id, recipient=user)
        notification.is_read = True
        notification.save()
        return Response({'success': True, 'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'success': False, 'message': 'Notification not found'}, status=404)


@api_view(['POST'])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Authorization required'}, status=401)
    
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
    return Response({'success': True, 'message': 'All notifications marked as read'})


@api_view(['POST'])
def submit_course_for_approval(request, course_id):
    """Submit course for approval (Instructor)"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Authorization required'}, status=401)
    
    try:
        course = Course.objects.get(id=course_id)
        
        # Check course ownership - allow if instructor not assigned, user is instructor, or user is admin
        is_admin = hasattr(user, 'profile') and user.profile.user_type == 'admin'
        is_owner = course.instructor == user or course.instructor is None
        
        if not is_owner and not is_admin:
            return Response({'success': False, 'message': 'You do not have permission to submit this course'}, status=403)
        
        # Check if already pending
        if course.approval_status == 'pending':
            return Response({'success': False, 'message': 'This course is already pending approval'}, status=400)
        
        # If instructor not assigned, assign the submitting user
        if course.instructor is None:
            course.instructor = user
        
        # Submit course for approval
        course.approval_status = 'pending'
        course.submitted_at = timezone.now()
        course.save()
        
        # Send notification to all admin users
        admins = User.objects.filter(profile__user_type='admin')
        for admin in admins:
            notification = Notification.objects.create(
                recipient=admin,
                sender=user,
                course=course,
                notification_type='approval_request',
                message=f'{user.get_full_name() or user.username} submitted "{course.code} - {course.name}" for your approval.'
            )
            # Send email notification
            send_notification_email(notification)
        
        return Response({
            'success': True, 
            'message': 'Course submitted for approval',
            'approval_status': 'pending'
        })
    except Course.DoesNotExist:
        return Response({'success': False, 'message': 'Course not found'}, status=404)


@api_view(['GET'])
def get_pending_approvals(request):
    """Get pending approvals (Admin)"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Authorization required'}, status=401)
    
    # Admin check
    try:
        if user.profile.user_type != 'admin':
            return Response({'success': False, 'message': 'Admin permission required'}, status=403)
    except UserProfile.DoesNotExist:
        return Response({'success': False, 'message': 'Admin permission required'}, status=403)
    
    pending_courses = Course.objects.filter(approval_status='pending').select_related('instructor')
    serializer = CourseSerializer(pending_courses, many=True)
    
    return Response({
        'success': True,
        'pending_courses': serializer.data
    })


@api_view(['POST'])
def approve_course(request, course_id):
    """Dersi onayla (Admin)"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Yetkilendirme gerekli'}, status=401)
    
    # Admin kontrolü
    try:
        if user.profile.user_type != 'admin':
            return Response({'success': False, 'message': 'Admin permission required'}, status=403)
    except UserProfile.DoesNotExist:
        return Response({'success': False, 'message': 'Admin permission required'}, status=403)
    
    message = request.data.get('message', 'Your course has been approved.')
    
    try:
        course = Course.objects.get(id=course_id)
        
        if course.approval_status != 'pending':
            return Response({'success': False, 'message': 'This course is not pending approval'}, status=400)
        
        # Approve the course
        course.approval_status = 'approved'
        course.reviewed_at = timezone.now()
        course.reviewed_by = user
        course.rejection_reason = None
        course.save()
        
        # Send notification to course owner
        if course.instructor:
            notification = Notification.objects.create(
                recipient=course.instructor,
                sender=user,
                course=course,
                notification_type='approved',
                message=f'"{course.code} - {course.name}" has been approved. {message}'
            )
            # Send email notification
            send_notification_email(notification)
        
        return Response({
            'success': True,
            'message': 'Course approved',
            'approval_status': 'approved'
        })
    except Course.DoesNotExist:
        return Response({'success': False, 'message': 'Ders bulunamadı'}, status=404)


@api_view(['POST'])
def reject_course(request, course_id):
    """Reject course (Admin)"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Authorization required'}, status=401)
    
    # Admin check
    try:
        if user.profile.user_type != 'admin':
            return Response({'success': False, 'message': 'Admin permission required'}, status=403)
    except UserProfile.DoesNotExist:
        return Response({'success': False, 'message': 'Admin permission required'}, status=403)
    
    reason = request.data.get('reason', '')
    if not reason:
        return Response({'success': False, 'message': 'Rejection reason is required'}, status=400)
    
    try:
        course = Course.objects.get(id=course_id)
        
        if course.approval_status != 'pending':
            return Response({'success': False, 'message': 'This course is not pending approval'}, status=400)
        
        # Reject the course
        course.approval_status = 'rejected'
        course.reviewed_at = timezone.now()
        course.reviewed_by = user
        course.rejection_reason = reason
        course.save()
        
        # Send notification to course owner
        if course.instructor:
            notification = Notification.objects.create(
                recipient=course.instructor,
                sender=user,
                course=course,
                notification_type='rejected',
                message=f'"{course.code} - {course.name}" has been rejected. Reason: {reason}'
            )
            # Send email notification
            send_notification_email(notification)
        
        return Response({
            'success': True,
            'message': 'Course rejected',
            'approval_status': 'rejected'
        })
    except Course.DoesNotExist:
        return Response({'success': False, 'message': 'Course not found'}, status=404)


def detect_assessment_type(name):
    """Assessment adından türünü tahmin et"""
    name_lower = name.lower()
    if 'midterm' in name_lower or 'vize' in name_lower:
        return 'midterm'
    elif 'final' in name_lower:
        return 'final'
    elif 'quiz' in name_lower:
        return 'quiz'
    elif 'project' in name_lower or 'proje' in name_lower:
        return 'project'
    elif 'homework' in name_lower or 'ödev' in name_lower:
        return 'homework'
    elif 'attendance' in name_lower or 'devam' in name_lower:
        return 'homework'
    return 'quiz'


@api_view(['POST'])
def import_obs_excel(request):
    """
    OBS Excel formatından ders, öğrenci, assessment ve notları içeri aktar.
    """
    import pandas as pd
    import re
    from io import BytesIO
    
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Authorization required'}, status=401)
    
    if 'file' not in request.FILES:
        return Response({'success': False, 'message': 'No file provided'}, status=400)
    
    try:
        excel_file = request.FILES['file']
        df = pd.read_excel(BytesIO(excel_file.read()))
    except Exception as e:
        return Response({'success': False, 'message': f'Excel read error: {str(e)}'}, status=400)
    
    # Course bilgilerini al
    course_id = request.data.get('course_id')
    course_code = request.data.get('course_code', '')
    course_name = request.data.get('course_name', '')
    
    # Sütun isimlerinden course code çıkar (örn: "Öğrenci No_0833AB" -> "0833AB")
    if not course_code:
        for col in df.columns:
            if '_' in col:
                course_code = col.split('_')[-1]
                break
    
    if not course_code:
        return Response({'success': False, 'message': 'Course code not found'}, status=400)
    
    if not course_name:
        course_name = course_code
    
    # Course oluştur veya bul
    created_course = False
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'success': False, 'message': 'Course not found'}, status=404)
    else:
        course, created_course = Course.objects.get_or_create(
            code=course_code,
            defaults={
                'name': course_name,
                'department': 'CSE',
                'instructor': user
            }
        )
    
    # Assessment sütunlarını tespit et: "Assessment Name(%Weight)_CourseCode"
    assessment_pattern = re.compile(r'^(.+?)\(%(\d+)\)_')
    assessment_columns = {}
    
    for col in df.columns:
        match = assessment_pattern.match(col)
        if match:
            assessment_name = match.group(1).strip()
            weight = int(match.group(2))
            assessment_columns[col] = {
                'name': assessment_name,
                'weight': weight
            }
    
    # Assessment'ları oluştur
    created_assessments = 0
    assessments_map = {}
    
    for col, info in assessment_columns.items():
        assessment, created = Assessment.objects.get_or_create(
            course=course,
            name=info['name'],
            defaults={
                'assessment_type': detect_assessment_type(info['name']),
                'total_points': 100  # Default 100 puan üzerinden
            }
        )
        assessments_map[col] = assessment
        if created:
            created_assessments += 1
    
    # Öğrenci sütunlarını bul
    student_no_col = None
    first_name_col = None
    last_name_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'öğrenci no' in col_lower or 'student no' in col_lower or 'no_' in col_lower:
            if 'öğrenci no' in col_lower or 'student' in col_lower:
                student_no_col = col
        elif 'adı_' in col_lower or 'first' in col_lower:
            first_name_col = col
        elif 'soyadı_' in col_lower or 'last' in col_lower:
            last_name_col = col
    
    if not student_no_col:
        # Fallback: İkinci sütunu kullan (genellikle Öğrenci No)
        if len(df.columns) > 1:
            student_no_col = df.columns[1]
    
    if not student_no_col:
        return Response({'success': False, 'message': 'Student ID column not found'}, status=400)
    
    # Öğrenci ve notları işle
    created_students = 0
    updated_students = 0
    created_grades = 0
    
    for index, row in df.iterrows():
        student_no = str(row.get(student_no_col, '')).strip()
        if not student_no or student_no == 'nan':
            continue
        
        first_name = str(row.get(first_name_col, '')).strip() if first_name_col else ''
        last_name = str(row.get(last_name_col, '')).strip() if last_name_col else ''
        
        if first_name == 'nan':
            first_name = ''
        if last_name == 'nan':
            last_name = ''
        
        # Öğrenci oluştur veya güncelle
        try:
            student = Student.objects.get(student_no=student_no)
            # Mevcut öğrenciyi güncelle
            if first_name and last_name:
                student.user.first_name = first_name
                student.user.last_name = last_name
                student.user.save()
            updated_students += 1
        except Student.DoesNotExist:
            # Yeni kullanıcı ve öğrenci oluştur
            username = f"student_{student_no}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name or 'Öğrenci',
                    'last_name': last_name or student_no,
                    'email': f"{student_no}@student.edu"
                }
            )
            student = Student.objects.create(
                user=user,
                student_no=student_no,
                department='CSE'
            )
            created_students += 1
        
        # Enrollment oluştur
        Enrollment.objects.get_or_create(student=student, course=course)
        
        # Notları kaydet
        for col, assessment in assessments_map.items():
            try:
                grade_value = row.get(col)
                if pd.notna(grade_value):
                    points = float(grade_value)
                    grade, g_created = Grade.objects.get_or_create(
                        student=student,
                        assessment=assessment,
                        defaults={'points': points}
                    )
                    if not g_created and grade.points != points:
                        grade.points = points
                        grade.save()
                    if g_created:
                        created_grades += 1
            except (ValueError, TypeError):
                pass
    
    return Response({
        'success': True,
        'course_code': course.code,
        'course_created': created_course,
        'students_created': created_students,
        'students_updated': updated_students,
        'assessments_created': created_assessments,
        'grades_created': created_grades
    })
