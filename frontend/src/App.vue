<template>
  <div id="app">
    <!-- Login sayfası - Giriş yapmamışsa göster -->
    <LoginView v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
    
    <!-- Ana uygulama - Giriş yapmışsa göster -->
    <template v-else>
      <!-- Top Navigation Bar -->
      <header class="top-navbar">
        <div class="navbar-left">
          <div class="logo">
            <span class="logo-icon">🎓</span>
            <span class="logo-text">PO Manager</span>
          </div>
        </div>
        
        <nav class="navbar-center">
          <button 
            :class="['nav-item', { active: currentView === 'dashboard' }]" 
            @click="currentView = 'dashboard'">
            <span class="nav-icon">📊</span>
            <span class="nav-text">Dashboard</span>
          </button>
          
          <button 
            :class="['nav-item', { active: currentView === 'courses' }]" 
            @click="currentView = 'courses'">
            <span class="nav-icon">📚</span>
            <span class="nav-text">Courses</span>
          </button>

          <button 
            :class="['nav-item', { active: currentView === 'learning-outcomes' }]" 
            @click="currentView = 'learning-outcomes'">
            <span class="nav-icon">📝</span>
            <span class="nav-text">Learning Outcomes</span>
          </button>
          
          <button 
            :class="['nav-item', { active: currentView === 'outcomes' }]" 
            @click="currentView = 'outcomes'">
            <span class="nav-icon">🎯</span>
            <span class="nav-text">Program Outcomes</span>
          </button>
          
          <button 
            :class="['nav-item', { active: currentView === 'editor' }]" 
            @click="currentView = 'editor'">
            <span class="nav-icon">🔗</span>
            <span class="nav-text">LO-PO Mapping</span>
          </button>
          
          <button 
            :class="['nav-item', { active: currentView === 'students' }]" 
            @click="currentView = 'students'">
            <span class="nav-icon">👥</span>
            <span class="nav-text">Students</span>
          </button>
          
          <button 
            :class="['nav-item', { active: currentView === 'reports' }]" 
            @click="currentView = 'reports'">
            <span class="nav-icon">📈</span>
            <span class="nav-text">Reports</span>
          </button>
        </nav>

        <div class="navbar-right">
          <div class="user-menu">
            <div class="user-info" @click="showUserMenu = !showUserMenu">
              <div class="user-avatar">{{ userInitials }}</div>
              <div class="user-details">
                <div class="user-name">{{ currentUser?.first_name || currentUser?.username }}</div>
                <div class="user-role">{{ currentUser?.user_type === 'admin' ? 'Admin' : 'Instructor' }}</div>
              </div>
              <span class="dropdown-arrow">▼</span>
            </div>
            <div v-if="showUserMenu" class="user-dropdown">
              <div class="dropdown-header">
                <strong>{{ currentUser?.first_name }} {{ currentUser?.last_name }}</strong>
                <small>@{{ currentUser?.username }}</small>
              </div>
              <button @click="handleLogout" class="logout-btn">
                <span>🚪</span> Çıkış Yap
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Content Area -->
      <main class="content-area">
        <Dashboard v-if="currentView === 'dashboard'" />
        <CoursesView 
          v-else-if="currentView === 'courses'" 
          @viewCourse="viewCourseDetails" 
        />
        <CourseDetailView 
          v-else-if="currentView === 'course-detail'" 
          :courseId="selectedCourseId" 
          @back="currentView = 'courses'"
          @openEditor="openEditorForCourse"
        />
        <LearningOutcomesView v-else-if="currentView === 'learning-outcomes'" />
        <OutcomesView v-else-if="currentView === 'outcomes'" />
        <div v-else-if="currentView === 'editor'" class="editor-container">
          <ReteEditor :preselectedCourse="preselectedCourseForEditor" />
        </div>
        <StudentsView v-else-if="currentView === 'students'" />
        <ReportsView v-else-if="currentView === 'reports'" />
      </main>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Dashboard from './components/Dashboard.vue'
