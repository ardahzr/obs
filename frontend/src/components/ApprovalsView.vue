<template>
  <div class="approvals-container">
    <!-- Modern Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            <polyline points="9 12 11 14 15 10"></polyline>
          </svg>
        </div>
        <div class="header-text">
          <h1>Admin Panel</h1>
          <p class="subtitle">Manage course approvals and instructor accounts</p>
        </div>
      </div>
    </div>

    <!-- Modern Tab Navigation -->
    <div class="admin-tabs">
      <button 
        :class="['tab-btn', { active: activeTab === 'approvals' }]"
        @click="activeTab = 'approvals'"
      >
        <div class="tab-icon approvals-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </div>
        <span class="tab-text">Pending Approvals</span>
        <span v-if="pendingCourses.length > 0" class="tab-badge">{{ pendingCourses.length }}</span>
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'instructors' }]"
        @click="activeTab = 'instructors'"
      >
        <div class="tab-icon instructors-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
        </div>
        <span class="tab-text">Instructor Management</span>
      </button>
    </div>

    <!-- Approvals Tab Content -->
    <div v-if="activeTab === 'approvals'" class="tab-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading pending approvals...</p>
      </div>

      <div v-else-if="pendingCourses.length === 0" class="empty-state">
        <div class="empty-icon-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
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
          <span class="status-badge pending">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            Pending
          </span>
        </div>

        <div class="card-body">
          <div class="info-row">
            <span class="label">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              Faculty Member
            </span>
            <span class="value">{{ course.instructor_name || 'Not specified' }}</span>
          </div>
          <div class="info-row">
            <span class="label">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              Department
            </span>
            <span class="value">{{ course.department }}</span>
          </div>
          <div class="info-row">
            <span class="label">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              Semester
            </span>
            <span class="value">{{ course.semester || 'Not specified' }}</span>
          </div>
          <div class="info-row">
            <span class="label">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 2L11 13"></path>
                <path d="M22 2l-7 20-4-9-9-4 20-7z"></path>
              </svg>
              Submitted
            </span>
            <span class="value">{{ formatDate(course.submitted_at) }}</span>
          </div>
        </div>

        <div class="card-actions">
          <button @click="openApproveModal(course)" class="approve-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Approve
          </button>
          <button @click="openRejectModal(course)" class="reject-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            Reject
          </button>
        </div>
      </div>
      </div>
    </div>

    <!-- Instructor Management Tab Content -->
    <div v-if="activeTab === 'instructors'" class="tab-content">
      <div class="instructor-section">
        <div class="section-card">
          <div class="section-header">
            <div class="section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <line x1="20" y1="8" x2="20" y2="14"></line>
                <line x1="23" y1="11" x2="17" y2="11"></line>
              </svg>
            </div>
            <div class="section-text">
              <h2>Create New Instructor Account</h2>
              <p>Create a new instructor account. A random password will be generated and sent to the instructor's email.</p>
            </div>
          </div>

          <form @submit.prevent="createInstructor" class="instructor-form">
            <div class="form-row">
              <div class="form-group">
                <label>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  Username <span class="required">*</span>
                </label>
                <input 
                  v-model="newInstructor.username" 
                  type="text" 
                  placeholder="e.g. johndoe"
                  required
                />
              </div>
              <div class="form-group">
                <label>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                  Email <span class="required">*</span>
                </label>
                <input 
                  v-model="newInstructor.email" 
                  type="email" 
                  placeholder="e.g. john.doe@university.edu"
                  required
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  First Name <span class="required">*</span>
                </label>
                <input 
                  v-model="newInstructor.first_name" 
                  type="text" 
                  placeholder="e.g. John"
                  required
                />
              </div>
              <div class="form-group">
                <label>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  Last Name <span class="required">*</span>
                </label>
                <input 
                  v-model="newInstructor.last_name" 
                  type="text" 
                  placeholder="e.g. Doe"
                  required
                />
              </div>
            </div>

            <div class="form-row single">
              <div class="form-group">
                <label>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                  </svg>
                  Department
                </label>
                <input 
                  v-model="newInstructor.department" 
                  type="text" 
                placeholder="e.g. Computer Science"
              />
              </div>
            </div>

            <div v-if="instructorError" class="error-message">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
              {{ instructorError }}
            </div>

            <div v-if="instructorSuccess" class="success-message">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              {{ instructorSuccess }}
            </div>

            <button type="submit" class="submit-btn" :disabled="creatingInstructor">
              <span v-if="creatingInstructor" class="btn-spinner"></span>
              <template v-else>
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="8.5" cy="7" r="4"></circle>
                  <line x1="20" y1="8" x2="20" y2="14"></line>
                  <line x1="23" y1="11" x2="17" y2="11"></line>
                </svg>
                Create Instructor Account
              </template>
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Approve Modal -->
    <div v-if="showApproveModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <div class="modal-header approve">
          <div class="modal-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <h3>Approve Course</h3>
        </div>
        <div class="modal-body">
          <p class="course-preview"><strong>{{ selectedCourse?.code }}</strong> - {{ selectedCourse?.name }}</p>
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
          <div class="modal-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </div>
          <h3>Reject Course</h3>
        </div>
        <div class="modal-body">
          <p class="course-preview"><strong>{{ selectedCourse?.code }}</strong> - {{ selectedCourse?.name }}</p>
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

