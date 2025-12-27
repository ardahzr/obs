<template>
  <div class="notification-wrapper">
    <button class="notification-btn" @click="toggleDropdown">
      <span class="bell-icon">🔔</span>
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
    </button>

    <div v-if="showDropdown" class="notification-dropdown">
      <div class="dropdown-header">
        <h4>Notifications</h4>
        <button v-if="notifications.length > 0" @click="markAllRead" class="mark-all-btn">
          Mark All as Read
        </button>
      </div>

      <div class="notification-list">
        <div v-if="loading" class="loading-state">
          <span class="loading-spinner"></span>
          Loading...
        </div>

        <div v-else-if="notifications.length === 0" class="empty-state">
          <span class="empty-icon">📭</span>
          <p>No notifications yet</p>
        </div>

        <div
          v-else
          v-for="notification in notifications"
          :key="notification.id"
          :class="['notification-item', { unread: !notification.is_read }]"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-icon">
            <span v-if="notification.notification_type === 'approval_request'">📋</span>
            <span v-else-if="notification.notification_type === 'approved'">✅</span>
            <span v-else-if="notification.notification_type === 'rejected'">❌</span>
          </div>
          <div class="notification-content">
            <div class="notification-title">
              {{ notification.notification_type_display }}
              <span class="course-code">{{ notification.course_code }}</span>
            </div>
            <p class="notification-message">{{ notification.message }}</p>
            <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
          </div>
          <div v-if="!notification.is_read" class="unread-dot"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineEmits } from 'vue'
import api from '../services/api'

const emit = defineEmits(['view-approvals'])

const showDropdown = ref(false)
const notifications = ref([])
const unreadCount = ref(0)
const loading = ref(false)

let pollInterval = null

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
  if (showDropdown.value) {
    fetchNotifications()
  }
}

const fetchNotifications = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  loading.value = true
  try {
    const response = await api.getNotifications(token)
    if (response.data.success) {
      notifications.value = response.data.notifications
      unreadCount.value = response.data.unread_count
    }
  } catch (err) {
    console.error('Bildirimler yüklenemedi:', err)
  } finally {
    loading.value = false
  }
}

const markAllRead = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    await api.markAllNotificationsRead(token)
    notifications.value = notifications.value.map(n => ({ ...n, is_read: true }))
    unreadCount.value = 0
  } catch (err) {
    console.error('İşaretleme hatası:', err)
  }
}

const handleNotificationClick = async (notification) => {
  const token = localStorage.getItem('token')
  
  // Okundu olarak işaretle
  if (!notification.is_read && token) {
    try {
      await api.markNotificationRead(token, notification.id)
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (err) {
      console.error('İşaretleme hatası:', err)
    }
  }

  // Onay isteği ise onay sayfasına yönlendir
  if (notification.notification_type === 'approval_request') {
    emit('view-approvals')
    showDropdown.value = false
  }
}

const formatTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`
  
  return date.toLocaleDateString('en-US')
}

// Click outside to close
const handleClickOutside = (e) => {
  if (!e.target.closest('.notification-wrapper')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  fetchNotifications()
  // Her 30 saniyede bir yeni bildirimleri kontrol et
  pollInterval = setInterval(fetchNotifications, 30000)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  document.removeEventListener('click', handleClickOutside)
})

// Dışarıdan erişim için
defineExpose({ fetchNotifications })
</script>

<style scoped>
.notification-wrapper {
  position: relative;
}

.notification-btn {
  position: relative;
  width: 40px;
  height: 40px;
  background: var(--bg-primary, #f3f4f6);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.notification-btn:hover {
  background: var(--primary-color, #3b82f6);
  border-color: var(--primary-color, #3b82f6);
}

.notification-btn:hover .bell-icon {
  filter: brightness(0) invert(1);
}

.bell-icon {
  font-size: 18px;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  width: 380px;
  max-height: 500px;
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.2);
  z-index: 1002;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-primary, #f9fafb);
}

.dropdown-header h4 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary, #1f2937);
}

.mark-all-btn {
  background: none;
  border: none;
  color: var(--primary-color, #3b82f6);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.mark-all-btn:hover {
  background: rgba(59, 130, 246, 0.1);
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-secondary, #6b7280);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color, #e5e7eb);
  border-top-color: var(--primary-color, #3b82f6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.notification-item:hover {
  background: var(--bg-primary, #f9fafb);
}

.notification-item.unread {
  background: rgba(59, 130, 246, 0.05);
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary, #1f2937);
  margin-bottom: 4px;
}

.course-code {
  background: linear-gradient(135deg, var(--primary-color, #3b82f6), var(--secondary-color, #8b5cf6));
  color: white;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
}

.notification-message {
  font-size: 13px;
  color: var(--text-secondary, #6b7280);
  margin: 0 0 6px 0;
  line-height: 1.4;
}

.notification-time {
  font-size: 11px;
  color: var(--text-secondary, #9ca3af);
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: var(--primary-color, #3b82f6);
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
}
</style>
