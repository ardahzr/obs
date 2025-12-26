from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import (
    Course, ProgramOutcome, LearningOutcome, 
    LoToPoMapping, Student, Assessment, AssessmentToLoMapping, Grade, UserProfile
)


class UserProfileSerializer(serializers.ModelSerializer):
    """Kullanıcı profil serializer"""
    class Meta:
        model = UserProfile
        fields = ['user_type', 'department', 'is_admin', 'is_instructor']


class UserSerializer(serializers.ModelSerializer):
    """Kullanıcı serializer"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("Hesabınız aktif değil.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Kullanıcı adı veya şifre hatalı.")
        else:
            raise serializers.ValidationError("Kullanıcı adı ve şifre gerekli.")
        
        return data


class RegisterSerializer(serializers.Serializer):
    """Register serializer - sadece admin yeni kullanıcı oluşturabilir"""
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, default='')
    last_name = serializers.CharField(required=False, default='')
    user_type = serializers.ChoiceField(choices=['admin', 'instructor'], default='instructor')
    department = serializers.CharField(default='CSE')
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu kullanıcı adı zaten kullanılıyor.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email adresi zaten kullanılıyor.")
        return value
    
    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        department = validated_data.pop('department')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        UserProfile.objects.create(
            user=user,
            user_type=user_type,
            department=department
        )
        
        return user


class CourseSerializer(serializers.ModelSerializer):
    """Ders serializer"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'semester', 'department', 'instructor', 'instructor_name']


class ProgramOutcomeSerializer(serializers.ModelSerializer):
    """Program Outcome serializer"""
    class Meta:
        model = ProgramOutcome
        fields = ['id', 'code', 'description']


class LearningOutcomeSerializer(serializers.ModelSerializer):
    """Learning Outcome serializer"""
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = LearningOutcome
        fields = ['id', 'course', 'course_code', 'code', 'description', 'weight']


class LoToPoMappingSerializer(serializers.ModelSerializer):
    """LO to PO Mapping serializer"""
    lo_code = serializers.CharField(source='learning_outcome.code', read_only=True)
    po_code = serializers.CharField(source='program_outcome.code', read_only=True)
    
    class Meta:
        model = LoToPoMapping
        fields = ['id', 'learning_outcome', 'lo_code', 'program_outcome', 'po_code', 'contribution_weight']


class AssessmentToLoMappingSerializer(serializers.ModelSerializer):
    """Assessment to LO Mapping serializer"""
    assessment_name = serializers.CharField(source='assessment.name', read_only=True)
    lo_code = serializers.CharField(source='learning_outcome.code', read_only=True)
    
    class Meta:
        model = AssessmentToLoMapping
        fields = ['id', 'assessment', 'assessment_name', 'learning_outcome', 'lo_code', 'contribution_weight']


class StudentSerializer(serializers.ModelSerializer):
    """Öğrenci serializer"""
    user = UserSerializer(read_only=True)
    
    # User bilgileri için yazılabilir alanlar
    username = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=False, default='')
    last_name = serializers.CharField(write_only=True, required=False, default='')
    email = serializers.EmailField(write_only=True, required=False, default='')
    student_number = serializers.CharField(source='student_no', required=True)
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'student_number', 'student_no', 'department', 
                  'username', 'first_name', 'last_name', 'email']
    
    def create(self, validated_data):
        # User bilgilerini al ve validated_data'dan çıkar
        username = validated_data.pop('username')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email', '')
        
        # User oluştur
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        # Student oluştur
        student = Student.objects.create(user=user, **validated_data)
        return student


class AssessmentSerializer(serializers.ModelSerializer):
    """Değerlendirme serializer"""
    course_code = serializers.CharField(source='course.code', read_only=True)
    learning_outcome_codes = serializers.SerializerMethodField()
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'course', 'course_code', 'name', 'assessment_type', 
            'total_points', 'date', 'learning_outcomes', 'learning_outcome_codes'
        ]
    
    def get_learning_outcome_codes(self, obj):
        return [lo.code for lo in obj.learning_outcomes.all()]


class GradeSerializer(serializers.ModelSerializer):
    """Not serializer"""
    student_no = serializers.CharField(source='student.student_no', read_only=True)
    assessment_name = serializers.CharField(source='assessment.name', read_only=True)
    percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id', 'assessment', 'assessment_name', 
            'student', 'student_no', 'points', 'percentage'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Detaylı ders serializer (LO'lar dahil)"""
    learning_outcomes = LearningOutcomeSerializer(many=True, read_only=True)
    assessments = AssessmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'semester', 'department', 
            'instructor', 'learning_outcomes', 'assessments'
        ]
