<template>
  <div class="students-view">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
        </div>
        <div class="header-text">
          <h1>Students</h1>
          <p>Manage student records and track program outcome scores</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="course-selector">
          <label>Filter by Course</label>
          <select v-model="selectedCourseId" @change="loadStudents" class="select-input">
            <option :value="null">All Courses</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.code }} - {{ course.name }}
            </option>
          </select>
        </div>
        <button @click="showImportModal = true" class="btn-import">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Import Excel
        </button>
        <button @click="showAddModal = true" class="btn-add">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Add Student
        </button>
      </div>
    </div>

    <!-- Stats Bar -->
    <div class="stats-bar" v-if="students.length > 0">
      <div class="stat-item">
        <div class="stat-icon students-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ students.length }}</span>
          <span class="stat-label">Total Students</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="students.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
          <circle cx="9" cy="7" r="4"></circle>
          <line x1="19" y1="8" x2="19" y2="14"></line>
          <line x1="22" y1="11" x2="16" y2="11"></line>
        </svg>
      </div>
      <h3>{{ selectedCourseId ? 'No Students in This Course' : 'No Students Yet' }}</h3>
      <p>{{ selectedCourseId ? 'There are no students enrolled in the selected course' : 'Get started by adding students or importing from Excel' }}</p>
      <div class="empty-actions">
        <button @click="showImportModal = true" class="btn-import">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Import from Excel
        </button>
        <button @click="showAddModal = true" class="btn-add">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Add Student
        </button>
      </div>
    </div>

    <!-- Students Grid -->
    <div v-else class="students-grid">
      <div v-for="(student, index) in students" :key="student.id" class="student-card">
        <div class="card-header">
          <div class="student-avatar" :style="{ background: getAvatarColor(index) }">
            {{ getInitials(student.user.first_name, student.user.last_name) }}
          </div>
          <div class="student-info">
            <h3>{{ student.user.first_name }} {{ student.user.last_name }}</h3>
            <div class="student-meta">
              <span class="student-id">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                {{ student.student_no }}
              </span>
            </div>
          </div>
          <button @click="loadStudentScores(student.id)" class="btn-scores" :class="{ active: selectedStudentId === student.id }">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
            {{ selectedStudentId === student.id ? 'Hide Scores' : 'View Scores' }}
          </button>
        </div>
        
        <!-- PO Scores Section -->
        <div v-if="selectedStudentId === student.id && poScores.length > 0" class="po-scores-section">
          <div class="scores-header">
            <h4>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              Program Outcome Scores
            </h4>
          </div>
          <div class="scores-grid">
            <div v-for="score in poScores" :key="score.po_code" class="score-card">
              <div class="score-info">
                <span class="po-badge">{{ score.po_code }}</span>
                <span class="score-percentage" :style="{ color: getScoreColor(score.score) }">
                  {{ score.score.toFixed(1) }}%
                </span>
              </div>
              <div class="score-bar-container">
                <div class="score-bar-bg">
                  <div class="score-bar-fill" :style="{ width: score.score + '%', background: getScoreGradient(score.score) }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Student Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <div class="modal-title">
            <div class="modal-icon add-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <line x1="20" y1="8" x2="20" y2="14"></line>
                <line x1="23" y1="11" x2="17" y2="11"></line>
              </svg>
            </div>
            <h3>Add New Student</h3>
          </div>
          <button @click="showAddModal = false" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="addStudent" class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>First Name</label>
              <input v-model="newStudent.first_name" type="text" placeholder="John" required class="form-input">
            </div>
            <div class="form-group">
              <label>Last Name</label>
              <input v-model="newStudent.last_name" type="text" placeholder="Doe" required class="form-input">
            </div>
          </div>
          <div class="form-group">
            <label>Username</label>
            <input v-model="newStudent.username" type="text" placeholder="johndoe" required class="form-input">
          </div>
          <div class="form-group">
            <label>Student Number</label>
            <input v-model="newStudent.student_number" type="text" placeholder="e.g., 20230123" required class="form-input">
          </div>
          <div class="modal-footer">
            <button type="button" @click="showAddModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">Create Student</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Import Excel Modal -->
    <div v-if="showImportModal" class="modal-overlay" @click="showImportModal = false">
      <div class="modal-content modal-lg" @click.stop>
        <div class="modal-header">
          <div class="modal-title">
            <div class="modal-icon import-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
            </div>
            <h3>Import from OBS Excel</h3>
          </div>
          <button @click="showImportModal = false" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="handleImport" class="modal-body">
          <div class="upload-zone">
            <input type="file" accept=".xlsx,.xls" @change="onFileChange" required id="excel-file" class="file-input">
            <label for="excel-file" class="upload-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              <span class="upload-text">{{ importData.file ? importData.file.name : 'Click to select Excel file' }}</span>
              <span class="upload-hint">Supports .xlsx and .xls files</span>
            </label>
          </div>

          <div class="form-group">
            <label>Target Course</label>
            <select v-model="importData.courseId" class="select-input">
              <option :value="null">Create New Course</option>
              <option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.code }} - {{ course.name }}
              </option>
            </select>
          </div>

          <div v-if="!importData.courseId" class="new-course-section">
            <div class="section-label">New Course Details</div>
            <div class="form-row">
              <div class="form-group">
                <label>Course Code</label>
                <input v-model="importData.courseCode" type="text" placeholder="Auto-detect from Excel" class="form-input">
              </div>
              <div class="form-group">
                <label>Course Name</label>
                <input v-model="importData.courseName" type="text" placeholder="e.g., Operating Systems" class="form-input">
              </div>
            </div>
          </div>

          <div v-if="importResult" class="import-result" :class="importResult.success ? 'success' : 'error'">
            <div v-if="importResult.success" class="result-content">
              <div class="result-icon success">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
              </div>
              <div class="result-details">
                <strong>Import Successful!</strong>
                <div class="result-stats">
                  <span>Course: {{ importResult.course }} {{ importResult.course_created ? '(new)' : '' }}</span>
                  <span>Students: {{ importResult.students_created }} created</span>
                  <span>Assessments: {{ importResult.assessments_created || 0 }}</span>
                  <span>Grades: {{ importResult.grades_created || 0 }}</span>
                </div>
              </div>
            </div>
            <div v-else class="result-content">
              <div class="result-icon error">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
              </div>
              <div class="result-details">
                <strong>Import Failed</strong>
                <span>{{ importResult.message }}</span>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" @click="showImportModal = false" class="btn-cancel">Close</button>
            <button type="submit" class="btn-submit" :disabled="importing">
              <span v-if="importing" class="spinner"></span>
              {{ importing ? 'Importing...' : 'Import Data' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const students = ref([])
const courses = ref([])
const selectedCourseId = ref(null)
const poScores = ref([])
const selectedStudentId = ref(null)
const showAddModal = ref(false)
const showImportModal = ref(false)
const importing = ref(false)
const importResult = ref(null)
const importData = ref({
  file: null,
  courseId: null,
  courseCode: '',
  courseName: ''
})
const newStudent = ref({
  first_name: '',
  last_name: '',
  username: '',
  student_number: ''
})

async function loadCourses() {
  try {
    const response = await api.getCourses()
    courses.value = response.data
  } catch (error) {
    console.error('Error loading courses:', error)
  }
}

async function loadStudents() {
  try {
    let url = 'students/'
    if (selectedCourseId.value) {
      url += `?course=${selectedCourseId.value}`
    }
    const response = await api.get(url)
    students.value = response.data
  } catch (error) {
    console.error('Error loading students:', error)
  }
}

async function loadStudentScores(studentId) {
  if (selectedStudentId.value === studentId) {
    selectedStudentId.value = null
    poScores.value = []
    return
  }

  try {
    const response = await api.getStudentPOScores(studentId)
    poScores.value = response.data.po_scores
    selectedStudentId.value = studentId
  } catch (error) {
    console.error('Error loading scores:', error)
    alert('Failed to load student scores')
  }
}

async function addStudent() {
  try {
    await api.createStudent(newStudent.value)
    showAddModal.value = false
    newStudent.value = { first_name: '', last_name: '', username: '', student_number: '' }
    await loadStudents()
  } catch (error) {
    console.error('Error adding student:', error)
    alert('Failed to add student')
  }
}

function onFileChange(e) {
  importData.value.file = e.target.files[0]
}

async function handleImport() {
  if (!importData.value.file) {
    alert('Lütfen bir Excel dosyası seçin')
    return
  }
  importing.value = true
  importResult.value = null
  try {
    const res = await api.importObsExcel(
      importData.value.file,
      importData.value.courseId,
      importData.value.courseCode,
      importData.value.courseName
    )
    importResult.value = res.data
    await loadCourses()
    await loadStudents()
  } catch (err) {
    console.error('Import error:', err)
    importResult.value = { success: false, message: err.response?.data?.message || 'Import başarısız' }
  } finally {
    importing.value = false
  }
}

function getInitials(firstName, lastName) {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

const avatarColors = [
  'linear-gradient(135deg, #667eea, #764ba2)',
  'linear-gradient(135deg, #f093fb, #f5576c)',
  'linear-gradient(135deg, #4facfe, #00f2fe)',
  'linear-gradient(135deg, #43e97b, #38f9d7)',
  'linear-gradient(135deg, #fa709a, #fee140)',
  'linear-gradient(135deg, #a8edea, #fed6e3)',
  'linear-gradient(135deg, #6a11cb, #2575fc)',
  'linear-gradient(135deg, #ff9a9e, #fecfef)',
]

function getAvatarColor(index) {
  return avatarColors[index % avatarColors.length]
}

function getScoreClass(score) {
  if (score >= 80) return 'score-excellent'
  if (score >= 60) return 'score-good'
  if (score >= 40) return 'score-fair'
  return 'score-poor'
}

function getScoreColor(score) {
  const s = Math.max(0, Math.min(100, score))
  if (s >= 70) return '#10b981'
  if (s >= 50) return '#f59e0b'
  return '#ef4444'
}

function getScoreGradient(score) {
  const s = Math.max(0, Math.min(100, score))
  if (s >= 70) return 'linear-gradient(90deg, #10b981, #34d399)'
  if (s >= 50) return 'linear-gradient(90deg, #f59e0b, #fbbf24)'
  return 'linear-gradient(90deg, #ef4444, #f87171)'
}

onMounted(() => {
  loadCourses()
  loadStudents()
})
</script>

<style scoped>
.students-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 24px;
}

.header-content {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.header-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
}

.header-text h1 {
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.header-text p {
  font-size: 16px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.course-selector {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.course-selector label {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.select-input {
  padding: 12px 16px;
  padding-right: 40px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  min-width: 220px;
  background: white;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
}

.select-input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.btn-import {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  color: #475569;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-import:hover {
  border-color: #10b981;
  color: #10b981;
  background: #f0fdf4;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
}

.btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
}

/* Stats Bar */
.stats-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid #f1f5f9;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.students-icon {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #3b82f6;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #1e293b;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 40px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-radius: 24px;
  border: 2px dashed #e2e8f0;
}

.empty-icon {
  color: #94a3b8;
  margin-bottom: 24px;
}

.empty-state h3 {
  font-size: 24px;
  font-weight: 700;
  color: #334155;
  margin: 0 0 12px 0;
}

.empty-state p {
  font-size: 16px;
  color: #64748b;
  max-width: 400px;
  margin: 0 auto 28px;
  line-height: 1.6;
}

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Students Grid */
.students-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.student-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.student-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.student-avatar {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.student-info {
  flex: 1;
}

.student-info h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px 0;
}

.student-meta {
  display: flex;
  gap: 16px;
}

.student-id {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #64748b;
}

.btn-scores {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #f1f5f9;
  color: #475569;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-scores:hover {
  background: #e2e8f0;
}

.btn-scores.active {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

/* PO Scores Section */
.po-scores-section {
  padding: 0 24px 24px;
  border-top: 1px solid #f1f5f9;
  margin-top: 0;
  padding-top: 20px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.scores-header h4 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: #334155;
  margin: 0 0 20px 0;
}

.scores-header h4 svg {
  color: #10b981;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.score-card {
  background: #f8fafc;
  padding: 16px;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
}

.score-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.po-badge {
  background: #e0e7ff;
  color: #4338ca;
  padding: 4px 12px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
}

.score-percentage {
  font-size: 20px;
  font-weight: 800;
}

.score-bar-container {
  width: 100%;
}

.score-bar-bg {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 24px;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease;
}

.modal-lg {
  max-width: 600px;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 14px;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.add-icon {
  background: linear-gradient(135deg, #10b981, #059669);
}

.import-icon {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.btn-close {
  width: 40px;
  height: 40px;
  background: #f1f5f9;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #e2e8f0;
  color: #334155;
}

.modal-body {
  padding: 28px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #334155;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.2s;
  background: #fafafa;
}

.form-input:focus {
  outline: none;
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

/* Upload Zone */
.upload-zone {
  margin-bottom: 24px;
}

.file-input {
  display: none;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f8fafc;
  color: #64748b;
}

.upload-label:hover {
  border-color: #10b981;
  background: #f0fdf4;
  color: #10b981;
}

.upload-text {
  margin-top: 12px;
  font-weight: 600;
  font-size: 15px;
  color: #334155;
}

.upload-hint {
  margin-top: 4px;
  font-size: 13px;
  color: #94a3b8;
}

.new-course-section {
  background: #f8fafc;
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 20px;
}

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

/* Import Result */
.import-result {
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 20px;
}

.import-result.success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.import-result.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.result-content {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.result-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.result-icon.success {
  background: #dcfce7;
  color: #16a34a;
}

.result-icon.error {
  background: #fee2e2;
  color: #dc2626;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-details strong {
  font-size: 16px;
  color: #1e293b;
}

.result-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  font-size: 14px;
  color: #475569;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

.btn-cancel {
  padding: 14px 24px;
  background: #f1f5f9;
  color: #475569;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-submit {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .students-view {
    padding: 20px;
  }
  
  .page-header {
    flex-direction: column;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }
  
  .select-input {
    min-width: 100%;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .scores-grid {
    grid-template-columns: 1fr;
  }
}
</style>
