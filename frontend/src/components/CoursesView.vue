<template>
  <div class="courses-view">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1>📚 Course Management</h1>
          <p>Create, manage, and track your courses with learning outcomes and assessments</p>
        </div>
        <button @click="showAddModal = true" class="btn-add">
          + Add New Course
        </button>
      </div>
      
      <!-- Stats Cards -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">📖</div>
          <div class="stat-info">
            <div class="stat-value">{{ courses.length }}</div>
            <div class="stat-label">Total Courses</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalLOs }}</div>
            <div class="stat-label">Learning Outcomes</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalAssessments }}</div>
            <div class="stat-label">Assessments</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔗</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalMappings }}</div>
            <div class="stat-label">LO-PO Mappings</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="toolbar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search courses by code or name..."
          class="search-input"
        />
      </div>
      <div class="view-toggle">
        <button 
          :class="['toggle-btn', { active: viewMode === 'grid' }]"
          @click="viewMode = 'grid'"
        >
          ▦ Grid
        </button>
        <button 
          :class="['toggle-btn', { active: viewMode === 'list' }]"
          @click="viewMode = 'list'"
        >
          ☰ List
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredCourses.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>No courses found</h3>
      <p v-if="searchQuery">Try adjusting your search terms</p>
      <p v-else>Get started by adding your first course</p>
      <button v-if="!searchQuery" @click="showAddModal = true" class="btn-add">
        + Add Your First Course
      </button>
    </div>

    <!-- Courses Grid -->
    <div v-else :class="['courses-container', viewMode]">
      <div 
        v-for="(course, index) in filteredCourses" 
        :key="course.id" 
        class="course-card"
      >
        <!-- Card Accent -->
        <div class="card-accent" :style="{ background: getCardColor(index) }"></div>
        
        <!-- Card Content -->
        <div class="card-body">
          <div class="card-header">
            <div class="course-badge" :style="{ background: getCardColor(index) }">
              {{ course.code }}
            </div>
            <div class="card-actions">
              <button @click="deleteCourse(course.id)" class="action-btn delete" title="Delete Course">
                🗑️
              </button>
            </div>
          </div>
          
          <h3 class="course-title">{{ course.name }}</h3>
          
          <div class="course-info">
            <div class="info-item">
              <span class="info-icon">📅</span>
              <span>{{ course.semester || 'Not set' }}</span>
            </div>
            <div class="info-item">
              <span class="info-icon">🏛️</span>
              <span>{{ course.department }}</span>
            </div>
          </div>

          <!-- Course Stats -->
          <div class="course-stats">
            <div class="mini-stat">
              <span class="mini-stat-icon">📚</span>
              <span class="mini-stat-value">{{ getCourseLoCount(course.id) }}</span>
              <span class="mini-stat-label">Learning Outcomes</span>
            </div>
            <div class="mini-stat">
              <span class="mini-stat-icon">📝</span>
              <span class="mini-stat-value">{{ getCourseAssessmentCount(course.id) }}</span>
              <span class="mini-stat-label">Assessments</span>
            </div>
            <div class="mini-stat">
              <span class="mini-stat-icon">🔗</span>
              <span class="mini-stat-value">{{ getCourseMappingCount(course.id) }}</span>
              <span class="mini-stat-label">PO Mappings</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <button @click="$emit('viewCourse', course.id)" class="btn-view-details">
            View Details →
          </button>
        </div>
      </div>
    </div>

    <!-- Add Course Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📚 Add New Course</h3>
          <button @click="showAddModal = false" class="btn-close">×</button>
        </div>
        
        <!-- Tab Buttons -->
        <div class="modal-tabs">
          <button 
            :class="['tab-btn', { active: addMode === 'manual' }]"
            @click="addMode = 'manual'"
          >
            ✏️ Manual Entry
          </button>
          <button 
            :class="['tab-btn', { active: addMode === 'excel' }]"
            @click="addMode = 'excel'"
          >
            📊 Import from Excel
          </button>
        </div>

        <!-- Manual Entry Form -->
        <form v-if="addMode === 'manual'" @submit.prevent="addCourse" class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>🏷️ Course Code</label>
              <input v-model="newCourse.code" type="text" placeholder="e.g., CSE311" required />
            </div>
            <div class="form-group">
              <label>🏛️ Department</label>
              <input v-model="newCourse.department" type="text" placeholder="e.g., CSE" />
            </div>
          </div>
          <div class="form-group">
            <label>📖 Course Name</label>
            <input v-model="newCourse.name" type="text" placeholder="e.g., Software Engineering" required />
          </div>
          <div class="form-group">
            <label>📅 Semester</label>
            <input v-model="newCourse.semester" type="text" placeholder="e.g., 2024-Fall" />
          </div>
          <div class="modal-footer">
            <button type="button" @click="showAddModal = false" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary">
              ✨ Create Course
            </button>
          </div>
        </form>

        <!-- Excel Import Form -->
        <div v-else class="modal-body">
          <div class="excel-info">
            <p>📋 Upload an OBS Excel file to automatically create the course with students, assessments, and grades.</p>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>🏷️ Course Code</label>
              <input v-model="excelImport.courseCode" type="text" placeholder="e.g., CSE311" required />
            </div>
            <div class="form-group">
              <label>📖 Course Name</label>
              <input v-model="excelImport.courseName" type="text" placeholder="e.g., Software Engineering" required />
            </div>
          </div>
          
          <div class="form-group">
            <label>📁 Excel File</label>
            <input 
              type="file" 
              accept=".xlsx,.xls" 
              @change="handleExcelFile"
              class="file-input"
            />
          </div>
          
          <div v-if="excelImport.importing" class="import-status">
            <span class="loading-spinner">⏳</span> Importing...
          </div>
          
          <div v-if="excelImport.result" :class="['import-result', excelImport.result.success ? 'success' : 'error']">
            <template v-if="excelImport.result.success">
              ✅ Import successful!<br/>
              📚 Course: {{ excelImport.result.course_code }}<br/>
              👥 Students: {{ excelImport.result.students_created }} created, {{ excelImport.result.students_updated }} updated<br/>
              📝 Assessments: {{ excelImport.result.assessments_created || 0 }} created<br/>
              📊 Grades: {{ excelImport.result.grades_created || 0 }} imported
            </template>
            <template v-else>
              ❌ {{ excelImport.result.error }}
            </template>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeExcelModal" class="btn-secondary">
              Close
            </button>
            <button 
              type="button" 
              @click="importExcel" 
              class="btn-primary"
              :disabled="!excelImport.file || !excelImport.courseCode || !excelImport.courseName || excelImport.importing"
            >
              📥 Import Course
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const emit = defineEmits(['viewCourse'])

