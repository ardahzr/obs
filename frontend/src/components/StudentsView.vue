<template>
  <div class="students-view">
    <div class="view-header">
      <div class="header-left">
        <h2>Students</h2>
        <p class="subtitle">Manage student records and track PO scores</p>
      </div>
      <div class="header-actions">
        <select v-model="selectedCourseId" @change="loadStudents" class="course-select">
          <option :value="null">All Courses</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.code }} - {{ course.name }}
          </option>
        </select>
        <button @click="showImportModal = true" class="btn-secondary">
          <span class="icon">📥</span> Import from Excel
        </button>
        <button @click="showAddModal = true" class="btn-primary">
          <span class="icon">+</span> Add New Student
        </button>
      </div>
    </div>

    <div v-if="students.length === 0" class="empty-state">
      <p>{{ selectedCourseId ? 'Bu derste kayıtlı öğrenci yok.' : 'Henüz öğrenci eklenmemiş.' }}</p>
    </div>

    <div class="students-list">
      <div v-for="student in students" :key="student.id" class="student-card">
        <div class="student-header">
          <div class="student-avatar">
            {{ getInitials(student.user.first_name, student.user.last_name) }}
          </div>
          <div class="student-info">
            <h3>{{ student.user.first_name }} {{ student.user.last_name }}</h3>
            <p class="student-number">{{ student.student_no }}</p>
          </div>
          <button @click="loadStudentScores(student.id)" class="btn-secondary btn-sm">
            View PO Scores
          </button>
        </div>
        
        <div v-if="selectedStudentId === student.id && poScores.length > 0" class="po-scores">
          <h4>Program Outcome Scores</h4>
          <div class="scores-grid">
            <div v-for="score in poScores" :key="score.po_code" class="score-item">
              <div class="score-header">
                <span class="po-label">{{ score.po_code }}</span>
                <span class="score-value" :style="{ color: getScoreColor(score.score) }">
                  {{ score.score.toFixed(2) }}%
                </span>
              </div>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: score.score + '%', background: getScoreColor(score.score) }"></div>
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
          <h3>Add New Student</h3>
          <button @click="showAddModal = false" class="btn-close">×</button>
        </div>
        <form @submit.prevent="addStudent" class="modal-body">
          <div class="form-group">
            <label>First Name</label>
            <input v-model="newStudent.first_name" type="text" placeholder="Enter first name" required>
          </div>
          <div class="form-group">
            <label>Last Name</label>
            <input v-model="newStudent.last_name" type="text" placeholder="Enter last name" required>
          </div>
          <div class="form-group">
            <label>Username</label>
            <input v-model="newStudent.username" type="text" placeholder="Enter username" required>
          </div>
          <div class="form-group">
            <label>Student Number</label>
            <input v-model="newStudent.student_number" type="text" placeholder="e.g., 20230123" required>
          </div>
          <div class="modal-footer">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">Create Student</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Import Excel Modal -->
    <div v-if="showImportModal" class="modal-overlay" @click="showImportModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Import Students from OBS Excel</h3>
          <button @click="showImportModal = false" class="btn-close">×</button>
        </div>
        <form @submit.prevent="handleImport" class="modal-body">
          <div class="form-group">
            <label>Excel File (.xlsx)</label>
            <input type="file" accept=".xlsx,.xls" @change="onFileChange" required>
          </div>
          <div class="form-group">
            <label>Select Existing Course (or leave empty to create new)</label>
            <select v-model="importData.courseId" class="course-select">
              <option :value="null">-- Create New Course --</option>
              <option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.code }} - {{ course.name }}
              </option>
            </select>
          </div>
          <div v-if="!importData.courseId" class="new-course-fields">
            <div class="form-group">
              <label>Course Code</label>
              <input v-model="importData.courseCode" type="text" placeholder="e.g., CSE311 (auto-detect from Excel if empty)">
            </div>
            <div class="form-group">
              <label>Course Name</label>
              <input v-model="importData.courseName" type="text" placeholder="e.g., Operating Systems">
            </div>
          </div>
          <div v-if="importResult" class="import-result" :class="importResult.success ? 'success' : 'error'">
            <p v-if="importResult.success">
              ✅ Course: {{ importResult.course }} ({{ importResult.course_created ? 'created' : 'existed' }})<br>
              Students: {{ importResult.students_created }} created, {{ importResult.students_skipped }} skipped<br>
              Assessments: {{ importResult.assessments_created || 0 }} created<br>
              Grades: {{ importResult.grades_created || 0 }} imported
            </p>
            <p v-else>❌ {{ importResult.message }}</p>
          </div>
          <div class="modal-footer">
            <button type="button" @click="showImportModal = false" class="btn-secondary">Close</button>
            <button type="submit" class="btn-primary" :disabled="importing">
              {{ importing ? 'Importing...' : 'Import' }}
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

