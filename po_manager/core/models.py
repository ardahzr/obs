from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    """Kullanıcı profili - Admin veya Instructor"""
    USER_TYPES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='instructor')
    department = models.CharField(max_length=100, default='CSE')
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_instructor(self):
        return self.user_type == 'instructor'

class Course(models.Model):
    """Ders modeli - CSE311, CSE321 gibi dersler"""
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=200)
    semester = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, default='CSE')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['code']


class ProgramOutcome(models.Model):
    """Program Outcome (PO) - PO1, PO2, ... PO11"""
    code = models.CharField(max_length=8, unique=True)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.code}: {self.description[:50]}"
    
    class Meta:
        ordering = ['code']


class LearningOutcome(models.Model):
    """Learning Outcome (LO) - her ders için öğrenme çıktıları"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_outcomes')
    code = models.CharField(max_length=16)
    description = models.TextField()
    weight = models.FloatField(default=1.0, help_text="Ders içindeki ağırlık")
    
    def __str__(self):
        return f"{self.course.code} - {self.code}: {self.description[:30]}"
    
    class Meta:
        ordering = ['course', 'code']
        unique_together = ['course', 'code']


class LoToPoMapping(models.Model):
    """LO'dan PO'ya mapping ve katkı ağırlığı"""
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE, related_name='po_mappings')
    program_outcome = models.ForeignKey(ProgramOutcome, on_delete=models.CASCADE, related_name='lo_mappings')
    contribution_weight = models.FloatField(default=1.0, help_text="LO'nun PO'ya katkı ağırlığı (0-5 arası)")
    
    def __str__(self):
        return f"{self.learning_outcome.code} → {self.program_outcome.code} (weight: {self.contribution_weight})"
    
    class Meta:
        unique_together = ['learning_outcome', 'program_outcome']
        verbose_name = "LO to PO Mapping"
        verbose_name_plural = "LO to PO Mappings"


class Student(models.Model):
    """Öğrenci modeli"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_no = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, default='CSE')
    
    def __str__(self):
        return f"{self.student_no} - {self.user.get_full_name()}"
    
    class Meta:
        ordering = ['student_no']


class Assessment(models.Model):
    """Değerlendirme - Quiz, Midterm, Final, vb."""
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('project', 'Project'),
        ('homework', 'Homework'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=128)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='quiz')
    total_points = models.FloatField()
    date = models.DateField(blank=True, null=True)
    learning_outcomes = models.ManyToManyField(LearningOutcome, related_name='assessments', blank=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.name} ({self.total_points} pts)"
    
    class Meta:
        ordering = ['course', 'date']


class AssessmentToLoMapping(models.Model):
    """Assessment'tan LO'ya mapping - örn: Midterm %60 → LO1"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='lo_mappings')
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE, related_name='assessment_mappings')
    contribution_weight = models.FloatField(default=0.0, help_text="Assessment'ın LO'ya katkı yüzdesi (0-100)")
    
    def __str__(self):
        return f"{self.assessment.name} → {self.learning_outcome.code} ({self.contribution_weight}%)"
    
    class Meta:
        unique_together = ['assessment', 'learning_outcome']
        verbose_name = "Assessment to LO Mapping"
        verbose_name_plural = "Assessment to LO Mappings"


class Grade(models.Model):
    """Öğrenci notları"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    points = models.FloatField()
    
    def __str__(self):
        return f"{self.student.student_no} - {self.assessment.name}: {self.points}/{self.assessment.total_points}"
    
    class Meta:
        unique_together = ['assessment', 'student']
        ordering = ['assessment', 'student']
    
    @property
    def percentage(self):
        """Yüzde hesapla"""
        if self.assessment.total_points > 0:
            return (self.points / self.assessment.total_points) * 100
        return 0


class Enrollment(models.Model):
    """Öğrenci-Ders kayıt ilişkisi"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.student_no} - {self.course.code}"
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['course', 'student']
