import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  }
})

// API servis fonksiyonları
export default {
  // Courses
  getCourses() {
    return api.get('courses/')
  },
  getCourse(id) {
    return api.get(`courses/${id}/`)
  },
  getCourseDetail(id) {
    return api.get(`courses/${id}/detail/`)
  },
  createCourse(data) {
    return api.post('courses/', data)
  },
  deleteCourse(id) {
    return api.delete(`courses/${id}/`)
  },
  
  // Program Outcomes
  getProgramOutcomes() {
    return api.get('program-outcomes/')
  },
  createProgramOutcome(data) {
    return api.post('program-outcomes/', data)
  },
  updateProgramOutcome(id, data) {
    return api.patch(`program-outcomes/${id}/`, data)
  },
  deleteProgramOutcome(id) {
    return api.delete(`program-outcomes/${id}/`)
  },
  
  // Learning Outcomes
  getLearningOutcomes() {
    return api.get('learning-outcomes/')
  },
  getLearningOutcome(id) {
    return api.get(`learning-outcomes/${id}/`)
  },
  createLearningOutcome(data) {
    return api.post('learning-outcomes/', data)
  },
  updateLearningOutcome(id, data) {
    return api.patch(`learning-outcomes/${id}/`, data)
  },
  deleteLearningOutcome(id) {
    return api.delete(`learning-outcomes/${id}/`)
  },
  getLOMappings(loId) {
    return api.get(`learning-outcomes/${loId}/mappings/`)
  },
  createLOMapping(loId, data) {
    return api.post(`learning-outcomes/${loId}/mappings/`, data)
  },
  
  // LO to PO Mappings
  getMappings() {
    return api.get('mappings/')
  },
  getLoToPoMappings() {
    return api.get('mappings/')
  },
  createMapping(data) {
    return api.post('mappings/', data)
  },
  createLoToPoMapping(data) {
    return api.post('mappings/', data)
  },
  updateMapping(id, data) {
    return api.patch(`mappings/${id}/`, data)
  },
  deleteMapping(id) {
    return api.delete(`mappings/${id}/`)
  },
  
  // Students
  getStudents() {
    return api.get('students/')
  },
  getStudent(id) {
    return api.get(`students/${id}/`)
  },
  createStudent(data) {
    return api.post('students/', data)
  },
  getStudentPOScores(studentId) {
    return api.get(`students/${studentId}/po_scores/`)
  },
  getStudentPoScores(studentId) {
    return api.get(`students/${studentId}/po_scores/`)
  },
  
  // Assessments
  getAssessments() {
    return api.get('assessments/')
  },
  createAssessment(data) {
    return api.post('assessments/', data)
  },
  
  // Assessment to LO Mappings
  getAssessmentToLoMappings() {
    return api.get('assessment-to-lo-mappings/')
  },
  createAssessmentToLoMapping(data) {
    return api.post('assessment-to-lo-mappings/', data)
  },
  updateAssessmentToLoMapping(id, data) {
    return api.patch(`assessment-to-lo-mappings/${id}/`, data)
  },
  deleteAssessmentToLoMapping(id) {
    return api.delete(`assessment-to-lo-mappings/${id}/`)
  },
  
  // Grades
  getGrades() {
    return api.get('grades/')
  },
  createGrade(data) {
    return api.post('grades/', data)
  },
  
  // Chat
  chatWithGemini(message) {
    return api.post('chat/', { message })
  }
}
