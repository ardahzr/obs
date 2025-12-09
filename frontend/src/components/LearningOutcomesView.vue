<template>
  <div class="learning-outcomes-view">
    <div class="view-header">
      <div class="header-left">
        <h2>Learning Outcomes</h2>
        <p class="subtitle">Manage learning outcomes for each course</p>
      </div>
      <div class="header-actions">
        <select v-model="selectedCourse" class="course-select">
          <option value="">Select Course</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.code }} - {{ course.name }}
          </option>
        </select>
        <button @click="openAddModal" class="btn-primary" :disabled="!selectedCourse">
          <span class="icon">+</span> Add New LO
        </button>
      </div>
    </div>

    <div v-if="!selectedCourse" class="empty-state">
      <p>📚 Please select a course to manage its Learning Outcomes</p>
    </div>

    <div v-else class="outcomes-list">
      <div v-for="lo in filteredOutcomes" :key="lo.id" class="outcome-card">
        <div class="outcome-header">
          <div class="outcome-code">{{ lo.code }}</div>
          <div class="outcome-actions">
            <button @click="openEditModal(lo)" class="btn-icon" title="Edit">✏️</button>
            <button @click="deleteOutcome(lo.id)" class="btn-icon" title="Delete">🗑️</button>
          </div>
        </div>
        <p class="outcome-description">{{ lo.description }}</p>
      </div>
      
      <div v-if="filteredOutcomes.length === 0" class="no-data">
        <p>No Learning Outcomes found for this course.</p>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Learning Outcome' : 'Add New Learning Outcome' }}</h3>
          <button @click="closeModal" class="btn-close">×</button>
        </div>
        <form @submit.prevent="saveOutcome" class="modal-body">
          <div class="form-group">
            <label>Code</label>
            <input 
              v-model="formData.code" 
              placeholder="e.g., LO-1"
              required
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="formData.description" 
              rows="4" 
              placeholder="Enter learning outcome description..."
              required
              class="form-textarea"
            ></textarea>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">{{ isEditing ? 'Update' : 'Create' }} LO</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../services/api'

const courses = ref([])
const outcomes = ref([])
const selectedCourse = ref('')
const showModal = ref(false)
const isEditing = ref(false)
const formData = ref({
  id: null,
  code: '',
  description: ''
})

const filteredOutcomes = computed(() => {
  if (!selectedCourse.value) return []
  return outcomes.value.filter(lo => lo.course == selectedCourse.value)
})

async function loadData() {
  try {
    const [coursesRes, outcomesRes] = await Promise.all([
      api.getCourses(),
      api.getLearningOutcomes()
    ])
    courses.value = coursesRes.data
    outcomes.value = outcomesRes.data
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

function openAddModal() {
  isEditing.value = false
  formData.value = { id: null, code: '', description: '' }
  showModal.value = true
}

function openEditModal(lo) {
  isEditing.value = true
  formData.value = { ...lo }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  formData.value = { id: null, code: '', description: '' }
  isEditing.value = false
}

async function saveOutcome() {
  try {
    if (isEditing.value) {
      await api.updateLearningOutcome(formData.value.id, {
        code: formData.value.code,
        description: formData.value.description,
        course: selectedCourse.value
      })
    } else {
      await api.createLearningOutcome({
        code: formData.value.code,
        description: formData.value.description,
        course: selectedCourse.value
      })
    }
    closeModal()
    // Reload outcomes
    const res = await api.getLearningOutcomes()
    outcomes.value = res.data
  } catch (error) {
    console.error('Error saving outcome:', error)
    alert('Failed to save outcome')
  }
}

async function deleteOutcome(id) {
  if (!confirm('Are you sure you want to delete this Learning Outcome? This will also delete all associated mappings.')) {
    return
  }
  
  try {
    await api.deleteLearningOutcome(id)
    // Reload outcomes
    const res = await api.getLearningOutcomes()
    outcomes.value = res.data
  } catch (error) {
    console.error('Error deleting outcome:', error)
    alert('Failed to delete outcome')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.learning-outcomes-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.course-select {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  min-width: 250px;
  background: white;
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

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #ccc;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 16px;
  border: 2px dashed var(--border-color);
  color: var(--text-secondary);
  font-size: 18px;
}

.outcomes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.outcome-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
  box-shadow: var(--shadow-sm);
}

.outcome-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
}

.outcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.outcome-code {
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 16px;
}

.outcome-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--bg-primary);
}

.outcome-description {
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-primary);
}

.no-data {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-style: italic;
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
  max-width: 600px;
  width: 100%;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
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
</style>