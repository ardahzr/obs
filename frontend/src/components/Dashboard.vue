<template>
  <div class="dashboard">
    <h2>Program Outcome Manager Dashboard</h2>
    
    <div class="dashboard-tabs">
      <button 
        :class="['tab', { active: activeTab === 'courses' }]" 
        @click="activeTab = 'courses'">
        Dersler
      </button>
      <button 
        :class="['tab', { active: activeTab === 'po' }]" 
        @click="activeTab = 'po'">
        Program Outcomes
      </button>
      <button 
        :class="['tab', { active: activeTab === 'students' }]" 
        @click="activeTab = 'students'">
        Öğrenciler
      </button>
      <button 
        :class="['tab', { active: activeTab === 'mapping' }]" 
        @click="activeTab = 'mapping'">
        LO-PO Mapping
      </button>
    </div>

    <!-- Dersler Tab -->
    <div v-if="activeTab === 'courses'" class="tab-content">
      <div class="content-header">
        <h3>Dersler</h3>
        <button @click="showCourseForm = !showCourseForm" class="btn btn-primary">
          {{ showCourseForm ? 'İptal' : '+ Yeni Ders' }}
        </button>
      </div>
      
      <div v-if="showCourseForm" class="form-card">
        <h4>Yeni Ders Ekle</h4>
        <form @submit.prevent="createCourse">
          <input v-model="newCourse.code" placeholder="Ders Kodu (örn: CSE311)" required>
          <input v-model="newCourse.name" placeholder="Ders Adı" required>
          <input v-model="newCourse.semester" placeholder="Dönem (örn: 2024-Fall)">
          <button type="submit" class="btn btn-success">Kaydet</button>
        </form>
      </div>

      <div class="courses-grid">
        <div v-for="course in courses" :key="course.id" class="card">
          <h4>{{ course.code }}</h4>
          <p>{{ course.name }}</p>
          <span class="badge">{{ course.semester || 'Dönem belirtilmemiş' }}</span>
        </div>
      </div>
    </div>

    <!-- Program Outcomes Tab -->
    <div v-if="activeTab === 'po'" class="tab-content">
      <div class="content-header">
        <h3>Program Outcomes</h3>
        <button @click="showPOForm = !showPOForm" class="btn btn-primary">
          {{ showPOForm ? 'İptal' : '+ Yeni PO' }}
        </button>
      </div>

      <div v-if="showPOForm" class="form-card">
        <h4>Yeni Program Outcome Ekle</h4>
        <form @submit.prevent="createPO">
          <input v-model="newPO.code" placeholder="PO Kodu (örn: PO1)" required>
          <textarea v-model="newPO.description" placeholder="Açıklama" required></textarea>
          <button type="submit" class="btn btn-success">Kaydet</button>
        </form>
      </div>

      <div class="po-list">
        <div v-for="po in programOutcomes" :key="po.id" class="card po-card">
          <div class="po-header">
            <h4>{{ po.code }}</h4>
          </div>
          <p>{{ po.description }}</p>
        </div>
      </div>
    </div>

    <!-- Öğrenciler Tab -->
    <div v-if="activeTab === 'students'" class="tab-content">
      <h3>Öğrenciler ve PO Skorları</h3>
      
      <div v-if="students.length === 0" class="empty-state">
        <p>Henüz öğrenci kaydı yok.</p>
      </div>

      <div class="students-grid">
        <div v-for="student in students" :key="student.id" class="card student-card">
          <h4>{{ student.student_no }}</h4>
          <p v-if="student.user_info">
            {{ student.user_info.first_name }} {{ student.user_info.last_name }}
          </p>
          <button @click="viewStudentPO(student.id)" class="btn btn-info">
            PO Skorlarını Gör
          </button>
        </div>
      </div>

      <!-- Student PO Modal -->
      <div v-if="selectedStudentPO" class="modal-overlay" @click="selectedStudentPO = null">
        <div class="modal-content" @click.stop>
          <h3>{{ selectedStudentPO.student }} - PO Skorları</h3>
          <div class="po-scores">
            <div v-for="score in selectedStudentPO.po_scores" :key="score.po_code" class="score-item">
              <div class="score-header">
                <strong>{{ score.po_code }}</strong>
                <span class="score-value">{{ score.score }}%</span>
              </div>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: score.score + '%' }"></div>
              </div>
              <p class="score-desc">{{ score.po_description }}</p>
            </div>
          </div>
          <button @click="selectedStudentPO = null" class="btn btn-secondary">Kapat</button>
        </div>
      </div>
    </div>

    <!-- LO-PO Mapping Tab -->
    <div v-if="activeTab === 'mapping'" class="tab-content">
      <h3>Learning Outcome ↔ Program Outcome Mapping</h3>
      <p class="info-text">
        Aşağıdaki editörde LO ve PO arasında bağlantı kurabilirsiniz.
      </p>
      <div class="mapping-stats">
        <div class="stat-card">
          <h4>{{ learningOutcomes.length }}</h4>
          <p>Learning Outcomes</p>
        </div>
        <div class="stat-card">
          <h4>{{ programOutcomes.length }}</h4>
          <p>Program Outcomes</p>
        </div>
        <div class="stat-card">
          <h4>{{ mappings.length }}</h4>
          <p>Toplam Mapping</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const activeTab = ref('courses')
