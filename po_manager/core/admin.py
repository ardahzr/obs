from django.contrib import admin
from .models import (
    Course, ProgramOutcome, LearningOutcome, 
    LoToPoMapping, Student, Assessment, AssessmentToLoMapping, Grade
)

# Register your models here.

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'semester', 'department', 'instructor']
    list_filter = ['department', 'semester']
    search_fields = ['code', 'name']


@admin.register(ProgramOutcome)
class ProgramOutcomeAdmin(admin.ModelAdmin):
    list_display = ['code', 'description']
    search_fields = ['code', 'description']


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ['code', 'course', 'description', 'weight']
    list_filter = ['course']
    search_fields = ['code', 'description']


@admin.register(LoToPoMapping)
class LoToPoMappingAdmin(admin.ModelAdmin):
    list_display = ['learning_outcome', 'program_outcome', 'contribution_weight']
    list_filter = ['program_outcome']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_no', 'user', 'department']
    search_fields = ['student_no', 'user__username', 'user__first_name', 'user__last_name']
    list_filter = ['department']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'assessment_type', 'total_points', 'date']
    list_filter = ['course', 'assessment_type']
    search_fields = ['name']
    filter_horizontal = ['learning_outcomes']


@admin.register(AssessmentToLoMapping)
class AssessmentToLoMappingAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'learning_outcome', 'contribution_weight']
    list_filter = ['assessment__course', 'learning_outcome__course']
    search_fields = ['assessment__name', 'learning_outcome__code']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'points', 'percentage']
    list_filter = ['assessment__course']
    search_fields = ['student__student_no', 'assessment__name']
