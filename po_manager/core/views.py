from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg, Sum, F, Q
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from collections import Counter
import pandas as pd

from .models import (
    Course, ProgramOutcome, LearningOutcome, 
    LoToPoMapping, Student, Assessment, AssessmentToLoMapping, Grade, UserProfile, Enrollment
)
from .serializers import (
    CourseSerializer, CourseDetailSerializer, ProgramOutcomeSerializer,
    LearningOutcomeSerializer, LoToPoMappingSerializer, StudentSerializer,
    AssessmentSerializer, AssessmentToLoMappingSerializer, GradeSerializer,
    LoginSerializer, RegisterSerializer, UserSerializer
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
        return 'homework'  # Attendance için homework kullanıyoruz
    return 'quiz'  # Default


# ============ EXCEL IMPORT ============


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_obs_excel(request):
    """
    OBS Excel formatından ders ve öğrencileri içeri aktar.

    Beklenen input (multipart/form-data):
      - file: XLSX dosyası
      - course_code (opsiyonel): Ders kodu, verilmezse sütun son ekinden türetilir (örn. _0833AB)
      - course_name (opsiyonel): Ders adı; yoksa ders kodu ile oluşturulur

    İşlemler:
      1) Course yoksa oluşturur, eğitmeni giriş yapan kullanıcı yapar.
      2) Öğrencileri (User + Student) ekler, mevcutsa atlar.
    """
    upload = request.FILES.get('file')
    if not upload:
        return Response({'success': False, 'message': 'file alanı (XLSX) gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    # Dosyayı pandas ile oku
    try:
        df = pd.read_excel(upload)
    except Exception as exc:
        return Response({'success': False, 'message': f'Excel okunamadı: {exc}'}, status=status.HTTP_400_BAD_REQUEST)

    if df.empty:
        return Response({'success': False, 'message': 'Excel boş görünüyor'}, status=status.HTTP_400_BAD_REQUEST)

    # Mevcut ders ID'si verilmişse onu kullan
    course_id = request.data.get('course_id')
    created_course = False
    
    if course_id:
        # Mevcut derse kaydet
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'success': False, 'message': 'Seçilen ders bulunamadı'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Yeni ders oluştur
        # Sütun son ekinden ders kodu tahmini (örn: "Adı_0833AB")
        suffixes = []
        for col in df.columns:
            if isinstance(col, str) and '_' in col:
                suffixes.append(col.split('_')[-1])
        course_code = request.data.get('course_code') or (Counter(suffixes).most_common(1)[0][0] if suffixes else None)
        if not course_code:
            return Response({'success': False, 'message': 'Ders kodu bulunamadı; course_code gönderin veya mevcut ders seçin.'}, status=status.HTTP_400_BAD_REQUEST)

        course_name = request.data.get('course_name') or f"Imported Course {course_code}"

        # Course oluştur / bul
        course, created_course = Course.objects.get_or_create(
            code=course_code,
            defaults={
                'name': course_name,
                'semester': '',
                'department': getattr(getattr(request.user, 'profile', None), 'department', 'CSE'),
                'instructor': request.user,
            }
        )
        if not created_course and course.instructor is None:
            course.instructor = request.user
            course.save(update_fields=['instructor'])

    # Sütun eşleştirmeleri
    def find_col(substring, default=None):
        for c in df.columns:
            if isinstance(c, str) and substring.lower() in c.lower():
                return c
        return default

    col_student_no = find_col('öğrenci no') or find_col('ogrenci')
    col_first = find_col('adı') or find_col('ad')
    col_last = find_col('soyadı') or find_col('soyad')

    if not col_student_no:
        return Response({'success': False, 'message': 'Öğrenci numarası kolonu bulunamadı'}, status=status.HTTP_400_BAD_REQUEST)

    # Assessment sütunlarını tespit et (format: "Assessment Name(%Weight)_CourseCode")
    import re
    assessment_columns = {}  # {column_name: {'name': str, 'weight': float}}
    assessment_pattern = re.compile(r'^(.+?)\(%(\d+)\)_')
    
    for col in df.columns:
        if isinstance(col, str):
            match = assessment_pattern.match(col)
            if match:
                assess_name = match.group(1).strip()
                weight = int(match.group(2))
                assessment_columns[col] = {'name': assess_name, 'weight': weight}
    
    # Assessment'ları oluştur
    created_assessments = 0
    assessments_map = {}  # {column_name: Assessment instance}
    
    for col, info in assessment_columns.items():
        assessment, a_created = Assessment.objects.get_or_create(
            course=course,
            name=info['name'],
            defaults={
                'assessment_type': detect_assessment_type(info['name']),
                'total_points': 100,  # Default 100 puan üzerinden
            }
        )
        assessments_map[col] = assessment
        if a_created:
            created_assessments += 1

    created_students = 0
    skipped_students = 0
    created_grades = 0
    for _, row in df.iterrows():
        student_no = str(row.get(col_student_no, '')).strip()
        if not student_no or student_no.lower() == 'nan':
            skipped_students += 1
            continue

        first_name = ''
        last_name = ''
        if col_first:
            first_name = str(row.get(col_first, '')).strip()
        if col_last:
            last_name = str(row.get(col_last, '')).strip()

        user, user_created = User.objects.get_or_create(
            username=student_no,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f"{student_no}@example.com",
            }
        )
        if user_created:
            user.set_password(student_no)
            user.save()
        else:
            # Güncelle isimler boş değilse
            update_fields = []
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                update_fields.append('first_name')
            if last_name and user.last_name != last_name:
                user.last_name = last_name
                update_fields.append('last_name')
            if update_fields:
                user.save(update_fields=update_fields)

        student, s_created = Student.objects.get_or_create(
            student_no=student_no,
            defaults={
                'user': user,
                'department': course.department,
            }
        )
        if s_created:
            created_students += 1
        else:
            skipped_students += 1

        # Enrollment oluştur (öğrenciyi derse kaydet)
        Enrollment.objects.get_or_create(student=student, course=course)

        # Notları ekle
        for col, assessment in assessments_map.items():
            grade_value = row.get(col)
            # NaN veya boş değilse not ekle
            if pd.notna(grade_value):
                try:
                    points = float(grade_value)
                    grade, g_created = Grade.objects.get_or_create(
                        assessment=assessment,
                        student=student,
                        defaults={'points': points}
                    )
                    if not g_created and grade.points != points:
                        grade.points = points
                        grade.save(update_fields=['points'])
                    if g_created:
                        created_grades += 1
                except (ValueError, TypeError):
                    pass  # Geçersiz not değeri, atla

    return Response({
        'success': True,
        'course': course.code,
        'course_created': created_course,
        'students_created': created_students,
        'students_skipped': skipped_students,
        'assessments_created': created_assessments,
        'grades_created': created_grades,
    }, status=status.HTTP_201_CREATED)
