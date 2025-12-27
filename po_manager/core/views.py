from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg, Sum, F, Q
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone

from .models import (
    Course, ProgramOutcome, LearningOutcome, 
    LoToPoMapping, Student, Assessment, AssessmentToLoMapping, Grade, UserProfile, Notification
)
from .serializers import (
    CourseSerializer, CourseDetailSerializer, ProgramOutcomeSerializer,
    LearningOutcomeSerializer, LoToPoMappingSerializer, StudentSerializer,
    AssessmentSerializer, AssessmentToLoMappingSerializer, GradeSerializer,
    LoginSerializer, RegisterSerializer, UserSerializer, NotificationSerializer
)
from .chat_utils import chat_with_gemini


# Create your views here.

@api_view(['GET'])
def test_api(request):
    return Response({"message": "Hello from Django API!"})


# ============ AUTH VIEWS ============

@api_view(['POST'])
def login_view(request):
    """Kullanıcı girişi"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Profil bilgisi al
        try:
            profile = user.profile
            user_type = profile.user_type
        except UserProfile.DoesNotExist:
            user_type = 'instructor'
        
        return Response({
            'success': True,
            'message': 'Giriş başarılı',
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
    """Kullanıcı çıkışı"""
    try:
        # Token'ı sil
        if request.auth:
            request.auth.delete()
    except:
        pass
    
    return Response({
        'success': True,
        'message': 'Çıkış başarılı'
    })


@api_view(['POST'])
def register_view(request):
    """Yeni kullanıcı kaydı (sadece admin yapabilir)"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'Kullanıcı başarıyla oluşturuldu',
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
    """Kullanıcının bildirimlerini getir"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Yetkilendirme gerekli'}, status=401)
    
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
    """Bildirimi okundu olarak işaretle"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Yetkilendirme gerekli'}, status=401)
    
    try:
        notification = Notification.objects.get(id=notification_id, recipient=user)
        notification.is_read = True
        notification.save()
        return Response({'success': True, 'message': 'Bildirim okundu olarak işaretlendi'})
    except Notification.DoesNotExist:
        return Response({'success': False, 'message': 'Bildirim bulunamadı'}, status=404)


@api_view(['POST'])
def mark_all_notifications_read(request):
    """Tüm bildirimleri okundu olarak işaretle"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Yetkilendirme gerekli'}, status=401)
    
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
    return Response({'success': True, 'message': 'Tüm bildirimler okundu olarak işaretlendi'})


@api_view(['POST'])
def submit_course_for_approval(request, course_id):
    """Dersi onaya gönder (Instructor)"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Yetkilendirme gerekli'}, status=401)
    
    try:
        course = Course.objects.get(id=course_id)
        
        # Ders sahibi kontrolü - instructor atanmamışsa veya kullanıcı instructor ise veya admin ise izin ver
        is_admin = hasattr(user, 'profile') and user.profile.user_type == 'admin'
        is_owner = course.instructor == user or course.instructor is None
        
        if not is_owner and not is_admin:
            return Response({'success': False, 'message': 'Bu dersi onaya gönderme yetkiniz yok'}, status=403)
        
        # Zaten onay bekliyor mu kontrol et
        if course.approval_status == 'pending':
            return Response({'success': False, 'message': 'Bu ders zaten onay bekliyor'}, status=400)
        
        # Eğer instructor atanmamışsa, gönderen kullanıcıyı instructor olarak ata
        if course.instructor is None:
            course.instructor = user
        
        # Dersi onaya gönder
        course.approval_status = 'pending'
        course.submitted_at = timezone.now()
        course.save()
        
        # Tüm admin kullanıcılarına bildirim gönder
        admins = User.objects.filter(profile__user_type='admin')
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                sender=user,
                course=course,
                notification_type='approval_request',
                message=f'{user.get_full_name() or user.username} "{course.code} - {course.name}" dersini onayınıza sundu.'
            )
        
        return Response({
            'success': True, 
            'message': 'Ders onaya gönderildi',
            'approval_status': 'pending'
        })
    except Course.DoesNotExist:
        return Response({'success': False, 'message': 'Ders bulunamadı'}, status=404)


@api_view(['GET'])
def get_pending_approvals(request):
    """Bekleyen onayları getir (Admin)"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Yetkilendirme gerekli'}, status=401)
    
    # Admin kontrolü
    try:
        if user.profile.user_type != 'admin':
            return Response({'success': False, 'message': 'Admin yetkisi gerekli'}, status=403)
    except UserProfile.DoesNotExist:
        return Response({'success': False, 'message': 'Admin yetkisi gerekli'}, status=403)
    
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
            return Response({'success': False, 'message': 'Admin yetkisi gerekli'}, status=403)
    except UserProfile.DoesNotExist:
        return Response({'success': False, 'message': 'Admin yetkisi gerekli'}, status=403)
    
    message = request.data.get('message', 'Dersiniz onaylandı.')
    
    try:
        course = Course.objects.get(id=course_id)
        
        if course.approval_status != 'pending':
            return Response({'success': False, 'message': 'Bu ders onay bekliyor durumunda değil'}, status=400)
        
        # Dersi onayla
        course.approval_status = 'approved'
        course.reviewed_at = timezone.now()
        course.reviewed_by = user
        course.rejection_reason = None
        course.save()
        
        # Ders sahibine bildirim gönder
        if course.instructor:
            Notification.objects.create(
                recipient=course.instructor,
                sender=user,
                course=course,
                notification_type='approved',
                message=f'"{course.code} - {course.name}" dersiniz onaylandı. {message}'
            )
        
        return Response({
            'success': True,
            'message': 'Ders onaylandı',
            'approval_status': 'approved'
        })
    except Course.DoesNotExist:
        return Response({'success': False, 'message': 'Ders bulunamadı'}, status=404)


@api_view(['POST'])
def reject_course(request, course_id):
    """Dersi reddet (Admin)"""
    user = get_user_from_token(request)
    if not user:
        return Response({'success': False, 'message': 'Yetkilendirme gerekli'}, status=401)
    
    # Admin kontrolü
    try:
        if user.profile.user_type != 'admin':
            return Response({'success': False, 'message': 'Admin yetkisi gerekli'}, status=403)
    except UserProfile.DoesNotExist:
        return Response({'success': False, 'message': 'Admin yetkisi gerekli'}, status=403)
    
    reason = request.data.get('reason', '')
    if not reason:
        return Response({'success': False, 'message': 'Red sebebi gerekli'}, status=400)
    
    try:
        course = Course.objects.get(id=course_id)
        
        if course.approval_status != 'pending':
            return Response({'success': False, 'message': 'Bu ders onay bekliyor durumunda değil'}, status=400)
        
        # Dersi reddet
        course.approval_status = 'rejected'
        course.reviewed_at = timezone.now()
        course.reviewed_by = user
        course.rejection_reason = reason
        course.save()
        
        # Ders sahibine bildirim gönder
        if course.instructor:
            Notification.objects.create(
                recipient=course.instructor,
                sender=user,
                course=course,
                notification_type='rejected',
                message=f'"{course.code} - {course.name}" dersiniz reddedildi. Sebep: {reason}'
            )
        
        return Response({
            'success': True,
            'message': 'Ders reddedildi',
            'approval_status': 'rejected'
        })
    except Course.DoesNotExist:
        return Response({'success': False, 'message': 'Ders bulunamadı'}, status=404)
