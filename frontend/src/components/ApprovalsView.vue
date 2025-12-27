<template>
  <div class="approvals-container">
    <div class="page-header">
      <h1>📋 Pending Approvals</h1>
      <p class="subtitle">Course approval requests from faculty members</p>
    </div>

    <div v-if="loading" class="loading-state">
      <span class="loading-spinner"></span>
      <p>Loading...</p>
    </div>

    <div v-else-if="pendingCourses.length === 0" class="empty-state">
      <span class="empty-icon">✅</span>
      <h3>No Pending Approvals</h3>
      <p>There are no courses waiting for approval.</p>
    </div>

    <div v-else class="approvals-grid">
      <div v-for="course in pendingCourses" :key="course.id" class="approval-card">
        <div class="card-header">
          <div class="course-info">
            <span class="course-code">{{ course.code }}</span>
            <h3 class="course-name">{{ course.name }}</h3>
          </div>
          <span class="status-badge pending">Pending Approval</span>
        </div>

        <div class="card-body">
          <div class="info-row">
            <span class="label">👨‍🏫 Faculty Member:</span>
            <span class="value">{{ course.instructor_name || 'Not specified' }}</span>
          </div>
          <div class="info-row">
            <span class="label">🏢 Department:</span>
            <span class="value">{{ course.department }}</span>
          </div>
          <div class="info-row">
            <span class="label">📅 Semester:</span>
            <span class="value">{{ course.semester || 'Not specified' }}</span>
          </div>
          <div class="info-row">
            <span class="label">📤 Submission:</span>
            <span class="value">{{ formatDate(course.submitted_at) }}</span>
          </div>
        </div>

        <div class="card-actions">
          <button @click="openApproveModal(course)" class="approve-btn">
            <span>✅</span> Approve
          </button>
          <button @click="openRejectModal(course)" class="reject-btn">
            <span>❌</span> Reject
          </button>
        </div>
      </div>
    </div>

    <!-- Approve Modal -->
    <div v-if="showApproveModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <div class="modal-header approve">
          <span class="modal-icon">✅</span>
          <h3>Approve Course</h3>
        </div>
        <div class="modal-body">
          <p><strong>{{ selectedCourse?.code }}</strong> - {{ selectedCourse?.name }}</p>
          <div class="form-group">
            <label>Message (Optional)</label>
            <textarea 
              v-model="approveMessage" 
              placeholder="You can write a message to the instructor..."
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="closeModals" class="cancel-btn">Cancel</button>
          <button @click="confirmApprove" class="confirm-approve-btn" :disabled="actionLoading">
            <span v-if="actionLoading" class="btn-spinner"></span>
            <span v-else>Approve</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <div class="modal-header reject">
          <span class="modal-icon">❌</span>
          <h3>Reject Course</h3>
        </div>
        <div class="modal-body">
          <p><strong>{{ selectedCourse?.code }}</strong> - {{ selectedCourse?.name }}</p>
          <div class="form-group">
            <label>Rejection Reason <span class="required">*</span></label>
            <textarea 
              v-model="rejectReason" 
              placeholder="Please explain the reason for rejection..."
              rows="4"
              required
            ></textarea>
            <span v-if="rejectError" class="error-text">{{ rejectError }}</span>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="closeModals" class="cancel-btn">Cancel</button>
          <button @click="confirmReject" class="confirm-reject-btn" :disabled="actionLoading">
            <span v-if="actionLoading" class="btn-spinner"></span>
            <span v-else>Reject</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const pendingCourses = ref([])
const loading = ref(true)
const actionLoading = ref(false)

const showApproveModal = ref(false)
const showRejectModal = ref(false)
const selectedCourse = ref(null)
const approveMessage = ref('')
const rejectReason = ref('')
const rejectError = ref('')

const fetchPendingApprovals = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  loading.value = true
  try {
    const response = await api.getPendingApprovals(token)
    if (response.data.success) {
      pendingCourses.value = response.data.pending_courses
    }
  } catch (err) {
    console.error('Onaylar yüklenemedi:', err)
  } finally {
    loading.value = false
  }
}

