<template>
  <div class="reports-view">
    <div class="view-header">
      <div class="header-left">
        <h2>Reports & Analytics</h2>
        <p class="subtitle">View comprehensive program outcome statistics and reports</p>
      </div>
      <button @click="exportReport" class="btn-primary">
        <span class="icon">📊</span> Export Report
      </button>
    </div>

    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon">🎓</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalCourses }}</div>
          <div class="stat-label">Total Courses</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalPOs }}</div>
          <div class="stat-label">Program Outcomes</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalLOs }}</div>
          <div class="stat-label">Learning Outcomes</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalStudents }}</div>
          <div class="stat-label">Students</div>
        </div>
      </div>
    </div>

    <div class="reports-grid">
      <!-- PO Coverage Report -->
      <div class="report-card">
        <div class="report-header">
          <h3>PO Coverage Analysis</h3>
          <span class="report-badge">Updated</span>
        </div>
        <div class="report-content">
          <div v-for="po in poReport" :key="po.id" class="coverage-item">
            <div class="coverage-header">
              <span class="coverage-label">{{ po.id }}</span>
              <span class="coverage-count">{{ po.mappingCount }} mappings</span>
            </div>
            <div class="coverage-bar">
              <div 
                class="coverage-fill" 
                :style="{ width: getCoveragePercentage(po.mappingCount) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Course Distribution -->
      <div class="report-card">
        <div class="report-header">
          <h3>Course Distribution</h3>
          <span class="report-badge">Live</span>
        </div>
        <div class="report-content">
          <div v-for="course in courseReport" :key="course.id" class="distribution-item">
            <div class="distribution-info">
              <span class="course-code">{{ course.code }}</span>
              <span class="course-name">{{ course.name }}</span>
            </div>
            <div class="distribution-stats">
              <span class="stat-pill">{{ course.learning_outcomes ? course.learning_outcomes.length : 0 }} LOs</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Performance -->
      <div class="report-card full-width">
        <div class="report-header">
          <h3>Student Performance Overview</h3>
          <span class="report-badge">Summary</span>
        </div>
        <div class="report-content">
          <div class="performance-grid">
            <div v-for="student in studentReport" :key="student.id" class="performance-card">
              <div class="performance-header">
                <div class="student-avatar-sm">
                  {{ getInitials(student.first_name, student.last_name) }}
                </div>
                <div>
                  <div class="student-name-sm">{{ student.first_name }} {{ student.last_name }}</div>
                  <div class="student-number-sm">{{ student.student_no }}</div>
                </div>
              </div>
              <div class="performance-score">
                <div class="score-circle" :class="getPerformanceClass(student.avgScore)">
                  {{ student.avgScore ? student.avgScore.toFixed(1) : 'N/A' }}
                </div>
                <div class="score-label">Avg Score</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Widget -->
    <div class="chat-widget" :class="{ open: chatOpen }">
      <div class="chat-header" @click="toggleChat">
        <div class="chat-title">
          <span class="icon">🤖</span> AI Assistant
        </div>
        <button class="close-btn" @click.stop="toggleChat">
          {{ chatOpen ? '−' : '+' }}
        </button>
      </div>
      
      <div class="chat-body" v-show="chatOpen">
        <div class="messages-container" ref="messagesContainer">
          <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
            <div class="message-content">{{ msg.content }}</div>
          </div>
          <div v-if="isLoading" class="message assistant">
            <div class="message-content typing">Thinking...</div>
          </div>
        </div>
        
        <div class="chat-input">
          <input 
            v-model="userMessage" 
            @keyup.enter="sendMessage"
            placeholder="Ask about PO stats..."
            :disabled="isLoading"
          />
          <button @click="sendMessage" :disabled="isLoading || !userMessage.trim()">
            ➤
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import api from '../services/api'

const stats = ref({
  totalCourses: 0,
  totalPOs: 0,
  totalLOs: 0,
  totalStudents: 0
})

const poReport = ref([])
const courseReport = ref([])
const studentReport = ref([])

const chatOpen = ref(false)
const messages = ref([
  { role: 'assistant', content: 'Hello! I can help you analyze the Program Outcome statistics. Ask me anything!' }
])
const userMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)

