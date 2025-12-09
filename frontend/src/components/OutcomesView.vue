<template>
  <div class="outcomes-view">
    <div class="view-header">
      <div class="header-left">
        <h2>Program Outcomes</h2>
        <p class="subtitle">Manage and track all program learning outcomes</p>
      </div>
      <button @click="openAddModal" class="btn-primary">
        <span class="icon">+</span> Add New Outcome
      </button>
    </div>

    <div class="outcomes-list">
      <div v-for="outcome in outcomes" :key="outcome.id" class="outcome-card">
        <div class="outcome-header">
          <div class="outcome-code">{{ outcome.code }}</div>
          <div class="outcome-actions">
            <button @click="openEditModal(outcome)" class="btn-icon" title="Edit">✏️</button>
            <button @click="deleteOutcome(outcome.id)" class="btn-icon" title="Delete">🗑️</button>
          </div>
        </div>
        <p class="outcome-description">{{ outcome.description }}</p>
        <div class="outcome-footer">
          <span class="stat-badge">
            <span class="stat-label">Mapped LOs:</span>
            <span class="stat-value">{{ getMappingCount(outcome.id) }}</span>
          </span>
          <span class="stat-badge">
            <span class="stat-label">Courses:</span>
            <span class="stat-value">{{ getCourseCount(outcome.id) }}</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Add/Edit Outcome Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Program Outcome' : 'Add New Program Outcome' }}</h3>
          <button @click="closeModal" class="btn-close">×</button>
        </div>
        <form @submit.prevent="saveOutcome" class="modal-body">
          <div class="form-group">
            <label>Code</label>
            <input 
              v-model="newOutcome.code" 
              placeholder="e.g., PO-1"
              required
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="newOutcome.description" 
              rows="4" 
              placeholder="Enter program outcome description..."
              required
              class="form-textarea"
            ></textarea>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">{{ isEditing ? 'Update' : 'Create' }} Outcome</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const outcomes = ref([])
const mappings = ref([])
const courses = ref([])
const showAddModal = ref(false)
const isEditing = ref(false)
const newOutcome = ref({
  id: null,
  code: '',
  description: ''
})

async function loadData() {
  try {
    const [outcomesRes, mappingsRes, coursesRes] = await Promise.all([
      api.getProgramOutcomes(),
      api.getLoToPoMappings(),
      api.getCourses()
    ])
    outcomes.value = outcomesRes.data
    mappings.value = mappingsRes.data
    courses.value = coursesRes.data
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

function getMappingCount(poId) {
  return mappings.value.filter(m => m.program_outcome === poId).length
}

function getCourseCount(poId) {
  const loIds = mappings.value
    .filter(m => m.program_outcome === poId)
    .map(m => m.learning_outcome)
  
  const uniqueCourses = new Set()
  courses.value.forEach(course => {
    if (course.learning_outcomes && course.learning_outcomes.some(lo => loIds.includes(lo.id))) {
      uniqueCourses.add(course.id)
    }
  })
  
  return uniqueCourses.size
}

function openAddModal() {
  isEditing.value = false
  newOutcome.value = { id: null, code: '', description: '' }
  showAddModal.value = true
}

function openEditModal(outcome) {
  isEditing.value = true
  newOutcome.value = { ...outcome }
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  newOutcome.value = { id: null, code: '', description: '' }
  isEditing.value = false
}

async function saveOutcome() {
  try {
    if (isEditing.value) {
      await api.updateProgramOutcome(newOutcome.value.id, {
        code: newOutcome.value.code,
        description: newOutcome.value.description
      })
    } else {
      await api.createProgramOutcome({
        code: newOutcome.value.code,
        description: newOutcome.value.description
      })
    }
    closeModal()
    await loadData()
  } catch (error) {
    console.error('Error saving outcome:', error)
    alert('Failed to save outcome')
  }
}

async function deleteOutcome(id) {
  if (!confirm('Are you sure you want to delete this Program Outcome? This will also delete all associated mappings.')) {
    return
  }
  
  try {
    await api.deleteProgramOutcome(id)
    await loadData()
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
.outcomes-view {
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
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  padding: 8px 20px;
  border-radius: 10px;
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
  margin-bottom: 20px;
}

.outcome-footer {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-primary);
  border-radius: 8px;
  font-size: 14px;
}

.stat-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  color: var(--primary-color);
  font-weight: 700;
  font-size: 16px;
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
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>
