<template>
  <div class="description-control" @pointerdown.stop="" @mousedown.stop="">
    <div class="description-title">Description</div>
    <div class="description-text">{{ data.description }}</div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.description-control {
  /* Visibility handled by parent component based on selection */
  position: absolute;
  top: 50%;
  left: 100%;
  transform: translateY(-50%);
  width: 250px;
  background: white;
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
  z-index: 1000;
  margin-left: 12px;
  text-align: left;
  pointer-events: none; /* Let clicks pass through if needed, but we stop propagation on container */
}

.description-control::before {
  content: '';
  position: absolute;
  top: 50%;
  left: -6px;
  transform: translateY(-50%);
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-right: 6px solid white;
}

.description-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: #333;
  margin-bottom: 4px;
  border-bottom: 1px solid #eee;
  padding-bottom: 4px;
}

.description-text {
  font-size: 0.8rem;
  color: #555;
  line-height: 1.4;
  white-space: pre-wrap;
}

/* Show when parent node is selected */
:global(.node.selected) .description-control {
  display: block;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, -10px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>
