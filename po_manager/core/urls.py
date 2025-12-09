from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'program-outcomes', views.ProgramOutcomeViewSet)
router.register(r'learning-outcomes', views.LearningOutcomeViewSet)
router.register(r'mappings', views.LoToPoMappingViewSet)
router.register(r'assessment-to-lo-mappings', views.AssessmentToLoMappingViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'grades', views.GradeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', views.chat_view, name='chat'),
]