function getScoreClass(score) {
  if (score >= 80) return 'score-excellent'
  if (score >= 60) return 'score-good'
  if (score >= 40) return 'score-fair'
  return 'score-poor'
}

function getScoreColor(score) {
  // Clamp score between 0 and 100
  const s = Math.max(0, Math.min(100, score))
  
  // Red to Yellow to Green gradient
  // 0% = Red (255, 0, 0)
  // 50% = Yellow (255, 200, 0)
  // 100% = Green (16, 185, 129)
  
  let r, g, b
  
  if (s <= 50) {
    // Red to Yellow (0-50%)
    const ratio = s / 50
    r = 255
    g = Math.round(ratio * 200)
    b = 0
  } else {
    // Yellow to Green (50-100%)
    const ratio = (s - 50) / 50
    r = Math.round(255 - ratio * (255 - 16))
    g = Math.round(200 + ratio * (185 - 200))
    b = Math.round(ratio * 129)
  }
  
  return `rgb(${r}, ${g}, ${b})`
}

onMounted(() => {
  loadCourses()
  loadStudents()
})
</script>

<style scoped>
.students-view {
  max-width: 1200px;
  margin: 0 auto;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-left h2 {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: var(--text-secondary);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  box-shadow: var(--shadow-md);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-secondary {
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: 12px 24px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--bg-secondary);
  border-color: var(--primary-color);
}

.btn-sm {
  padding: 8px 16px;
  font-size: 14px;
}

.students-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.student-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
  box-shadow: var(--shadow-sm);
}

.student-card:hover {
  box-shadow: var(--shadow-md);
}

.student-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.student-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  flex-shrink: 0;
}

.student-info {
  flex: 1;
}

.student-info h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.student-number {
  font-size: 14px;
  color: var(--text-secondary);
}

.po-scores {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.po-scores h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.scores-grid {
  display: grid;
  gap: 16px;
}

.score-item {
  background: var(--bg-primary);
  padding: 16px;
  border-radius: 12px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.po-label {
  font-weight: 600;
  color: var(--text-primary);
}

.score-value {
  font-size: 18px;
  font-weight: 700;
}

.score-excellent { color: #10b981; }
.score-good { color: #3b82f6; }
.score-fair { color: #f59e0b; }
.score-poor { color: #ef4444; }

.score-bar {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  transition: width 0.3s ease, background 0.3s ease;
  border-radius: 4px;
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
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 24px;
  font-weight: 700;
}

.btn-close {
  background: none;
  border: none;
  font-size: 32px;
  color: var(--text-secondary);
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.import-result {
  padding: 12px;
  border-radius: 8px;
  margin-top: 16px;
}

.import-result.success {
  background: #d1fae5;
  color: #065f46;
}

.import-result.error {
  background: #fee2e2;
  color: #991b1b;
}

.course-select {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  min-width: 200px;
}

.course-select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px dashed var(--border-color);
}
</style>
