<template>
  <div class="reports-view">
    <!-- Header -->
    <div class="view-header">
      <div class="header-left">
        <h2>📊 Reports & AI Analytics</h2>
        <p class="subtitle">Comprehensive program outcome analysis with AI-powered insights</p>
      </div>
      <div class="header-actions">
        <button @click="refreshData" class="btn-secondary" :disabled="loading">
          <span>🔄</span> Refresh
        </button>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="stats-overview">
      <div class="stat-card stat-courses">
        <div class="stat-icon">🎓</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalCourses }}</div>
          <div class="stat-label">Total Courses</div>
        </div>
      </div>
      <div class="stat-card stat-pos">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalPOs }}</div>
          <div class="stat-label">Program Outcomes</div>
        </div>
      </div>
      <div class="stat-card stat-los">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalLOs }}</div>
          <div class="stat-label">Learning Outcomes</div>
        </div>
      </div>
      <div class="stat-card stat-students">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalStudents }}</div>
          <div class="stat-label">Students</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="main-grid">
      <!-- Left Side - Reports -->
      <div class="reports-section">
        <!-- Quick Report Actions -->
        <div class="quick-actions-card">
          <h3>📥 Quick Report Downloads</h3>
          <div class="action-grid">
            <button @click="downloadAllCoursesReport" class="action-btn" :disabled="generatingReport">
              <span class="action-icon">📑</span>
              <span class="action-text">All Courses Report</span>
              <span class="action-desc">Complete course analysis</span>
            </button>
            <button @click="downloadPOAnalysisReport" class="action-btn" :disabled="generatingReport">
              <span class="action-icon">🎯</span>
              <span class="action-text">PO Analysis Report</span>
              <span class="action-desc">Program outcomes breakdown</span>
            </button>
            <button @click="downloadStudentPerformanceReport" class="action-btn" :disabled="generatingReport">
              <span class="action-icon">👥</span>
              <span class="action-text">Student Performance</span>
              <span class="action-desc">All students overview</span>
            </button>
            <button @click="showCustomReportModal = true" class="action-btn custom">
              <span class="action-icon">⚙️</span>
              <span class="action-text">Custom Report</span>
              <span class="action-desc">Build your own report</span>
            </button>
          </div>
        </div>

        <!-- PO Coverage Report -->
        <div class="report-card">
          <div class="report-header">
            <h3>🎯 PO Coverage Analysis</h3>
            <span class="report-badge live">Live</span>
          </div>
          <div class="report-content">
            <div v-if="poReport.length === 0" class="empty-state">
              <span>No program outcomes found</span>
            </div>
            <div v-else>
              <div v-for="po in poReport" :key="po.id" class="coverage-item">
                <div class="coverage-header">
                  <span class="coverage-label">{{ po.id }}</span>
                  <span class="coverage-stats">
                    <span class="mapping-count">{{ po.mappingCount }} mappings</span>
                    <span class="coverage-percent">{{ getCoveragePercentage(po.mappingCount) }}%</span>
                  </span>
                </div>
                <div class="coverage-bar">
                  <div 
                    class="coverage-fill" 
                    :style="{ width: getCoveragePercentage(po.mappingCount) + '%', background: getCoverageColor(getCoveragePercentage(po.mappingCount)) }"
                  ></div>
                </div>
                <p class="po-description">{{ po.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Course Distribution -->
        <div class="report-card">
          <div class="report-header">
            <h3>📚 Course Distribution</h3>
            <button @click="downloadSelectedCourseReport" class="btn-sm" :disabled="!selectedCourseForReport">
              📥 Download Selected
            </button>
          </div>
          <div class="report-content">
            <div v-for="course in courseReport" :key="course.id" class="distribution-item" 
                 :class="{ selected: selectedCourseForReport === course.id }"
                 @click="selectedCourseForReport = course.id">
              <div class="distribution-info">
                <span class="course-code">{{ course.code }}</span>
                <span class="course-name">{{ course.name }}</span>
              </div>
              <div class="distribution-stats">
                <span class="stat-pill lo">{{ course.loCount }} LOs</span>
                <span class="stat-pill assessment">{{ course.assessmentCount }} Assessments</span>
                <span class="stat-pill student">{{ course.studentCount }} Students</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - AI Assistant -->
      <div class="ai-section">
        <div class="ai-assistant-card">
          <div class="ai-header">
            <div class="ai-avatar">
              <span>🤖</span>
            </div>
            <div class="ai-info">
              <h3>AI Analytics Assistant</h3>
              <p>Powered by Gemini AI</p>
            </div>
            <div class="ai-status" :class="{ online: !isLoading }">
              {{ isLoading ? 'Thinking...' : 'Online' }}
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="ai-quick-actions">
            <button v-for="action in quickActions" :key="action.id" 
                    @click="executeQuickAction(action)"
                    class="quick-action-btn"
                    :disabled="isLoading">
              <span class="qa-icon">{{ action.icon }}</span>
              <span class="qa-text">{{ action.label }}</span>
            </button>
          </div>

          <!-- Chat Messages -->
          <div class="ai-messages" ref="messagesContainer">
            <div v-for="(msg, index) in messages" :key="index" :class="['ai-message', msg.role]">
              <div class="message-avatar">
                {{ msg.role === 'user' ? '👤' : '🤖' }}
              </div>
              <div class="message-bubble">
                <div class="message-content" v-html="formatMessage(msg.content)"></div>
                <div class="message-time">{{ msg.time }}</div>
              </div>
            </div>
            <div v-if="isLoading" class="ai-message assistant">
              <div class="message-avatar">🤖</div>
              <div class="message-bubble">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="ai-input-area">
            <div class="input-suggestions" v-if="showSuggestions">
              <button v-for="suggestion in inputSuggestions" :key="suggestion" 
                      @click="useSuggestion(suggestion)"
                      class="suggestion-btn">
                {{ suggestion }}
              </button>
            </div>
            <div class="ai-input">
              <button @click="showSuggestions = !showSuggestions" class="suggest-btn" title="Show suggestions">
                💡
              </button>
              <input 
                v-model="userMessage" 
                @keyup.enter="sendMessage"
                @focus="showSuggestions = false"
                placeholder="Ask me about reports, statistics, or analysis..."
                :disabled="isLoading"
              />
              <button @click="sendMessage" :disabled="isLoading || !userMessage.trim()" class="send-btn">
                <span v-if="isLoading">⏳</span>
                <span v-else>➤</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Report Modal -->
    <div v-if="showCustomReportModal" class="modal-overlay" @click="showCustomReportModal = false">
      <div class="modal-content custom-report-modal" @click.stop>
        <div class="modal-header">
          <h3>⚙️ Custom Report Builder</h3>
          <button @click="showCustomReportModal = false" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="report-options">
            <h4>Select Report Type</h4>
            <div class="option-group">
              <label class="option-item">
                <input type="radio" v-model="customReport.type" value="course" />
                <span class="option-label">📚 Course Report</span>
              </label>
              <label class="option-item">
                <input type="radio" v-model="customReport.type" value="student" />
                <span class="option-label">👤 Student Report</span>
              </label>
              <label class="option-item">
                <input type="radio" v-model="customReport.type" value="po" />
                <span class="option-label">🎯 PO Analysis</span>
              </label>
            </div>

            <div v-if="customReport.type === 'course'" class="selection-group">
              <h4>Select Course</h4>
              <select v-model="customReport.courseId" class="select-input">
                <option :value="null">-- Select a course --</option>
                <option v-for="course in courseReport" :key="course.id" :value="course.id">
                  {{ course.code }} - {{ course.name }}
                </option>
              </select>
            </div>

            <div v-if="customReport.type === 'student'" class="selection-group">
              <h4>Select Student</h4>
              <select v-model="customReport.studentId" class="select-input">
                <option :value="null">-- Select a student --</option>
                <option v-for="student in allStudents" :key="student.id" :value="student.id">
                  {{ student.student_no }} - {{ student.user?.first_name }} {{ student.user?.last_name }}
                </option>
              </select>
              <div class="checkbox-group">
                <label>
                  <input type="checkbox" v-model="customReport.allCourses" />
                  Include all enrolled courses
                </label>
              </div>
            </div>

            <div class="include-options">
              <h4>Include in Report</h4>
              <div class="checkbox-group">
                <label>
                  <input type="checkbox" v-model="customReport.includePOScores" />
                  PO Scores
                </label>
                <label>
                  <input type="checkbox" v-model="customReport.includeGrades" />
                  Assessment Grades
                </label>
                <label>
                  <input type="checkbox" v-model="customReport.includeMappings" />
                  LO-PO Mappings
                </label>
                <label>
                  <input type="checkbox" v-model="customReport.includeStatistics" />
                  Statistical Summary
                </label>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCustomReportModal = false" class="btn-secondary">Cancel</button>
          <button @click="generateCustomReport" class="btn-primary" :disabled="!canGenerateCustomReport">
            📥 Generate Report
          </button>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="generatingReport" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>Generating report...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import api from '../services/api'

// State
const loading = ref(false)
const generatingReport = ref(false)
const stats = ref({
  totalCourses: 0,
  totalPOs: 0,
  totalLOs: 0,
  totalStudents: 0
})

const poReport = ref([])
const courseReport = ref([])
const allStudents = ref([])
const selectedCourseForReport = ref(null)

// AI Chat State
const messages = ref([
  { 
    role: 'assistant', 
    content: `👋 Hello! I'm your **AI Analytics Assistant**. I can help you with:

• 📊 **Analyzing** program outcome statistics
• 📈 **Generating** custom reports
• 🔍 **Finding** specific student or course data
• 💡 **Providing** insights and recommendations

Try clicking one of the quick actions below or ask me anything!`,
    time: getCurrentTime()
  }
])
const userMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const showSuggestions = ref(false)

// Quick Actions
const quickActions = ref([
  { id: 'overview', icon: '📊', label: 'System Overview', prompt: 'Give me an overview of the current system statistics including total courses, students, and PO coverage.' },
  { id: 'top-students', icon: '🏆', label: 'Top Performers', prompt: 'Who are the top performing students based on their PO scores? List the top 5 with their average scores.' },
  { id: 'weak-pos', icon: '⚠️', label: 'Weak POs', prompt: 'Which program outcomes have the lowest coverage or need more attention? Identify POs with fewer mappings.' },
  { id: 'recommendations', icon: '💡', label: 'Recommendations', prompt: 'Based on the current data, what recommendations do you have to improve program outcome coverage and student performance?' },
  { id: 'course-analysis', icon: '📚', label: 'Course Analysis', prompt: 'Analyze the courses and their learning outcome distributions. Which courses have the most comprehensive LO coverage?' },
  { id: 'export-help', icon: '📥', label: 'Export Help', prompt: 'How can I export reports? What types of reports are available and what do they include?' }
])

const inputSuggestions = ref([
  'Compare PO scores across courses',
  'Show students below 60% average',
  'Which LOs contribute most to PO1?',
  'Generate summary for this semester',
  'Find unmapped learning outcomes',
  'Calculate class average for each PO'
])

// Custom Report State
const showCustomReportModal = ref(false)
const customReport = ref({
  type: 'course',
  courseId: null,
  studentId: null,
  allCourses: true,
  includePOScores: true,
  includeGrades: true,
  includeMappings: true,
  includeStatistics: true
})

const canGenerateCustomReport = computed(() => {
  if (customReport.value.type === 'course' && !customReport.value.courseId) return false
  if (customReport.value.type === 'student' && !customReport.value.studentId) return false
  return true
})

// Functions
function getCurrentTime() {
  return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

async function loadReports() {
  loading.value = true
  try {
    const [coursesRes, posRes, losRes, studentsRes, mappingsRes, assessmentsRes] = await Promise.all([
      api.getCourses(),
      api.getProgramOutcomes(),
      api.getLearningOutcomes(),
      api.getStudents(),
      api.getLoToPoMappings(),
      api.getAssessments()
    ])

    const courses = coursesRes.data.results || coursesRes.data
    const pos = posRes.data.results || posRes.data
    const los = losRes.data.results || losRes.data
    const students = studentsRes.data.results || studentsRes.data
    const mappings = mappingsRes.data.results || mappingsRes.data
    const assessments = assessmentsRes.data.results || assessmentsRes.data

    allStudents.value = students

    // Update stats
    stats.value = {
      totalCourses: courses.length,
      totalPOs: pos.length,
      totalLOs: los.length,
      totalStudents: students.length
    }

    // PO Report with mapping counts
    poReport.value = pos.map(po => ({
      id: po.code,
      description: po.description,
      mappingCount: mappings.filter(m => m.program_outcome === po.id).length
    }))

    // Course Report with detailed stats
    courseReport.value = courses.map(course => {
      const courseLOs = los.filter(lo => lo.course == course.id)
      const courseAssessments = assessments.filter(a => a.course == course.id)
      
      return {
        id: course.id,
        code: course.code,
        name: course.name,
        loCount: courseLOs.length,
        assessmentCount: courseAssessments.length,
        studentCount: 0
      }
    })

  } catch (error) {
    console.error('Error loading reports:', error)
  } finally {
    loading.value = false
  }
}

function getCoveragePercentage(count) {
  const maxMappings = Math.max(...poReport.value.map(po => po.mappingCount), 1)
  return Math.round((count / maxMappings) * 100)
}

function getCoverageColor(percentage) {
  if (percentage >= 80) return 'linear-gradient(90deg, #10b981, #34d399)'
  if (percentage >= 50) return 'linear-gradient(90deg, #3b82f6, #60a5fa)'
  if (percentage >= 25) return 'linear-gradient(90deg, #f59e0b, #fbbf24)'
  return 'linear-gradient(90deg, #ef4444, #f87171)'
}

function formatMessage(content) {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
    .replace(/• /g, '&bull; ')
}

async function refreshData() {
  await loadReports()
  messages.value.push({
    role: 'assistant',
    content: '🔄 Data refreshed! All statistics are now up to date.',
    time: getCurrentTime()
  })
  scrollToBottom()
}

// Report Download Functions
async function downloadSelectedCourseReport() {
  if (!selectedCourseForReport.value) return
  
  generatingReport.value = true
  try {
    const response = await api.downloadCourseReport(selectedCourseForReport.value)
    downloadBlob(response.data, `course_report.xlsx`)
    
    messages.value.push({
      role: 'assistant',
      content: '✅ Course report downloaded successfully!',
      time: getCurrentTime()
    })
  } catch (error) {
    console.error('Error downloading report:', error)
    alert('Failed to download report')
  } finally {
    generatingReport.value = false
  }
}

async function downloadAllCoursesReport() {
  generatingReport.value = true
  try {
    for (const course of courseReport.value) {
      const response = await api.downloadCourseReport(course.id)
      downloadBlob(response.data, `${course.code}_report.xlsx`)
    }
    
    messages.value.push({
      role: 'assistant',
      content: `✅ Downloaded reports for all ${courseReport.value.length} courses!`,
      time: getCurrentTime()
    })
  } catch (error) {
    console.error('Error downloading reports:', error)
    alert('Failed to download some reports')
  } finally {
    generatingReport.value = false
  }
}

async function downloadPOAnalysisReport() {
  messages.value.push({
    role: 'user',
    content: 'Generate a PO Analysis Report',
    time: getCurrentTime()
  })
  
  await sendContextualMessage(`Please provide a detailed analysis of all Program Outcomes. Include:
    - Current PO coverage statistics: ${JSON.stringify(poReport.value)}
    - Total courses: ${stats.value.totalCourses}
    - Total LOs: ${stats.value.totalLOs}
    - Recommendations for improving coverage`)
}

async function downloadStudentPerformanceReport() {
  generatingReport.value = true
  try {
    const students = allStudents.value.slice(0, 10)
    for (const student of students) {
      const response = await api.downloadStudentReport(student.id)
      downloadBlob(response.data, `${student.student_no}_report.xlsx`)
    }
    
    messages.value.push({
      role: 'assistant',
      content: `✅ Downloaded performance reports for ${students.length} students!`,
      time: getCurrentTime()
    })
  } catch (error) {
    console.error('Error downloading reports:', error)
  } finally {
    generatingReport.value = false
  }
}

async function generateCustomReport() {
  generatingReport.value = true
  showCustomReportModal.value = false
  
  try {
    if (customReport.value.type === 'course' && customReport.value.courseId) {
      const response = await api.downloadCourseReport(customReport.value.courseId)
      const course = courseReport.value.find(c => c.id === customReport.value.courseId)
      downloadBlob(response.data, `${course?.code || 'course'}_custom_report.xlsx`)
    } else if (customReport.value.type === 'student' && customReport.value.studentId) {
      const courseId = customReport.value.allCourses ? null : customReport.value.courseId
      const response = await api.downloadStudentReport(customReport.value.studentId, courseId)
      const student = allStudents.value.find(s => s.id === customReport.value.studentId)
      downloadBlob(response.data, `${student?.student_no || 'student'}_custom_report.xlsx`)
    }
    
    messages.value.push({
      role: 'assistant',
      content: '✅ Custom report generated and downloaded successfully!',
      time: getCurrentTime()
    })
  } catch (error) {
    console.error('Error generating custom report:', error)
    alert('Failed to generate custom report')
  } finally {
    generatingReport.value = false
  }
}

function downloadBlob(data, filename) {
  const blob = new Blob([data], { 
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
  })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

// AI Chat Functions
async function executeQuickAction(action) {
  messages.value.push({
    role: 'user',
    content: action.label,
    time: getCurrentTime()
  })
  scrollToBottom()
  
  await sendContextualMessage(action.prompt)
}

function useSuggestion(suggestion) {
  userMessage.value = suggestion
  showSuggestions.value = false
}

async function sendMessage() {
  if (!userMessage.value.trim() || isLoading.value) return
  
  const text = userMessage.value
  messages.value.push({ role: 'user', content: text, time: getCurrentTime() })
  userMessage.value = ''
  scrollToBottom()
  
  await sendContextualMessage(text)
}

async function sendContextualMessage(userPrompt) {
  isLoading.value = true
  
  const context = `
You are an AI assistant for a Program Outcome (PO) Management System. You have access to the following current data:

**System Statistics:**
- Total Courses: ${stats.value.totalCourses}
- Total Program Outcomes: ${stats.value.totalPOs}
- Total Learning Outcomes: ${stats.value.totalLOs}
- Total Students: ${stats.value.totalStudents}

**PO Coverage Data:**
${poReport.value.map(po => `- ${po.id}: ${po.mappingCount} mappings (${po.description?.substring(0, 50)}...)`).join('\n')}

**Courses:**
${courseReport.value.map(c => `- ${c.code}: ${c.name} (${c.loCount} LOs, ${c.assessmentCount} assessments)`).join('\n')}

Based on this data, please respond to the following user query in a helpful and informative way. Use markdown formatting for better readability (bold, bullet points, etc.):

User Query: ${userPrompt}
`

  try {
    const response = await api.chatWithGemini(context)
    messages.value.push({ 
      role: 'assistant', 
      content: response.data.response,
      time: getCurrentTime()
    })
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({ 
      role: 'assistant', 
      content: '❌ Sorry, I encountered an error processing your request. Please try again.',
      time: getCurrentTime()
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.reports-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
}

/* Header */
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
  gap: 12px;
}

.btn-secondary {
  background: white;
  color: var(--text-primary);
  padding: 12px 24px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
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
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled, .btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.stat-card.stat-courses .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-card.stat-pos .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-card.stat-los .stat-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-card.stat-students .stat-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.stat-icon {
  font-size: 32px;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 450px;
  gap: 24px;
}

/* Reports Section */
.reports-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Quick Actions Card */
.quick-actions-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid var(--border-color);
}

.quick-actions-card h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-btn {
  background: var(--bg-primary);
  border: 2px solid transparent;
  border-radius: 12px;
  padding: 20px 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.action-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  background: white;
  transform: translateY(-2px);
}

.action-btn.custom {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.action-icon {
  font-size: 32px;
}

.action-text {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.action-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Report Cards */
.report-card {
  background: white;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.report-header h3 {
  font-size: 18px;
  color: var(--text-primary);
}

.report-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.report-badge.live {
  background: #dcfce7;
  color: #16a34a;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.report-content {
  padding: 20px 24px;
  max-height: 400px;
  overflow-y: auto;
}

/* Coverage Items */
.coverage-item {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.coverage-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.coverage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.coverage-label {
  font-weight: 700;
  color: var(--primary-color);
  font-size: 15px;
}

.coverage-stats {
  display: flex;
  gap: 12px;
  font-size: 13px;
}

.mapping-count {
  color: var(--text-secondary);
}

.coverage-percent {
  font-weight: 600;
  color: var(--text-primary);
}

.coverage-bar {
  height: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.coverage-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.po-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin: 0;
}

/* Distribution Items */
.distribution-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.distribution-item:hover {
  background: white;
  border-color: var(--border-color);
}

.distribution-item.selected {
  border-color: var(--primary-color);
  background: rgba(102, 126, 234, 0.05);
}

.distribution-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.course-code {
  font-weight: 700;
  color: var(--primary-color);
}

.course-name {
  font-size: 14px;
  color: var(--text-primary);
}

.distribution-stats {
  display: flex;
  gap: 8px;
}

.stat-pill {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.stat-pill.lo { background: #dbeafe; color: #1d4ed8; }
.stat-pill.assessment { background: #fef3c7; color: #b45309; }
.stat-pill.student { background: #dcfce7; color: #16a34a; }

/* AI Section */
.ai-section {
  position: sticky;
  top: 24px;
  height: fit-content;
}

.ai-assistant-card {
  background: white;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.ai-avatar {
  width: 50px;
  height: 50px;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.ai-info h3 {
  font-size: 18px;
  margin-bottom: 2px;
}

.ai-info p {
  font-size: 12px;
  opacity: 0.9;
}

.ai-status {
  margin-left: auto;
  padding: 6px 12px;
  background: rgba(255,255,255,0.2);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.ai-status.online::before {
  content: '●';
  color: #4ade80;
  margin-right: 6px;
}

/* Quick Actions */
.ai-quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.quick-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qa-icon {
  font-size: 20px;
}

.qa-text {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
}

/* AI Messages */
.ai-messages {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f9fafb;
}

.ai-message {
  display: flex;
  gap: 12px;
  max-width: 90%;
}

.ai-message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.ai-message.user .message-avatar {
  background: var(--primary-color);
}

.message-bubble {
  background: white;
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.ai-message.user .message-bubble {
  background: var(--primary-color);
  color: white;
  border: none;
}

.message-content {
  font-size: 14px;
  line-height: 1.5;
}

.message-content :deep(strong) {
  font-weight: 600;
}

.message-content :deep(code) {
  background: rgba(0,0,0,0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.message-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 6px;
  text-align: right;
}

.ai-message.user .message-time {
  color: rgba(255,255,255,0.7);
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--text-secondary);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* Input Area */
.ai-input-area {
  border-top: 1px solid var(--border-color);
  background: white;
}

.input-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.suggestion-btn {
  padding: 6px 12px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.ai-input {
  display: flex;
  gap: 8px;
  padding: 16px;
  align-items: center;
}

.suggest-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: var(--bg-primary);
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.2s;
}

.suggest-btn:hover {
  background: var(--border-color);
}

.ai-input input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.ai-input input:focus {
  border-color: var(--primary-color);
}

.send-btn {
  width: 44px;
  height: 44px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  background: var(--secondary-color);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 20px;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--bg-primary);
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.report-options h4 {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  background: var(--border-color);
}

.option-item input[type="radio"] {
  width: 18px;
  height: 18px;
}

.option-label {
  font-weight: 500;
}

.selection-group {
  margin-bottom: 24px;
}

.select-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  cursor: pointer;
}

.select-input:focus {
  border-color: var(--primary-color);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 14px;
}

.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
}

.include-options {
  background: var(--bg-primary);
  padding: 16px;
  border-radius: 12px;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-content p {
  font-size: 16px;
  color: var(--text-secondary);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .ai-section {
    position: static;
  }
  
  .action-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .ai-quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