const courses = ref([])
const learningOutcomes = ref([])
const assessments = ref([])
const mappings = ref([])
const loading = ref(true)
const showAddModal = ref(false)
const searchQuery = ref('')
const viewMode = ref('grid')
const addMode = ref('manual')

const newCourse = ref({
  code: '',
  name: '',
  semester: '',
  department: 'CSE'
})

const excelImport = ref({
  file: null,
  courseCode: '',
  courseName: '',
  importing: false,
  result: null
})

// Computed properties
const filteredCourses = computed(() => {
  if (!searchQuery.value) return courses.value
  const query = searchQuery.value.toLowerCase()
  return courses.value.filter(c => 
    c.code.toLowerCase().includes(query) || 
    c.name.toLowerCase().includes(query)
  )
})

const totalLOs = computed(() => learningOutcomes.value.length)
const totalAssessments = computed(() => assessments.value.length)
const totalMappings = computed(() => mappings.value.length)

// Helper functions
function getCourseLoCount(courseId) {
  return learningOutcomes.value.filter(lo => lo.course === courseId).length
}

function getCourseAssessmentCount(courseId) {
  return assessments.value.filter(a => a.course === courseId).length
}

function getCourseMappingCount(courseId) {
  const courseLOs = learningOutcomes.value.filter(lo => lo.course === courseId).map(lo => lo.id)
  return mappings.value.filter(m => courseLOs.includes(m.learning_outcome)).length
}