const openApproveModal = (course) => {
  selectedCourse.value = course
  approveMessage.value = ''
  showApproveModal.value = true
}

const openRejectModal = (course) => {
  selectedCourse.value = course
  rejectReason.value = ''
  rejectError.value = ''
  showRejectModal.value = true
}

const closeModals = () => {
  showApproveModal.value = false
  showRejectModal.value = false
  selectedCourse.value = null
}

const confirmApprove = async () => {
  const token = localStorage.getItem('token')
  if (!token || !selectedCourse.value) return

  actionLoading.value = true
  try {
    const response = await api.approveCourse(token, selectedCourse.value.id, approveMessage.value)
    if (response.data.success) {
      // Listeden kaldır
      pendingCourses.value = pendingCourses.value.filter(c => c.id !== selectedCourse.value.id)
      closeModals()
    }
  } catch (err) {
    console.error('Onaylama hatası:', err)
  } finally {
    actionLoading.value = false
  }
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    rejectError.value = 'Red sebebi zorunludur'
    return
  }

  const token = localStorage.getItem('token')
  if (!token || !selectedCourse.value) return

  actionLoading.value = true
  try {
    const response = await api.rejectCourse(token, selectedCourse.value.id, rejectReason.value)
    if (response.data.success) {
      pendingCourses.value = pendingCourses.value.filter(c => c.id !== selectedCourse.value.id)
      closeModals()
    }
  } catch (err) {
    console.error('Reddetme hatası:', err)
  } finally {
    actionLoading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Belirtilmemiş'
  return new Date(dateString).toLocaleString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchPendingApprovals()
})
</script>

<style scoped>
.approvals-container {
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: var(--text-primary, #1f2937);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-secondary, #6b7280);
  font-size: 15px;
  margin: 0;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color, #e5e7eb);
  border-top-color: var(--primary-color, #3b82f6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  color: var(--text-primary, #1f2937);
  margin: 0 0 8px 0;
}

.empty-state p {
  color: var(--text-secondary, #6b7280);
  margin: 0;
}

.approvals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
}

.approval-card {
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
}

.approval-card:hover {
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  background: linear-gradient(135deg, var(--primary-color, #3b82f6), var(--secondary-color, #8b5cf6));
}

.course-code {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.course-name {
  color: white;
  font-size: 18px;
  margin: 0;
  font-weight: 600;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.pending {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.card-body {
  padding: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: var(--text-secondary, #6b7280);
  font-size: 14px;
}

.info-row .value {
  font-weight: 500;
  color: var(--text-primary, #1f2937);
  font-size: 14px;
}

.card-actions {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-primary, #f9fafb);
}

.approve-btn,
.reject-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.approve-btn {
  background: #10b981;
  color: white;
}

.approve-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.reject-btn {
  background: #ef4444;
  color: white;
}

.reject-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 480px;
  overflow: hidden;
  animation: modalIn 0.2s ease-out;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  color: white;
}

.modal-header.approve {
  background: linear-gradient(135deg, #10b981, #059669);
}

.modal-header.reject {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.modal-icon {
  font-size: 24px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.modal-body {
  padding: 24px;
}

.modal-body > p {
  margin: 0 0 20px 0;
  color: var(--text-primary, #1f2937);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #1f2937);
}

.required {
  color: #ef4444;
}

.form-group textarea {
  padding: 12px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 10px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.error-text {
  color: #ef4444;
  font-size: 13px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-primary, #f9fafb);
}

.cancel-btn {
  flex: 1;
  padding: 12px 20px;
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--bg-primary, #f9fafb);
}

.confirm-approve-btn,
.confirm-reject-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.confirm-approve-btn {
  background: #10b981;
}

.confirm-approve-btn:hover:not(:disabled) {
  background: #059669;
}

.confirm-reject-btn {
  background: #ef4444;
}

.confirm-reject-btn:hover:not(:disabled) {
  background: #dc2626;
}

.confirm-approve-btn:disabled,
.confirm-reject-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
