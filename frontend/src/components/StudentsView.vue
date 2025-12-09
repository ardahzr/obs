<template>
  <div class="students-view">
    <div class="view-header">
      <div class="header-left">
        <h2>Students</h2>
        <p class="subtitle">Manage student records and track PO scores</p>
      </div>
      <button @click="showAddModal = true" class="btn-primary">
        <span class="icon">+</span> Add New Student
      </button>
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
                <span class="score-value" :class="getScoreClass(score.score)">
                  {{ score.score.toFixed(2) }}%
                </span>
              </div>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: score.score + '%' }"></div>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const students = ref([])
const poScores = ref([])
const selectedStudentId = ref(null)
const showAddModal = ref(false)
const newStudent = ref({
  first_name: '',
  last_name: '',
  username: '',
  student_number: ''
})

async function loadStudents() {
  try {
    const response = await api.getStudents()
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

function getInitials(firstName, lastName) {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

function getScoreClass(score) {
  if (score >= 80) return 'score-excellent'
  if (score >= 60) return 'score-good'
  if (score >= 40) return 'score-fair'
  return 'score-poor'
}

onMounted(() => {
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
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  transition: width 0.3s ease;
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
</style>
