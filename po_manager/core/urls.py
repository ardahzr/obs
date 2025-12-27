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
    # Auth endpoints
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/me/', views.me_view, name='me'),
    # Notification endpoints
    path('notifications/', views.get_notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    # Course approval endpoints
    path('courses/<int:course_id>/submit-for-approval/', views.submit_course_for_approval, name='submit_for_approval'),
    path('courses/<int:course_id>/approve/', views.approve_course, name='approve_course'),
    path('courses/<int:course_id>/reject/', views.reject_course, name='reject_course'),
    path('pending-approvals/', views.get_pending_approvals, name='pending_approvals'),
]