// Tab state
const activeTab = ref('approvals')

// Approvals state
const pendingCourses = ref([])
const loading = ref(true)
const actionLoading = ref(false)

const showApproveModal = ref(false)
const showRejectModal = ref(false)
const selectedCourse = ref(null)
const approveMessage = ref('')
const rejectReason = ref('')
const rejectError = ref('')

// Instructor management state
const newInstructor = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  department: ''
})
const creatingInstructor = ref(false)
const instructorError = ref('')
const instructorSuccess = ref('')

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

// Create instructor function
const createInstructor = async () => {
  instructorError.value = ''
  instructorSuccess.value = ''
  
  const token = localStorage.getItem('token')
  if (!token) return

  creatingInstructor.value = true
  try {
    const response = await api.createInstructor(token, newInstructor.value)
    if (response.data.success) {
      instructorSuccess.value = `Instructor account created successfully! Login credentials have been sent to ${newInstructor.value.email}`
      // Reset form
      newInstructor.value = {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        department: ''
      }
    }
  } catch (err) {
    console.error('Instructor creation failed:', err)
    instructorError.value = err.response?.data?.error || 'Failed to create instructor account'
  } finally {
    creatingInstructor.value = false
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
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* Page Header */
.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 10px 30px -10px rgba(139, 92, 246, 0.5);
}

.header-text h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.header-text .subtitle {
  color: #6b7280;
  font-size: 15px;
  margin: 0;
}

/* Tab Navigation */
.admin-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  background: white;
  padding: 8px;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  width: fit-content;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.tab-btn.active {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.tab-btn.active .tab-icon {
  background: rgba(255, 255, 255, 0.2);
}

.tab-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  transition: all 0.2s ease;
}

.tab-btn.active .tab-icon {
  background: rgba(255, 255, 255, 0.2);
}

.tab-badge {
  background: #ef4444;
  color: white;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.tab-content {
  min-height: 400px;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background: white;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #e5e7eb;
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon-wrapper {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.5);
}

.empty-state h3 {
  font-size: 20px;
  color: #1f2937;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.empty-state p {
  color: #6b7280;
  margin: 0;
  font-size: 15px;
}

/* Approval Cards Grid */
.approvals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.approval-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.approval-card:hover {
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
}

.course-code {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 8px;
  margin-bottom: 10px;
  backdrop-filter: blur(4px);
}

.course-name {
  color: white;
  font-size: 20px;
  margin: 0;
  font-weight: 700;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.pending {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(4px);
}

.card-body {
  padding: 24px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #6b7280;
  font-size: 14px;
}

.info-row .label svg {
  width: 18px;
  height: 18px;
  color: #9ca3af;
}

.info-row .value {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.card-actions {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f3f4f6;
  background: #fafafa;
}

.approve-btn,
.reject-btn {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.approve-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.approve-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.reject-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.reject-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
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
  backdrop-filter: blur(8px);
}

.modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 480px;
  overflow: hidden;
  animation: modalIn 0.3s ease-out;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px;
  color: white;
}

.modal-header.approve {
  background: linear-gradient(135deg, #10b981, #059669);
}

.modal-header.reject {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.modal-icon {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-icon svg {
  width: 24px;
  height: 24px;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}

.modal-body {
  padding: 24px;
}

.modal-body > p {
  margin: 0 0 20px 0;
  color: #374151;
  font-size: 15px;
  line-height: 1.6;
}

.modal-body > p strong {
  color: #1f2937;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.required {
  color: #ef4444;
}

.form-group textarea {
  padding: 14px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
  transition: all 0.2s ease;
}

.form-group textarea:focus {
  outline: none;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1);
}

.error-text {
  color: #ef4444;
  font-size: 13px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f3f4f6;
  background: #fafafa;
}

.cancel-btn {
  flex: 1;
  padding: 14px 20px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
}

.cancel-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.confirm-approve-btn,
.confirm-reject-btn {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.confirm-approve-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.confirm-approve-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.confirm-reject-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.confirm-reject-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
}

.confirm-approve-btn:disabled,
.confirm-reject-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Instructor Management Section */
.section-card {
  background: white;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  max-width: 700px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-bottom: 1px solid #f3f4f6;
}

.section-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 20px -8px rgba(59, 130, 246, 0.5);
}

.section-text h2 {
  font-size: 20px;
  color: #1f2937;
  margin: 0 0 4px 0;
  font-weight: 700;
}

.section-text p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.instructor-form {
  padding: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-row.single {
  grid-template-columns: 1fr;
}

.instructor-form .form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.instructor-form label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.instructor-form label svg {
  width: 16px;
  height: 16px;
  color: #9ca3af;
}

.instructor-form input {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.instructor-form input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.error-message {
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-weight: 500;
}

.success-message {
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border: 1px solid #bbf7d0;
  color: #16a34a;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-weight: 500;
}

.submit-btn {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .approvals-container {
    padding: 20px;
  }
  
  .approvals-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .admin-tabs {
    flex-direction: column;
    width: 100%;
  }
  
  .tab-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
