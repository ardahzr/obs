<template>
  <div class="learning-outcomes-view">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
          </svg>
        </div>
        <div class="header-text">
          <h1>Learning Outcomes</h1>
          <p>Define and manage course-specific learning objectives</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="course-selector-wrapper">
          <div class="course-selector" @click="showCourseDropdown = !showCourseDropdown">
            <span class="selector-icon">📚</span>
            <span class="selector-text">{{ selectedCourseName || 'Select a Course' }}</span>
            <span class="selector-arrow">{{ showCourseDropdown ? '▲' : '▼' }}</span>
          </div>
          <div class="course-dropdown" v-if="showCourseDropdown">
            <div class="dropdown-header">
              <span>📖</span> Choose a course
            </div>
            <div 
              v-for="course in courses" 
              :key="course.id" 
              class="dropdown-item"
              :class="{ active: selectedCourse === course.id }"
              @click="selectCourseItem(course.id)"
            >
              <div class="dropdown-item-main">
                <span class="course-code-badge">{{ course.code }}</span>
                <span class="course-name-text">{{ course.name }}</span>
              </div>
            </div>
            <div v-if="courses.length === 0" class="dropdown-empty">
              No courses available
            </div>
          </div>
        </div>
        <button @click="openAddModal" class="btn-add" :disabled="!selectedCourse">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Add Learning Outcome
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!selectedCourse" class="empty-state">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
      </div>
      <h3>Select a Course</h3>
      <p>Choose a course from the dropdown above to view and manage its learning outcomes</p>
    </div>

    <!-- Outcomes Grid -->
    <div v-else class="outcomes-container">
      <div class="outcomes-header">
        <div class="outcomes-count">
          <span class="count-badge">{{ filteredOutcomes.length }}</span>
          <span>Learning Outcome{{ filteredOutcomes.length !== 1 ? 's' : '' }}</span>
        </div>
      </div>

      <div v-if="filteredOutcomes.length > 0" class="outcomes-grid">
        <div v-for="(lo, index) in filteredOutcomes" :key="lo.id" class="outcome-card">
          <div class="card-accent" :style="{ background: getAccentColor(index) }"></div>
          <div class="card-content">
            <div class="card-header">
              <div class="lo-badge" :style="{ background: getAccentColor(index) + '20', color: getAccentColor(index) }">
                {{ lo.code }}
              </div>
              <div class="card-actions">
                <button @click="openEditModal(lo)" class="action-btn edit" title="Edit">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteOutcome(lo.id)" class="action-btn delete" title="Delete">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            </div>
            <p class="lo-description">{{ lo.description }}</p>
          </div>
        </div>
      </div>
      
      <div v-else class="no-outcomes">
        <div class="no-outcomes-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="18" x2="12" y2="12"></line>
            <line x1="9" y1="15" x2="15" y2="15"></line>
          </svg>
        </div>
        <h3>No Learning Outcomes Yet</h3>
        <p>Get started by adding the first learning outcome for this course</p>
        <button @click="openAddModal" class="btn-add-first">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Add First Learning Outcome
        </button>
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
const showCourseDropdown = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const formData = ref({
  id: null,
  code: '',
  description: ''
})

const accentColors = [
  '#6366f1', // indigo
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#f59e0b', // amber
  '#10b981', // emerald
  '#3b82f6', // blue
  '#ef4444', // red
  '#14b8a6', // teal
]

function getAccentColor(index) {
  return accentColors[index % accentColors.length]
}

const selectedCourseName = computed(() => {
  const course = courses.value.find(c => c.id === selectedCourse.value)
  return course ? `${course.code} - ${course.name}` : ''
})

function selectCourseItem(courseId) {
  selectedCourse.value = courseId
  showCourseDropdown.value = false
}

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

// Close dropdown when clicking outside
function handleClickOutside(event) {
  const wrapper = document.querySelector('.course-selector-wrapper')
  if (wrapper && !wrapper.contains(event.target)) {
    showCourseDropdown.value = false
  }
}

onMounted(() => {
  loadData()
  document.addEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.learning-outcomes-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
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
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
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
  align-items: center;
  gap: 16px;
}

.course-selector-wrapper {
  position: relative;
}

.course-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: white;
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  min-width: 280px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.course-selector:hover {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.selector-icon {
  font-size: 1.3rem;
}

.selector-text {
  flex: 1;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.selector-arrow {
  font-size: 0.75rem;
  color: #666;
  transition: transform 0.3s ease;
}

.course-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 350px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  overflow: hidden;
  animation: dropdownSlide 0.2s ease;
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-header {
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dropdown-item {
  padding: 1rem 1.25rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.2s ease;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #f8f9ff;
}

.dropdown-item.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-left: 4px solid #6366f1;
}

.dropdown-item-main {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.course-code-badge {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
}

.course-name-text {
  font-size: 0.95rem;
  color: #333;
  font-weight: 500;
}

.dropdown-empty {
  padding: 1.5rem;
  text-align: center;
  color: #888;
  font-style: italic;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.btn-add:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.btn-add:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #94a3b8;
  box-shadow: none;
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
  margin: 0 auto;
  line-height: 1.6;
}

/* Outcomes Container */
.outcomes-container {
  background: white;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.outcomes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f5f9;
}

.outcomes-count {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: #64748b;
  font-weight: 500;
}

.count-badge {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 14px;
}

/* Outcomes Grid */
.outcomes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
}

.outcome-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
  position: relative;
}

.outcome-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  border-color: transparent;
}

.card-accent {
  height: 4px;
  width: 100%;
}

.card-content {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.lo-badge {
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.5px;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  background: #f1f5f9;
  color: #64748b;
}

.action-btn:hover {
  transform: scale(1.1);
}

.action-btn.edit:hover {
  background: #dbeafe;
  color: #3b82f6;
}

.action-btn.delete:hover {
  background: #fee2e2;
  color: #ef4444;
}

.lo-description {
  font-size: 15px;
  line-height: 1.7;
  color: #475569;
  margin: 0;
}

/* No Outcomes State */
.no-outcomes {
  text-align: center;
  padding: 60px 40px;
}

.no-outcomes-icon {
  color: #cbd5e1;
  margin-bottom: 20px;
}

.no-outcomes h3 {
  font-size: 20px;
  font-weight: 700;
  color: #334155;
  margin: 0 0 8px 0;
}

.no-outcomes p {
  font-size: 15px;
  color: #64748b;
  margin: 0 0 24px 0;
}

.btn-add-first {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.btn-add-first:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
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
  max-width: 560px;
  width: 100%;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease;
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
  font-size: 24px;
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

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #334155;
  font-size: 14px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  transition: all 0.2s;
  background: #fafafa;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.btn-secondary {
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

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-primary {
  padding: 14px 24px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .learning-outcomes-view {
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
  
  .outcomes-grid {
    grid-template-columns: 1fr;
  }
}
</style>