const courses = ref([])
const programOutcomes = ref([])
const learningOutcomes = ref([])
const students = ref([])
const mappings = ref([])

const showCourseForm = ref(false)
const showPOForm = ref(false)
const selectedStudentPO = ref(null)

const newCourse = ref({
  code: '',
  name: '',
  semester: '',
  department: 'CSE'
})

const newPO = ref({
  code: '',
  description: ''
})

async function loadData() {
  try {
    const [coursesRes, posRes, losRes, studentsRes, mappingsRes] = await Promise.all([
      api.getCourses(),
      api.getProgramOutcomes(),
      api.getLearningOutcomes(),
      api.getStudents(),
      api.getMappings()
    ])
    
    courses.value = coursesRes.data
    programOutcomes.value = posRes.data
    learningOutcomes.value = losRes.data
    students.value = studentsRes.data
    mappings.value = mappingsRes.data
  } catch (error) {
    console.error('Veri yükleme hatası:', error)
  }
}

async function createCourse() {
  try {
    await api.createCourse(newCourse.value)
    alert('Ders başarıyla oluşturuldu!')
    newCourse.value = { code: '', name: '', semester: '', department: 'CSE' }
    showCourseForm.value = false
    await loadData()
  } catch (error) {
    console.error('Ders oluşturma hatası:', error)
    alert('Ders oluşturulamadı!')
  }
}

async function createPO() {
  try {
    await api.createProgramOutcome(newPO.value)
    alert('Program Outcome başarıyla oluşturuldu!')
    newPO.value = { code: '', description: '' }
    showPOForm.value = false
    await loadData()
  } catch (error) {
    console.error('PO oluşturma hatası:', error)
    alert('PO oluşturulamadı!')
  }
}

async function viewStudentPO(studentId) {
  try {
    const response = await api.getStudentPOScores(studentId)
    selectedStudentPO.value = response.data
  } catch (error) {
    console.error('PO skorları yüklenirken hata:', error)
    alert('PO skorları yüklenemedi!')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 15px;
  max-width: 1400px;
  margin: 0 auto;
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: clamp(20px, 5vw, 28px);
}

h3 {
  font-size: clamp(18px, 4vw, 24px);
}

.dashboard-tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 20px;
  border-bottom: 2px solid #ddd;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

.dashboard-tabs::-webkit-scrollbar {
  height: 4px;
}

.dashboard-tabs::-webkit-scrollbar-thumb {
  background: #3498db;
  border-radius: 2px;
}

.tab {
  padding: 12px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.3s;
  color: #666;
  white-space: nowrap;
  flex-shrink: 0;
}

.tab:hover {
  color: #3498db;
}

.tab.active {
  border-bottom-color: #3498db;
  color: #3498db;
  font-weight: 600;
}

.tab-content {
  padding: 20px 0;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.form-card form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-card input,
.form-card textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-card textarea {
  min-height: 80px;
  resize: vertical;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-success {
  background: #2ecc71;
  color: white;
}

.btn-success:hover {
  background: #27ae60;
}

.btn-info {
  background: #9b59b6;
  color: white;
  padding: 8px 16px;
  font-size: 12px;
}

.btn-info:hover {
  background: #8e44ad;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.courses-grid,
.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.card h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  background: #ecf0f1;
  border-radius: 12px;
  font-size: 12px;
  color: #7f8c8d;
  margin-top: 8px;
}

.po-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.po-card {
  border-left: 4px solid #e74c3c;
}

.po-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.student-card {
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #95a5a6;
}

.info-text {
  color: #7f8c8d;
  margin-bottom: 20px;
}

.mapping-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
}

.stat-card h4 {
  font-size: 36px;
  margin: 0 0 8px 0;
}

.stat-card p {
  margin: 0;
  opacity: 0.9;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 15px;
}

.modal-content {
  background: white;
  padding: 25px;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.po-scores {
  margin: 20px 0;
}

.score-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.score-value {
  font-size: 20px;
  font-weight: bold;
  color: #3498db;
}

.score-bar {
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s;
}

.score-desc {
  font-size: 12px;
  color: #7f8c8d;
  margin: 8px 0 0 0;
}

/* Mobil Responsive */
@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  h2 {
    font-size: 22px;
    margin-bottom: 15px;
  }
  
  .dashboard-tabs {
    gap: 3px;
    margin-bottom: 15px;
  }
  
  .tab {
    padding: 10px 15px;
    font-size: 13px;
  }
  
  .content-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .content-header .btn {
    width: 100%;
  }
  
  .courses-grid,
  .students-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .mapping-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-card h4 {
    font-size: 28px;
  }
  
  .form-card {
    padding: 15px;
  }
  
  .modal-content {
    padding: 20px;
    max-height: 90vh;
  }
  
  .po-scores {
    margin: 15px 0;
  }
  
  .score-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .score-value {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .dashboard {
    padding: 8px;
  }
  
  h2 {
    font-size: 20px;
  }
  
  .tab {
    padding: 8px 12px;
    font-size: 12px;
  }
  
  .card {
    padding: 15px;
  }
  
  .btn {
    padding: 8px 16px;
    font-size: 13px;
  }
}
</style>
