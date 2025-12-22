<template>
  <div class="course-detail-view">
    <!-- Back Button & Header -->
    <div class="view-header">
      <button @click="$emit('back')" class="btn-back">
        <span>←</span> Back to Courses
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading course details...</p>
    </div>

    <div v-else-if="course" class="course-content">
      <!-- Course Info Card -->
      <div class="course-header-card">
        <div class="course-main-info">
          <div class="course-badge">{{ course.code }}</div>
          <h1 class="course-title">{{ course.name }}</h1>
          <div class="course-meta">
            <span class="meta-item">
              <span class="icon">📅</span> {{ course.semester || 'No semester' }}
            </span>
            <span class="meta-item">
              <span class="icon">🏢</span> {{ course.department }}
            </span>
          </div>
        </div>
        <div class="course-actions">
          <button @click="$emit('openEditor', course.id)" class="btn-primary">
            <span>🔗</span> Edit LO-PO Mappings
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon assessments">📝</div>
          <div class="stat-info">
            <div class="stat-value">{{ assessments.length }}</div>
            <div class="stat-label">Assessments</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon los">🎯</div>
          <div class="stat-info">
            <div class="stat-value">{{ learningOutcomes.length }}</div>
            <div class="stat-label">Learning Outcomes</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pos">🏆</div>
          <div class="stat-info">
            <div class="stat-value">{{ mappedPOCount }}</div>
            <div class="stat-label">POs Covered</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon mappings">🔗</div>
          <div class="stat-info">
            <div class="stat-value">{{ mappings.length }}</div>
            <div class="stat-label">Total Mappings</div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="content-grid">
        <!-- Learning Outcomes Section -->
        <div class="section-card">
          <div class="section-header">
            <h2>🎯 Learning Outcomes</h2>
            <span class="badge">{{ learningOutcomes.length }}</span>
          </div>
          <div class="section-body">
            <div v-if="learningOutcomes.length === 0" class="empty-state">
              No learning outcomes defined yet.
            </div>
            <div v-else class="lo-list">
              <div v-for="lo in learningOutcomes" :key="lo.id" class="lo-item">
                <div class="lo-header">
                  <span class="lo-code">{{ lo.code }}</span>
                  <span class="lo-mappings-count" v-if="getLOMappingCount(lo.id) > 0">
                    → {{ getLOMappingCount(lo.id) }} PO(s)
                  </span>
                </div>
                <p class="lo-description">{{ lo.description }}</p>
                <div class="lo-pos" v-if="getLOMappedPOs(lo.id).length > 0">
                  <span v-for="po in getLOMappedPOs(lo.id)" :key="po.id" class="po-tag">
                    {{ po.code }} ({{ po.contribution_weight }}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Assessments Section -->
        <div class="section-card">
          <div class="section-header">
            <h2>📝 Assessments</h2>
            <span class="badge">{{ assessments.length }}</span>
          </div>
          <div class="section-body">
            <div v-if="assessments.length === 0" class="empty-state">
              No assessments defined yet.
            </div>
            <div v-else class="assessment-list">
              <div v-for="assessment in assessments" :key="assessment.id" class="assessment-item">
                <div class="assessment-header">
                  <span class="assessment-name">{{ assessment.name }}</span>
                  <span class="assessment-type" :class="assessment.type">{{ assessment.type }}</span>
                </div>
                <div class="assessment-details">
                  <span class="assessment-points">{{ assessment.points }} points</span>
                  <span class="assessment-los" v-if="getAssessmentLOCount(assessment.id) > 0">
                    → {{ getAssessmentLOCount(assessment.id) }} LO(s)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- PO Coverage Chart -->
      <div class="section-card full-width">
        <div class="section-header">
          <h2>🏆 Program Outcome Coverage</h2>
        </div>
        <div class="section-body">
          <div v-if="programOutcomes.length === 0" class="empty-state">
            No program outcomes available.
          </div>
          <div v-else class="po-coverage-grid">
            <div v-for="po in programOutcomes" :key="po.id" class="po-coverage-item">
              <div class="po-header">
                <span class="po-code">{{ po.code }}</span>
                <span class="po-coverage-value" :class="getCoverageClass(po.id)">
                  {{ getPOCoverage(po.id) }}%
                </span>
              </div>
              <div class="po-description">{{ po.description }}</div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: getPOCoverage(po.id) + '%' }" :class="getCoverageClass(po.id)"></div>
              </div>
              <div class="po-los" v-if="getPOMappedLOs(po.id).length > 0">
                <span class="contributing-label">Contributing LOs:</span>
                <span v-for="lo in getPOMappedLOs(po.id)" :key="lo.id" class="lo-tag">
                  {{ lo.code }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mapping Matrix -->
      <div class="section-card full-width">
        <div class="section-header">
          <h2>📊 LO-PO Mapping Matrix</h2>
        </div>
        <div class="section-body">
          <div v-if="learningOutcomes.length === 0 || programOutcomes.length === 0" class="empty-state">
            Add learning outcomes and program outcomes to see the mapping matrix.
          </div>
          <div v-else class="matrix-container">
            <table class="mapping-matrix">
              <thead>
                <tr>
                  <th class="corner-cell">LO \ PO</th>
                  <th v-for="po in programOutcomes" :key="po.id" class="po-header-cell">
                    {{ po.code }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="lo in learningOutcomes" :key="lo.id">
                  <td class="lo-header-cell">{{ lo.code }}</td>
                  <td v-for="po in programOutcomes" :key="po.id" class="mapping-cell" :class="{ mapped: hasMapping(lo.id, po.id) }">
                    <span v-if="hasMapping(lo.id, po.id)" class="mapping-weight">
                      {{ getMappingWeight(lo.id, po.id) }}%
                    </span>
                    <span v-else class="no-mapping">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error-state">
      <p>Failed to load course details.</p>
      <button @click="loadCourseData" class="btn-primary">Retry</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'

const props = defineProps({
  courseId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['back', 'openEditor'])

const loading = ref(true)
const course = ref(null)
const learningOutcomes = ref([])
const programOutcomes = ref([])
const assessments = ref([])
const mappings = ref([])
const assessmentMappings = ref([])

const mappedPOCount = computed(() => {
  const mappedPOs = new Set(mappings.value.map(m => m.program_outcome))
  return mappedPOs.size
})

function getLOMappingCount(loId) {
  return mappings.value.filter(m => m.learning_outcome === loId).length
}

function getLOMappedPOs(loId) {
  const loMappings = mappings.value.filter(m => m.learning_outcome === loId)
  return loMappings.map(m => {
    const po = programOutcomes.value.find(p => p.id === m.program_outcome)
    return po ? { ...po, contribution_weight: m.contribution_weight } : null
  }).filter(Boolean)
}

function getAssessmentLOCount(assessmentId) {
  return assessmentMappings.value.filter(m => m.assessment === assessmentId).length
}

function getPOCoverage(poId) {
  const poMappings = mappings.value.filter(m => m.program_outcome === poId)
  if (poMappings.length === 0) return 0
  const totalWeight = poMappings.reduce((sum, m) => sum + (m.contribution_weight || 0), 0)
  return Math.min(totalWeight, 100)
}

function getCoverageClass(poId) {
  const coverage = getPOCoverage(poId)
  if (coverage >= 80) return 'high'
  if (coverage >= 40) return 'medium'
  if (coverage > 0) return 'low'
  return 'none'
}

function getPOMappedLOs(poId) {
  const poMappings = mappings.value.filter(m => m.program_outcome === poId)
  return poMappings.map(m => {
    const lo = learningOutcomes.value.find(l => l.id === m.learning_outcome)
    return lo || null
  }).filter(Boolean)
}

function hasMapping(loId, poId) {
  return mappings.value.some(m => m.learning_outcome === loId && m.program_outcome === poId)
}

function getMappingWeight(loId, poId) {
  const mapping = mappings.value.find(m => m.learning_outcome === loId && m.program_outcome === poId)
  if (!mapping) return 0
  let weight = mapping.contribution_weight
  // If weight is less than 1, assume it was entered as decimal and convert to percentage
  if (weight > 0 && weight < 1) {
    weight = weight * 100
  }
  return Math.round(weight)
}

async function loadCourseData() {
  loading.value = true
  try {
    // Load course info
    const courseRes = await api.getCourse(props.courseId)
    course.value = courseRes.data

    // Load all related data
    const [losRes, posRes, assessRes, mappingsRes, assMappingsRes] = await Promise.all([
      api.getLearningOutcomes(),
      api.getProgramOutcomes(),
      api.getAssessments(),
      api.getMappings(),
      api.getAssessmentToLoMappings()
    ])

    // Filter LOs for this course
    learningOutcomes.value = losRes.data.filter(lo => lo.course === props.courseId)
    programOutcomes.value = posRes.data
    
    // Filter assessments for this course
    assessments.value = assessRes.data.filter(a => a.course === props.courseId)
    
    // Filter mappings for this course's LOs
    const courseLoIds = learningOutcomes.value.map(lo => lo.id)
    mappings.value = mappingsRes.data.filter(m => courseLoIds.includes(m.learning_outcome))
    
    // Filter assessment mappings for this course
    const courseAssessmentIds = assessments.value.map(a => a.id)
    assessmentMappings.value = assMappingsRes.data.filter(m => courseAssessmentIds.includes(m.assessment))
    
  } catch (error) {
    console.error('Error loading course data:', error)
    course.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCourseData()
})
</script>

<style scoped>
.course-detail-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.view-header {
  margin-bottom: 24px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: var(--bg-primary);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

/* Course Header Card */
.course-header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  box-shadow: var(--shadow-md);
}

.course-badge {
  display: inline-block;
  background: rgba(255,255,255,0.2);
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 12px;
}

.course-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
}

.course-meta {
  display: flex;
  gap: 24px;
  opacity: 0.9;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.course-actions .btn-primary {
  background: white;
  color: #667eea;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.2s;
}

.course-actions .btn-primary:hover {
  transform: scale(1.05);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.assessments { background: #fef3c7; }
.stat-icon.los { background: #dbeafe; }
.stat-icon.pos { background: #d1fae5; }
.stat-icon.mappings { background: #ede9fe; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.section-card {
  background: white;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 24px;
}

.section-card.full-width {
  grid-column: 1 / -1;
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.section-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.badge {
  background: var(--primary-color);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.section-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  color: var(--text-secondary);
  padding: 40px 20px;
}

/* LO List */
.lo-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lo-item {
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.lo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.lo-code {
  font-weight: 700;
  color: #3b82f6;
}

.lo-mappings-count {
  font-size: 12px;
  color: var(--text-secondary);
}

.lo-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 8px;
}

.lo-pos {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.po-tag {
  background: #10b981;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

/* Assessment List */
.assessment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assessment-item {
  padding: 14px;
  background: var(--bg-primary);
  border-radius: 8px;
  border-left: 4px solid #f97316;
}

.assessment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.assessment-name {
  font-weight: 600;
  color: var(--text-primary);
}

.assessment-type {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 500;
  text-transform: uppercase;
}

.assessment-type.midterm { background: #fef3c7; color: #d97706; }
.assessment-type.final { background: #fee2e2; color: #dc2626; }
.assessment-type.project { background: #dbeafe; color: #2563eb; }
.assessment-type.quiz { background: #ede9fe; color: #7c3aed; }
.assessment-type.homework { background: #d1fae5; color: #059669; }

.assessment-details {
  font-size: 13px;
  color: var(--text-secondary);
  display: flex;
  gap: 16px;
}

/* PO Coverage */
.po-coverage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.po-coverage-item {
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.po-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.po-code {
  font-weight: 700;
  color: var(--text-primary);
}

.po-coverage-value {
  font-weight: 700;
  font-size: 14px;
}

.po-coverage-value.high { color: #10b981; }
.po-coverage-value.medium { color: #f59e0b; }
.po-coverage-value.low { color: #ef4444; }
.po-coverage-value.none { color: #9ca3af; }

.po-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.4;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-fill.high { background: #10b981; }
.progress-fill.medium { background: #f59e0b; }
.progress-fill.low { background: #ef4444; }
.progress-fill.none { background: #e5e7eb; }

.po-los {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.contributing-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.lo-tag {
  background: #3b82f6;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

/* Mapping Matrix */
.matrix-container {
  overflow-x: auto;
}

.mapping-matrix {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.mapping-matrix th,
.mapping-matrix td {
  border: 1px solid var(--border-color);
  padding: 10px;
  text-align: center;
}

.corner-cell {
  background: var(--bg-primary);
  font-weight: 600;
}

.po-header-cell {
  background: #d1fae5;
  font-weight: 600;
  color: #059669;
}

.lo-header-cell {
  background: #dbeafe;
  font-weight: 600;
  color: #2563eb;
  text-align: left;
}

.mapping-cell {
  background: white;
}

.mapping-cell.mapped {
  background: #f0fdf4;
}

.mapping-weight {
  font-weight: 600;
  color: #10b981;
}

.no-mapping {
  color: #d1d5db;
}

/* Loading & Error States */
.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .course-header-card {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .course-meta {
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
