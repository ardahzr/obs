"""
Email utility functions for sending notifications
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_notification_email(notification):
    """
    Bildirim oluşturulduğunda email gönder.
    
    Args:
        notification: Notification model instance
    """
    recipient = notification.recipient
    
    # Kullanıcının email adresi yoksa gönderme
    if not recipient.email:
        return False
    
    # Email konusu
    subject_map = {
        'approval_request': f'🔔 Yeni Onay İsteği: {notification.course.code}',
        'approved': f'✅ Ders Onaylandı: {notification.course.code}',
        'rejected': f'❌ Ders Reddedildi: {notification.course.code}',
    }
    subject = subject_map.get(notification.notification_type, 'PO Manager Bildirimi')
    
    # Email içeriği (HTML)
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
            .footer {{ background: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px; }}
            .badge {{ display: inline-block; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
            .badge-pending {{ background: #fef3c7; color: #d97706; }}
            .badge-approved {{ background: #d1fae5; color: #059669; }}
            .badge-rejected {{ background: #fee2e2; color: #dc2626; }}
            .course-code {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">📚 PO Manager</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Program Outcome Management System</p>
            </div>
            <div class="content">
                <p>Merhaba <strong>{recipient.get_full_name() or recipient.username}</strong>,</p>
                
                <div class="course-code">{notification.course.code} - {notification.course.name}</div>
                
                <p>{notification.message}</p>
                
                <p style="margin-top: 20px;">
                    <span class="badge badge-{notification.notification_type.replace('approval_request', 'pending')}">
                        {notification.get_notification_type_display()}
                    </span>
                </p>
                
                <p style="margin-top: 20px; color: #6b7280; font-size: 14px;">
                    Gönderen: {notification.sender.get_full_name() or notification.sender.username}
                </p>
            </div>
            <div class="footer">
                <p>Bu email PO Manager sistemi tarafından otomatik olarak gönderilmiştir.</p>
                <p>© 2025 PO Manager - Program Outcome Management System</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text versiyonu
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email gönderme hatası: {e}")
        return False


def send_bulk_notification_emails(notifications):
    """
    Birden fazla bildirim için toplu email gönder.
    
    Args:
        notifications: List of Notification instances
    """
    success_count = 0
    for notification in notifications:
        if send_notification_email(notification):
            success_count += 1
    return success_count