async function loadReports() {
  try {
    const [coursesRes, posRes, losRes, studentsRes, mappingsRes] = await Promise.all([
      api.getCourses(),
      api.getProgramOutcomes(),
      api.getLearningOutcomes(),
      api.getStudents(),
      api.getLoToPoMappings()
    ])

    const courses = coursesRes.data.results || coursesRes.data
    const pos = posRes.data.results || posRes.data
    const los = losRes.data.results || losRes.data
    const students = studentsRes.data.results || studentsRes.data
    const mappings = mappingsRes.data.results || mappingsRes.data

    // Update stats
    stats.value = {
      totalCourses: courses.length,
      totalPOs: pos.length,
      totalLOs: los.length,
      totalStudents: students.length
    }

    // PO Report with mapping counts
    poReport.value = pos.map(po => ({
      id: po.code, // Use code for display
      description: po.description,
      mappingCount: mappings.filter(m => m.program_outcome === po.id).length
    }))

    // Course Report with LO counts
    courseReport.value = courses.map(course => ({
      id: course.id,
      code: course.code,
      name: course.name,
      // Ensure type safety when comparing IDs (string vs number)
      loCount: los.filter(lo => lo.course == course.id).length
    }))

    // Student Report (Show up to 20 students)
    // We will fetch PO scores for these students
    const sampleStudents = students.slice(0, 20)
    const studentPromises = sampleStudents.map(s => api.getStudentPOScores(s.id))
    const studentScoresRes = await Promise.all(studentPromises)
    
    studentReport.value = sampleStudents.map((student, index) => {
      const scores = studentScoresRes[index].data.po_scores
      const avgScore = scores.length > 0 
        ? scores.reduce((sum, s) => sum + s.score, 0) / scores.length 
        : 0
      
      return {
        id: student.id,
        first_name: student.user.first_name,
        last_name: student.user.last_name,
        student_no: student.student_no,
        avgScore: avgScore
      }
    })

  } catch (error) {
    console.error('Error loading reports:', error)
  }
}

function getCoveragePercentage(count) {
  const maxMappings = Math.max(...poReport.value.map(po => po.mappingCount), 1)
  return (count / maxMappings) * 100
}

function getInitials(firstName, lastName) {
  return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase()
}

function getPerformanceClass(score) {
  if (!score) return 'score-na'
  if (score >= 80) return 'score-excellent'
  if (score >= 60) return 'score-good'
  if (score >= 40) return 'score-fair'
  return 'score-poor'
}

function exportReport() {
  alert('Export functionality coming soon!')
}

function toggleChat() {
  chatOpen.value = !chatOpen.value
  if (chatOpen.value) {
    scrollToBottom()
  }
}

async function sendMessage() {
  if (!userMessage.value.trim() || isLoading.value) return
  
  const text = userMessage.value
  messages.value.push({ role: 'user', content: text })
  userMessage.value = ''
  isLoading.value = true
  scrollToBottom()
  
  try {
    const response = await api.chatWithGemini(text)
    messages.value.push({ role: 'assistant', content: response.data.response })
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({ role: 'assistant', content: 'Sorry, I encountered an error processing your request.' })
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

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  font-size: 40px;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.report-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.report-card.full-width {
  grid-column: 1 / -1;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.report-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.report-badge {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.report-content {
  padding: 24px;
}

.coverage-item {
  margin-bottom: 16px;
}

.coverage-item:last-child {
  margin-bottom: 0;
}

.coverage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.coverage-label {
  font-weight: 600;
  color: var(--text-primary);
}

.coverage-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.coverage-bar {
  height: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
  overflow: hidden;
}

.coverage-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  transition: width 0.3s ease;
  border-radius: 4px;
}

.distribution-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
  margin-bottom: 12px;
}

.distribution-item:last-child {
  margin-bottom: 0;
}

.distribution-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.course-code {
  font-weight: 700;
  color: var(--primary-color);
  font-size: 14px;
}

.course-name {
  font-size: 16px;
  color: var(--text-primary);
}

.stat-pill {
  background: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.performance-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.performance-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.student-avatar-sm {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.student-name-sm {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.student-number-sm {
  font-size: 12px;
  color: var(--text-secondary);
}

.performance-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.score-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.score-excellent { background: #10b981; }
.score-good { background: #3b82f6; }
.score-fair { background: #f59e0b; }
.score-poor { background: #ef4444; }
.score-na { background: #9ca3af; }

.score-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Chat Widget Styles */
.chat-widget {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 350px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.chat-widget:not(.open) {
  height: 60px;
  width: 200px;
  cursor: pointer;
}

.chat-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.chat-title {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

.chat-body {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #f9fafb;
}

.message {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
}

.message.assistant {
  align-self: flex-start;
  background: white;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.message.user {
  align-self: flex-end;
  background: var(--primary-color);
  color: white;
  border-bottom-right-radius: 4px;
}

.typing {
  color: var(--text-secondary);
  font-style: italic;
  font-size: 12px;
}

.chat-input {
  padding: 12px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 8px;
  background: white;
}

.chat-input input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  outline: none;
  font-size: 14px;
  transition: border-color 0.2s;
}

.chat-input input:focus {
  border-color: var(--primary-color);
}

.chat-input button {
  background: var(--primary-color);
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.chat-input button:hover:not(:disabled) {
  transform: scale(1.05);
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .reports-grid {
    grid-template-columns: 1fr;
  }
  
  .performance-grid {
    grid-template-columns: 1fr;
  }
}
</style>