function getCourseProgress(courseId) {
  const hasLOs = getCourseLoCount(courseId) > 0
  const hasAssessments = getCourseAssessmentCount(courseId) > 0
  const hasMappings = getCourseMappingCount(courseId) > 0
  
  let progress = 25
  if (hasLOs) progress += 25
  if (hasAssessments) progress += 25
  if (hasMappings) progress += 25
  
  return progress
}

function getCardColor(index) {
  const colors = [
    'linear-gradient(135deg, #667eea, #764ba2)',
    'linear-gradient(135deg, #f093fb, #f5576c)',
    'linear-gradient(135deg, #4facfe, #00f2fe)',
    'linear-gradient(135deg, #43e97b, #38f9d7)',
    'linear-gradient(135deg, #fa709a, #fee140)',
    'linear-gradient(135deg, #a8edea, #fed6e3)',
  ]
  return colors[index % colors.length]
}

function getProgressColor(progress) {
  if (progress >= 100) return 'linear-gradient(90deg, #10b981, #34d399)'
  if (progress >= 75) return 'linear-gradient(90deg, #3b82f6, #60a5fa)'
  if (progress >= 50) return 'linear-gradient(90deg, #f59e0b, #fbbf24)'
  return 'linear-gradient(90deg, #ef4444, #f87171)'
}

