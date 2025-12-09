<template>
  <div id="app">
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
          :class="['nav-item', { active: currentView === 'obs-mapping' }]" 
          @click="currentView = 'obs-mapping'">
          <span class="nav-icon">🎯</span>
          <span class="nav-text">OBS Mapping</span>
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
        <button class="action-btn" title="Notifications">
          <span class="icon">🔔</span>
          <span class="badge">3</span>
        </button>
        <div class="user-info">
          <div class="user-avatar">👤</div>
          <div class="user-name">Admin</div>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="content-area">
      <Dashboard v-if="currentView === 'dashboard'" />
      <CoursesView v-else-if="currentView === 'courses'" />
      <OutcomesView v-else-if="currentView === 'outcomes'" />
      <div v-else-if="currentView === 'editor'" class="editor-container">
        <ReteEditor />
      </div>
      <OBSMappingView v-else-if="currentView === 'obs-mapping'" />
      <StudentsView v-else-if="currentView === 'students'" />
      <ReportsView v-else-if="currentView === 'reports'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Dashboard from './components/Dashboard.vue'
import ReteEditor from './components/ReteEditor.vue'
import OBSMappingView from './components/OBSMappingView.vue'
import CoursesView from './components/CoursesView.vue'
import OutcomesView from './components/OutcomesView.vue'
import StudentsView from './components/StudentsView.vue'
import ReportsView from './components/ReportsView.vue'

const currentView = ref('dashboard')
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
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
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
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --sidebar-width: 260px;
  --sidebar-collapsed-width: 70px;
  --primary-color: #2563eb;
  --primary-dark: #1e40af;
  --secondary-color: #8b5cf6;
  --success-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --bg-primary: #f9fafb;
  --bg-secondary: #ffffff;
  --border-color: #e5e7eb;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  overflow-x: hidden;
}

#app {
  display: flex;
  min-height: 100vh;
}

/* Sidebar Styles */
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
  box-shadow: var(--shadow-md);
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  padding: 12px 8px; /* Padding azaltıldı */
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 60px; /* Yükseklik azaltıldı */
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px; /* Gap azaltıldı */
  font-weight: 700;
  font-size: 18px; /* Font size azaltıldı */
  color: var(--primary-color);
}

.logo-icon {
  font-size: 24px; /* Icon size azaltıldı */
}

.logo-text {
  white-space: nowrap;
  overflow: hidden;
}

.collapse-btn {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 16px;
}

.collapse-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.sidebar-nav {
  flex: 1;
  padding: 12px 6px; /* Padding azaltıldı */
  overflow-y: auto;
}

.nav-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px; /* Gap azaltıldı */
  padding: 10px 12px; /* Padding azaltıldı */
  margin-bottom: 4px; /* Margin azaltıldı */
  background: transparent;
  border: none;
  border-radius: 8px; /* Border radius azaltıldı */
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
  font-size: 14px; /* Font size azaltıldı */
  font-weight: 500;
  text-align: left;
}

.nav-item:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  box-shadow: var(--shadow-md);
}

.nav-item.active:hover {
  transform: translateX(0);
}

.nav-icon {
  font-size: 20px;
  min-width: 20px;
  text-align: center;
}

.nav-text {
  white-space: nowrap;
  overflow: hidden;
}

.sidebar.collapsed .nav-text {
  display: none;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px;
}

.sidebar-footer {
  padding: 12px 8px; /* Padding azaltıldı */
  border-top: 1px solid var(--border-color);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px; /* Gap azaltıldı */
}

.user-avatar {
  width: 36px; /* Boyut azaltıldı */
  height: 36px; /* Boyut azaltıldı */
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px; /* Icon size azaltıldı */
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Main Container */
.main-container {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

.main-container.expanded {
  margin-left: var(--sidebar-collapsed-width);
}

/* Top Bar */
.top-bar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 12px 16px; /* Padding azaltıldı */
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.page-title h1 {
  font-size: 22px; /* Font size azaltıldı */
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2px; /* Margin azaltıldı */
}

.page-subtitle {
  font-size: 13px; /* Font size azaltıldı */
  color: var(--text-secondary);
}

.top-bar-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  position: relative;
  width: 44px;
  height: 44px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 20px;
}

.action-btn:hover {
  background: var(--primary-color);
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.action-btn:hover .icon {
  filter: brightness(0) invert(1);
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--danger-color);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

/* Content Area */
.content-area {
  flex: 1;
  padding: 0; /* Boşluğu tamamen kaldır */
  overflow-y: auto;
  height: calc(100vh - 72px); /* Top bar height azaldı (24px padding -> 12px) */
}

.editor-container {
  background: white;
  border-radius: 0; /* Köşe yuvarlaklığını kaldır */
  box-shadow: var(--shadow-lg);
  height: calc(100vh - 72px); /* Full height - top bar height */
  overflow: auto; /* Yatay ve dikey scroll için */
  border: none; /* Border'ı kaldır */
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

/* Responsive - Tablet */
@media (max-width: 1024px) {
  .sidebar {
    width: var(--sidebar-collapsed-width);
  }
  
  .main-container {
    margin-left: var(--sidebar-collapsed-width);
  }
  
  .content-area {
    padding: 0;
  }
}

/* Responsive - Mobile */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    width: var(--sidebar-width);
  }
  
  .sidebar.active {
    transform: translateX(0);
  }
  
  .main-container {
    margin-left: 0;
  }
  
  .top-bar {
    padding: 10px 12px; /* Mobilde daha az padding */
  }
  
  .page-title h1 {
    font-size: 18px; /* Mobilde daha küçük */
  }
  
  .content-area {
    padding: 0;
  }
  
  .editor-container {
    height: calc(100vh - 60px); /* Mobile için optimize */
  }
}
</style>
