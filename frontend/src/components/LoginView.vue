<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <span class="logo-icon">🎓</span>
          <span class="logo-text">PO Manager</span>
        </div>
        <p class="login-subtitle">Program Outcome Management System</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Kullanıcı Adı</label>
          <div class="input-wrapper">
            <span class="input-icon">👤</span>
            <input 
              type="text" 
              id="username" 
              v-model="username" 
              placeholder="Kullanıcı adınızı girin"
              required
              :disabled="loading"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Şifre</label>
          <div class="input-wrapper">
            <span class="input-icon">🔒</span>
            <input 
              :type="showPassword ? 'text' : 'password'" 
              id="password" 
              v-model="password" 
              placeholder="Şifrenizi girin"
              required
              :disabled="loading"
            />
            <button 
              type="button" 
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div v-if="error" class="error-message">
          <span class="error-icon">⚠️</span>
          {{ error }}
        </div>

        <!-- reCAPTCHA Widget -->
        <div class="recaptcha-container">
          <div id="recaptcha-widget"></div>
        </div>

        <button type="submit" class="login-btn" :disabled="loading || !recaptchaToken">
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>Giriş Yap</span>
        </button>
      </form>

      <div class="login-footer">
        <p>Hesabınız yok mu? Sistem yöneticisiyle iletişime geçin.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, onMounted } from 'vue'
import api from '../services/api'

const emit = defineEmits(['login-success'])

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const recaptchaToken = ref('')

// reCAPTCHA Site Key
const RECAPTCHA_SITE_KEY = '6LffcTksAAAAAIB8PWS-uqaXDZ2bV1P6Lmr--0AO'

// Load reCAPTCHA script
onMounted(() => {
  loadRecaptchaScript()
})

const loadRecaptchaScript = () => {
  if (document.getElementById('recaptcha-script')) {
    renderRecaptcha()
    return
  }
  
  const script = document.createElement('script')
  script.id = 'recaptcha-script'
  script.src = 'https://www.google.com/recaptcha/api.js?onload=onRecaptchaLoad&render=explicit'
  script.async = true
  script.defer = true
  
  // Define global callback
  window.onRecaptchaLoad = () => {
    renderRecaptcha()
  }
  
  document.head.appendChild(script)
}

const renderRecaptcha = () => {
  if (window.grecaptcha && document.getElementById('recaptcha-widget')) {
    window.grecaptcha.render('recaptcha-widget', {
      sitekey: RECAPTCHA_SITE_KEY,
      callback: onRecaptchaSuccess,
      'expired-callback': onRecaptchaExpired,
      theme: 'dark'
    })
  }
}

const onRecaptchaSuccess = (token) => {
  recaptchaToken.value = token
}

const onRecaptchaExpired = () => {
  recaptchaToken.value = ''
}

const resetRecaptcha = () => {
  if (window.grecaptcha) {
    window.grecaptcha.reset()
  }
  recaptchaToken.value = ''
}

const handleLogin = async () => {
  error.value = ''
  
  if (!recaptchaToken.value) {
    error.value = 'Lütfen reCAPTCHA doğrulamasını tamamlayın'
    return
  }
  
  loading.value = true

  try {
    const response = await api.login(username.value, password.value, recaptchaToken.value)

    if (response.data.success) {
      // Token'ı localStorage'a kaydet
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      // Ana uygulamaya bildir
      emit('login-success', response.data.user)
    } else {
      error.value = response.data.message || 'Giriş başarısız'
      resetRecaptcha()
    }
  } catch (err) {
    console.error('Login error:', err)
    if (err.response?.data?.message) {
      if (typeof err.response.data.message === 'object') {
        error.value = Object.values(err.response.data.message).flat().join(', ')
      } else {
        error.value = err.response.data.message
      }
    } else {
      error.value = 'Bağlantı hatası. Lütfen tekrar deneyin.'
    }
    resetRecaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 20px;
}

.login-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.login-header {
  text-align: center;
  margin-bottom: 35px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 10px;
}

.logo-icon {
  font-size: 2.5rem;
}

.logo-text {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 15px;
  font-size: 1.1rem;
  z-index: 1;
}

.input-wrapper input {
  width: 100%;
  padding: 14px 45px 14px 45px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #60a5fa;
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2);
}

.input-wrapper input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input-wrapper input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 5px;
  transition: transform 0.2s;
}

.toggle-password:hover {
  transform: scale(1.1);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 15px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #fca5a5;
  font-size: 0.9rem;
}

.error-icon {
  font-size: 1.1rem;
}

/* reCAPTCHA Container */
.recaptcha-container {
  display: flex;
  justify-content: center;
  margin: 15px 0;
}

.recaptcha-container > div {
  transform: scale(0.95);
  transform-origin: center;
}

.login-btn {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.login-footer {
  margin-top: 25px;
  text-align: center;
}

.login-footer p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  margin: 0;
}
</style>
