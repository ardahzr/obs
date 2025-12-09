<template>
  <svg data-testid="connection">
    <path :d="path" />
  </svg>
  <div class="weight-container" :style="{ transform: `translate(${position.x}px, ${position.y}px) translate(-50%, -50%)` }">
    <input 
      type="number" 
      v-model="weightValue" 
      @pointerdown.stop="" 
      @mousedown.stop=""
      class="weight-input"
      min="0"
      max="100"
    />
    <span class="percent">%</span>
  </div>
</template>

<script setup>
import { computed, inject, ref, watch } from 'vue'

const props = defineProps({
  data: Object,
  start: Object,
  end: Object,
  path: String
})

const injectedUpdate = inject('updateConnectionWeight', () => {});

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Wrapper to use callback from data or injected
const updateConnectionWeight = (id, weight, data) => {
  if (data.updateCallback) {
    data.updateCallback(id, weight, data);
  } else {
    injectedUpdate(id, weight, data);
  }
};

// Debounced update function with retry logic for missing dbId
const debouncedUpdate = debounce((dbId, weight, data) => {
  if (dbId) {
    updateConnectionWeight(dbId, weight, data);
  } else {
    // If dbId is missing (e.g. creation in progress), retry after delay
    setTimeout(() => {
      if (data.dbId) {
        updateConnectionWeight(data.dbId, weight, data);
      }
    }, 1000);
  }
}, 500);

const weightValue = computed({
  get() {
    if (!props.data) return 100;
    const val = props.data.weight !== undefined ? props.data.weight : 1.0;
    if (val > 1) return Math.round(val);
    return Math.round(val * 100);
  },
  set(value) {
    if (props.data) {
      const decimalValue = value / 100;
      props.data.weight = decimalValue;
      // Trigger auto-save with debounce
      debouncedUpdate(props.data.dbId, decimalValue, props.data);
    }
  }
})

const position = computed(() => {
  const { start, end } = props
  return {
    x: (start.x + end.x) / 2,
    y: (start.y + end.y) / 2
  }
})
</script>

<style scoped>
svg {
  overflow: visible !important;
  position: absolute;
  pointer-events: none;
  width: 9999px;
  height: 9999px;
  left: 0;
  top: 0;
  z-index: 1;
}

path {
  fill: none;
  stroke-width: 4px;
  stroke: #2196f3;
  pointer-events: auto;
}

.weight-container {
  position: absolute;
  padding: 4px 8px;
  background: white;
  border: 2px solid #2196f3;
  border-radius: 16px;
  font-size: 12px;
  display: flex;
  align-items: center;
  pointer-events: auto;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  z-index: 10;
  left: 0;
  top: 0;
  cursor: text;
}

.weight-input {
  width: 30px;
  border: none;
  outline: none;
  text-align: right;
  padding: 0;
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: #1565c0;
  background: transparent;
}

.percent {
  color: #1565c0;
  margin-left: 1px;
  font-weight: 700;
  font-size: 11px;
}

/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
input[type=number] {
  -moz-appearance: textfield;
  appearance: textfield;
}
</style>
