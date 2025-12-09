<template>
  <div class="courses-view">
    <div class="view-header">
      <div class="header-left">
        <h2>Courses</h2>
        <p class="subtitle">Manage courses and their learning outcomes</p>
      </div>
      <button @click="showAddModal = true" class="btn-primary">
        <span class="icon">+</span> Add New Course
      </button>
    </div>

    <div class="courses-grid">
      <div v-for="course in courses" :key="course.id" class="course-card">
        <div class="card-header">
          <div class="course-code">{{ course.code }}</div>
          <div class="course-actions">
            <button @click="deleteCourse(course.id)" class="btn-icon" title="Delete Course">🗑️</button>
          </div>
        </div>
        <h3 class="course-name">{{ course.name }}</h3>
        <div class="course-meta">
          <span class="meta-item">
            <span class="icon">📅</span>
            {{ course.semester || 'No semester' }}
          </span>
          <span class="meta-item">
            <span class="icon">🏢</span>
            {{ course.department }}
          </span>
        </div>
        <div class="card-footer">
          <button @click="viewCourseDetails(course.id)" class="btn-secondary btn-sm">
            View Details
          </button>
        </div>
      </div>
    </div>

    <!-- Add Course Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New Course</h3>
          <button @click="showAddModal = false" class="btn-close">×</button>
        </div>
        <form @submit.prevent="addCourse" class="modal-body">
          <div class="form-group">
            <label>Course Code</label>
            <input v-model="newCourse.code" type="text" placeholder="e.g., CSE311" required>
          </div>
          <div class="form-group">
            <label>Course Name</label>
            <input v-model="newCourse.name" type="text" placeholder="e.g., Algorithms" required>
          </div>
          <div class="form-group">
            <label>Semester</label>
            <input v-model="newCourse.semester" type="text" placeholder="e.g., 2024-Fall">
          </div>
          <div class="form-group">
            <label>Department</label>
            <input v-model="newCourse.department" type="text" placeholder="e.g., CSE">
          </div>
          <div class="modal-footer">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">Create Course</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const courses = ref([])
const showAddModal = ref(false)
const newCourse = ref({
  code: '',
  name: '',
  semester: '',
  department: 'CSE'
})

async function loadCourses() {
  try {
    const response = await api.getCourses()
    courses.value = response.data
  } catch (error) {
    console.error('Error loading courses:', error)
  }
}

async function addCourse() {
  try {
    await api.createCourse(newCourse.value)
    showAddModal.value = false
    newCourse.value = { code: '', name: '', semester: '', department: 'CSE' }
    await loadCourses()
  } catch (error) {
    console.error('Error adding course:', error)
    alert('Failed to add course')
  }
}

async function deleteCourse(id) {
  if (!confirm('Are you sure you want to delete this course? This will delete all associated data (LOs, Assessments, etc.).')) {
    return
  }
  
  try {
    await api.deleteCourse(id)
    await loadCourses()
  } catch (error) {
    console.error('Error deleting course:', error)
    alert('Failed to delete course')
  }
}

function viewCourseDetails(id) {
  console.log('View course:', id)
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.courses-view {
  max-width: 1400px;
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

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.course-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
  box-shadow: var(--shadow-sm);
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.course-code {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  padding: 6px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--bg-primary);
}

.course-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.course-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
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

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
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
</style>