import ReteEditor from './components/ReteEditor.vue'
import CoursesView from './components/CoursesView.vue'
import CourseDetailView from './components/CourseDetailView.vue'
import OutcomesView from './components/OutcomesView.vue'
import LearningOutcomesView from './components/LearningOutcomesView.vue'
import StudentsView from './components/StudentsView.vue'
import ReportsView from './components/ReportsView.vue'
import LoginView from './components/LoginView.vue'
import api from './services/api'

const currentView = ref('dashboard')
const selectedCourseId = ref(null)
const preselectedCourseForEditor = ref(null)
const isAuthenticated = ref(false)
const currentUser = ref(null)
const showUserMenu = ref(false)

const userInitials = computed(() => {
  if (currentUser.value?.first_name && currentUser.value?.last_name) {
    return currentUser.value.first_name[0] + currentUser.value.last_name[0]
  }
  return currentUser.value?.username?.[0]?.toUpperCase() || '?'
})

const handleDocumentClick = (e) => {
  if (!e.target.closest('.user-menu')) {
    showUserMenu.value = false
  }
}

// Sayfa yüklendiğinde token kontrolü
onMounted(() => {
  const token = localStorage.getItem('token')
  const user = localStorage.getItem('user')
  
  if (token && user) {
    isAuthenticated.value = true
    currentUser.value = JSON.parse(user)
  }

  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})

const handleLoginSuccess = (user) => {
  isAuthenticated.value = true
  currentUser.value = user
}

const handleLogout = async () => {
  try {
    const token = localStorage.getItem('token')
    if (token) {
      await api.logout(token)
    }
  } catch (err) {
    console.error('Logout error:', err)
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    isAuthenticated.value = false
    currentUser.value = null
    showUserMenu.value = false
  }
}

function viewCourseDetails(courseId) {
  selectedCourseId.value = courseId
  currentView.value = 'course-detail'
}

function openEditorForCourse(courseId) {
  preselectedCourseForEditor.value = courseId
  currentView.value = 'editor'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary-color: #2563eb;
  --primary-dark: #1e40af;
  --secondary-color: #8b5cf6;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --bg-primary: #f9fafb;
  --bg-secondary: #ffffff;
  --border-color: #e5e7eb;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --navbar-height: 56px;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  overflow-x: hidden;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Top Navbar */
.top-navbar {
  height: var(--navbar-height);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-left {
  display: flex;
  align-items: center;
  min-width: 200px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 18px;
  color: var(--primary-color);
}

.logo-icon {
  font-size: 24px;
}

.navbar-center {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
}

.nav-item:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.nav-item.active {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  box-shadow: var(--shadow-sm);
}

.nav-icon {
  font-size: 16px;
}

.nav-text {
  font-size: 13px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
  justify-content: flex-end;
}

.action-btn {
  position: relative;
  width: 36px;
  height: 36px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 18px;
}

.action-btn:hover {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.action-btn:hover .icon {
  filter: brightness(0) invert(1);
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-info:hover {
  background: var(--bg-primary);
}

.user-menu {
  position: relative;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-role {
  font-size: 11px;
  color: var(--text-secondary);
}

.dropdown-arrow {
  font-size: 10px;
  color: var(--text-secondary);
  margin-left: 4px;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  overflow: hidden;
  z-index: 1001;
}

.dropdown-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-header strong {
  font-size: 14px;
  color: var(--text-primary);
}

.dropdown-header small {
  font-size: 12px;
  color: var(--text-secondary);
}

.logout-btn {
  width: 100%;
  padding: 12px 16px;
  background: none;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #ef4444;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: #fef2f2;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Content Area */
.content-area {
  flex: 1;
  padding: 0;
  overflow: auto;
  height: calc(100vh - var(--navbar-height));
}

.editor-container {
  background: white;
  height: calc(100vh - var(--navbar-height));
  overflow: auto;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Responsive */
@media (max-width: 1024px) {
  .nav-text {
    display: none;
  }
  
  .nav-item {
    padding: 8px;
  }
  
  .user-name {
    display: none;
  }
}

@media (max-width: 768px) {
  .navbar-center {
    gap: 2px;
  }
  
  .nav-item {
    padding: 6px;
  }
  
  .logo-text {
    display: none;
  }
}
</style>