// API functions
async function loadData() {
  loading.value = true
  try {
    const [coursesRes, losRes, assessRes, mappingsRes] = await Promise.all([
      api.getCourses(),
      api.getLearningOutcomes(),
      api.getAssessments(),
      api.getMappings()
    ])
    courses.value = coursesRes.data
    learningOutcomes.value = losRes.data
    assessments.value = assessRes.data
    mappings.value = mappingsRes.data
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

async function addCourse() {
  try {
    await api.createCourse(newCourse.value)
    showAddModal.value = false
    newCourse.value = { code: '', name: '', semester: '', department: 'CSE' }
    await loadData()
  } catch (error) {
    console.error('Error adding course:', error)
    alert('Failed to add course')
  }
}

async function deleteCourse(id) {
  if (!confirm('Are you sure you want to delete this course? This will delete all associated data.')) {
    return
  }
  
  try {
    await api.deleteCourse(id)
    await loadData()
  } catch (error) {
    console.error('Error deleting course:', error)
    alert('Failed to delete course')
  }
}

function handleExcelFile(event) {
  const file = event.target.files[0]
  if (file) {
    excelImport.value.file = file
    excelImport.value.result = null
  }
}

async function importExcel() {
  if (!excelImport.value.file || !excelImport.value.courseCode || !excelImport.value.courseName) {
    alert('Please fill in course code, name, and select an Excel file')
    return
  }
  
  excelImport.value.importing = true
  excelImport.value.result = null
  
  try {
    const response = await api.importObsExcel(
      excelImport.value.file,
      null, // No existing course ID - create new
      excelImport.value.courseCode,
      excelImport.value.courseName
    )
    excelImport.value.result = { success: true, ...response.data }
    await loadData() // Refresh courses list
  } catch (error) {
    console.error('Import error:', error)
    excelImport.value.result = {
      success: false,
      error: error.response?.data?.error || 'Failed to import Excel file'
    }
  } finally {
    excelImport.value.importing = false
  }
}

function closeExcelModal() {
  showAddModal.value = false
  addMode.value = 'manual'
  excelImport.value = {
    file: null,
    courseCode: '',
    courseName: '',
    importing: false,
    result: null
  }
}

function viewCourseDetails(id) {
  console.log('View course:', id)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.courses-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 28px;
  color: white;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 60%;
  height: 200%;
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(25deg);
  pointer-events: none;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  position: relative;
  z-index: 1;
  flex-wrap: wrap;
  gap: 16px;
}

.hero-text h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.hero-text p {
  font-size: 15px;
  opacity: 0.9;
  margin: 0;
}

.btn-add {
  background: white;
  color: #667eea;
  padding: 14px 28px;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  position: relative;
  z-index: 1;
}

@media (max-width: 900px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.stat-info {
  min-width: 0;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  opacity: 0.85;
  white-space: nowrap;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  max-width: 400px;
  min-width: 200px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.view-toggle {
  display: flex;
  background: #f3f4f6;
  border-radius: 10px;
  padding: 4px;
}

.toggle-btn {
  padding: 10px 18px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  color: #6b7280;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 30px;
  background: white;
  border-radius: 16px;
  border: 2px dashed #e5e7eb;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 22px;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.empty-state p {
  color: #6b7280;
  margin: 0 0 20px 0;
}

/* Courses Container */
.courses-container {
  display: grid;
  gap: 24px;
}

.courses-container.grid {
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
}

.courses-container.list {
  grid-template-columns: 1fr;
}

/* Course Card */
.course-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
  box-shadow: var(--shadow-sm);
}

.course-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.card-accent {
  height: 5px;
  width: 100%;
}

.card-body {
  padding: 22px;
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.course-badge {
  color: white;
  padding: 8px 14px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5px;
}

.card-actions {
  display: flex;
  gap: 6px;
}

.action-btn {
  width: 34px;
  height: 34px;
  border: none;
  background: #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: #e0e7ff;
}

.action-btn.delete:hover {
  background: #fee2e2;
}

.course-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 14px 0;
  line-height: 1.4;
}

.course-info {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 18px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
}

.info-icon {
  font-size: 15px;
}

/* Course Stats */
.course-stats {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}

.mini-stat {
  flex: 1;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 16px 12px;
  border-radius: 12px;
  text-align: center;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.mini-stat:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.mini-stat-icon {
  display: block;
  font-size: 20px;
  margin-bottom: 6px;
}

.mini-stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.mini-stat-label {
  font-size: 10px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

/* Progress Section */
.progress-section {
  margin-bottom: 0;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.progress-label {
  font-size: 12px;
  color: #6b7280;
}

.progress-value {
  font-size: 12px;
  font-weight: 600;
  color: #1f2937;
}

.progress-bar {
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* Card Footer */
.card-footer {
  padding: 14px 22px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.btn-view-details {
  width: 100%;
  padding: 11px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s;
}

.card-footer {
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 26px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.btn-close {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 22px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  line-height: 1;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 26px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 500px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 8px;
}

.btn-secondary {
  padding: 12px 22px;
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  color: #374151;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  padding: 12px 22px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Modal Tabs */
.modal-tabs {
  display: flex;
  gap: 8px;
  padding: 0 24px;
  margin-bottom: 16px;
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  background: #f9fafb;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.tab-btn.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: transparent;
  color: white;
}

/* Excel Import Styles */
.excel-info {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 16px;
}

.excel-info p {
  margin: 0;
  color: #0369a1;
  font-size: 14px;
}

.file-input {
  width: 100%;
  padding: 12px;
  border: 2px dashed #d1d5db;
  border-radius: 10px;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s;
}

.file-input:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.import-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fef3c7;
  border-radius: 10px;
  color: #92400e;
  font-weight: 500;
  margin-bottom: 16px;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.import-result {
  padding: 14px 16px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.import-result.success {
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  color: #065f46;
}

.import-result.error {
  background: #fee2e2;
  border: 1px solid #fca5a5;
  color: #991b1b;
}
</style>
