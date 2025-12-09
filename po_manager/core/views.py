from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Sum, F, Q

from .models import (
    Course, ProgramOutcome, LearningOutcome, 
    LoToPoMapping, Student, Assessment, AssessmentToLoMapping, Grade
)
from .serializers import (
    CourseSerializer, CourseDetailSerializer, ProgramOutcomeSerializer,
    LearningOutcomeSerializer, LoToPoMappingSerializer, StudentSerializer,
    AssessmentSerializer, AssessmentToLoMappingSerializer, GradeSerializer
)
from .chat_utils import chat_with_gemini


# Create your views here.

@api_view(['GET'])
def test_api(request):
    return Response({"message": "Hello from Django API!"})


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
