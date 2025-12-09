<template>
  <div class="mapping-editor">
    <div class="editor-header">
      <div class="header-left">
        <button @click="showForms = !showForms" class="btn-toggle">
          {{ showForms ? '◀' : '▶' }} {{ showForms ? 'Hide' : 'Show' }} Forms
        </button>
        <h2>LO-PO Mapping Editor</h2>
      </div>
      <div class="header-actions">
        <select v-model="selectedCourse" class="course-select">
          <option value="">Select Course</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.code }} - {{ course.name }}
          </option>
        </select>
      </div>
    </div>

    <div class="editor-content">
      <!-- Forms Panel - Collapsible -->
      <div class="forms-panel" v-if="selectedCourse && showForms">
        <div class="form-section">
          <h3>Create Assessment</h3>
          <form @submit.prevent="createAssessment">
            <input v-model="newAssessment.name" placeholder="Name (e.g., Midterm)" required class="form-input" />
            <select v-model="newAssessment.type" class="form-input">
              <option value="midterm">Midterm</option>
              <option value="final">Final</option>
              <option value="project">Project</option>
              <option value="quiz">Quiz</option>
              <option value="homework">Homework</option>
            </select>
            <input v-model.number="newAssessment.points" type="number" placeholder="Points" required class="form-input" />
            <button type="submit" class="btn-create">+ Create Assessment</button>
          </form>
        </div>

        <div class="form-section">
          <h3>Create Learning Outcome</h3>
          <form @submit.prevent="createLearningOutcome">
            <input v-model="newLO.code" placeholder="Code (e.g., LO-1)" required class="form-input" />
            <textarea v-model="newLO.description" placeholder="Description" required class="form-textarea"></textarea>
            <button type="submit" class="btn-create">+ Create LO</button>
          </form>
        </div>
        
        <div class="form-section">
          <h3>Create Program Outcome</h3>
          <form @submit.prevent="createProgramOutcome">
            <input v-model="newPO.code" placeholder="Code (e.g., PO-1)" required class="form-input" />
            <textarea v-model="newPO.description" placeholder="Description" required class="form-textarea"></textarea>
            <button type="submit" class="btn-create">+ Create PO</button>
          </form>
        </div>
      </div>

      <!-- Rete.js Editor Canvas -->
      <div ref="reteContainer" class="rete-container"></div>
    </div>

    <div v-if="!selectedCourse" class="empty-state">
      <p>📚 Please select a course to start mapping Learning Outcomes to Program Outcomes</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, provide } from 'vue';
import { NodeEditor, ClassicPreset } from 'rete';
import { AreaPlugin } from 'rete-area-plugin';
import { ConnectionPlugin, Presets as ConnectionPresets } from 'rete-connection-plugin';
import { VuePlugin, Presets as VuePresets } from 'rete-vue-plugin';
import { AreaExtensions } from 'rete-area-plugin';
import api from '@/services/api';
import CustomConnection from './Connection.vue';
import DescriptionControl from './DescriptionControl.vue';

const reteContainer = ref(null);
const selectedCourse = ref('');
const courses = ref([]);
const learningOutcomes = ref([]);
const programOutcomes = ref([]);
const assessments = ref([]);
const mappings = ref([]);
const assessmentMappings = ref([]);
const showForms = ref(false); // Forms başlangıçta gizli

const newLO = ref({ code: '', description: '' });
const newPO = ref({ code: '', description: '' });
const newAssessment = ref({ name: '', type: 'midterm', points: 100 });
const isRendering = ref(false);

let editor = null;
let area = null;
let connection = null;

// Custom socket for connections
class MappingSocket extends ClassicPreset.Socket {
  constructor(name) {
    super(name);
  }
  
  isCompatibleWith(socket) {
    return socket instanceof MappingSocket;
  }
}

const mappingSocket = new MappingSocket('mapping');

// Custom Control for Description
class DescriptionControlImpl extends ClassicPreset.Control {
  constructor(description) {
    super();
    this.description = description;
  }
}

// Assessment Node
class AssessmentNode extends ClassicPreset.Node {
  width = 220;
  height = 130;
  
  constructor(assessment) {
    super('Assessment');
    this.assessmentData = assessment;
    
    this.addOutput('assess-out', new ClassicPreset.Output(mappingSocket, 'Connect to LO'));
    this.addControl('info', new ClassicPreset.InputControl('text', { 
      initial: assessment.name,
      readonly: true 
    }));
  }
}

// Learning Outcome Node
class LONode extends ClassicPreset.Node {
  width = 220;
  height = 190;
  
  constructor(lo) {
    super('Learning Outcome');
    this.loData = lo;
    
    this.addInput('lo-in', new ClassicPreset.Input(mappingSocket, 'From Assessment', true));
    this.addOutput('lo-out', new ClassicPreset.Output(mappingSocket, 'Connect to PO'));
    this.addControl('info', new ClassicPreset.InputControl('text', { 
      initial: lo.code,
      readonly: true 
    }));
    this.addControl('description', new DescriptionControlImpl(lo.description));
  }
}

// Program Outcome Node
class PONode extends ClassicPreset.Node {
  width = 220;
  height = 160;
  
  constructor(po) {
    super('Program Outcome');
    this.poData = po;
    this.addInput('po-in', new ClassicPreset.Input(mappingSocket, 'From LO', true)); // Allow multiple connections
    this.addControl('info', new ClassicPreset.InputControl('text', { 
      initial: po.code,
      readonly: true 
    }));
    this.addControl('description', new DescriptionControlImpl(po.description));
  }
}

// Custom Connection with weight
class WeightedConnection extends ClassicPreset.Connection {
  weight = 1.0;
  dbId = null;
  
  constructor(source, sourceOutput, target, targetInput, weight = 1.0, dbId = null) {
    super(source, sourceOutput, target, targetInput);
    this.weight = weight;
    this.dbId = dbId;
  }
}

// Initialize Rete editor
async function initializeEditor() {
  if (!reteContainer.value) return;

  const container = reteContainer.value;
  
  // Create editor
  editor = new NodeEditor({
    nodes: [AssessmentNode, LONode, PONode],
    connections: [WeightedConnection]
  });

  // Auto-save pipe
  editor.addPipe(context => {
    if (context.type === 'connectioncreated') {
      // Attach update callback to connection instance for child component access
      context.data.updateCallback = updateConnectionWeight;
      
      if (!isRendering.value) {
        handleConnectionCreated(context.data);
      }
    }
    if (context.type === 'connectionremoved') {
      if (!isRendering.value) {
        handleConnectionRemoved(context.data);
      }
    }
    return context;
  });

  // Create area
  area = new AreaPlugin(container);
  
  // Add pipe to apply classes to nodes based on label
  area.addPipe(context => {
    if (context.type === 'render' && context.data.type === 'node') {
      const node = context.data.payload;
      const element = context.data.element;
      if (element) {
        const cls = node.label.toLowerCase().replace(/\s+/g, '-');
        element.classList.add(cls);
      }
    }
    return context;
  });
  
  // Create connection plugin - allow multiple connections to same input
  connection = new ConnectionPlugin();
  
  // Use standard classic preset
  connection.addPreset(ConnectionPresets.classic.setup());

  // Create Vue render plugin
  const render = new VuePlugin();
  render.addPreset(VuePresets.classic.setup({
    customize: {
      connection() {
        return CustomConnection;
      },
      control(data) {
        if (data.payload instanceof DescriptionControlImpl) {
          return DescriptionControl;
        }
        if (data.payload instanceof ClassicPreset.InputControl) {
          return VuePresets.classic.Control;
        }
      }
    }
  }));

  // Register plugins
  editor.use(area);
  area.use(connection);
  area.use(render);

  // Enable node selection
  AreaExtensions.selectableNodes(area, AreaExtensions.selector(), {
    accumulating: AreaExtensions.accumulateOnCtrl()
  });

  // Fit viewport to content
  AreaExtensions.zoomAt(area, editor.getNodes());
}

// Load course data and render nodes
async function loadCourseData() {
  if (!selectedCourse.value) return;

  // Prevent auto-save from deleting mappings during clear/reload
  isRendering.value = true;

  try {
    // Fetch data
    const [losRes, posRes, mapsRes, assessRes, assessMapsRes] = await Promise.all([
      api.getLearningOutcomes(),
      api.getProgramOutcomes(),
      api.getLoToPoMappings(),
      api.getAssessments(),
      api.getAssessmentToLoMappings()
    ]);

    learningOutcomes.value = losRes.data.filter(lo => lo.course == selectedCourse.value);
    programOutcomes.value = posRes.data;
    mappings.value = mapsRes.data;
    assessments.value = assessRes.data.filter(a => a.course == selectedCourse.value);
    assessmentMappings.value = assessMapsRes.data;

    // Clear editor completely - connections first, then nodes
    if (editor) {
      // Remove all connections first
      const connections = editor.getConnections();
      for (const conn of connections) {
        await editor.removeConnection(conn.id);
      }
      
      // Then remove all nodes
      const nodes = editor.getNodes();
      for (const node of nodes) {
        await editor.removeNode(node.id);
      }
    }

    // Render nodes
    await renderNodes();
  } catch (error) {
    console.error('Error loading course data:', error);
    alert('Failed to load course data');
    isRendering.value = false;
  }
}

// Render LO and PO nodes - left to right flow
async function renderNodes() {
  if (!editor || !area) return;
  
  isRendering.value = true;

  const assessNodes = [];
  const loNodes = [];
  const poNodes = [];

  const verticalSpacing = 200; // Dikey aralık
  const horizontalGap = 700; // Sütunlar arası yatay mesafe
  const startY = 100; // Başlangıç Y pozisyonu
  
  // Create Assessment nodes (sol taraf)
  for (let i = 0; i < assessments.value.length; i++) {
    const assess = assessments.value[i];
    const node = new AssessmentNode(assess);
    await editor.addNode(node);
    await area.translate(node.id, { x: 100, y: startY + i * verticalSpacing });
    assessNodes.push({ node, assess });
  }

  // Create LO nodes (orta)
  for (let i = 0; i < learningOutcomes.value.length; i++) {
    const lo = learningOutcomes.value[i];
    const node = new LONode(lo);
    await editor.addNode(node);
    await area.translate(node.id, { x: 100 + horizontalGap, y: startY + i * verticalSpacing });
    loNodes.push({ node, lo });
  }

  // Create PO nodes (sağ taraf)
  for (let i = 0; i < programOutcomes.value.length; i++) {
    const po = programOutcomes.value[i];
    const node = new PONode(po);
    await editor.addNode(node);
    await area.translate(node.id, { x: 100 + horizontalGap * 2, y: startY + i * verticalSpacing });
    poNodes.push({ node, po });
  }

  // Create connections for Assessment -> LO
  for (const mapping of assessmentMappings.value) {
    const assessNode = assessNodes.find(an => an.assess.id === mapping.assessment);
    const loNode = loNodes.find(ln => ln.lo.id === mapping.learning_outcome);
    
    if (assessNode && loNode) {
      const weight = mapping.contribution_weight !== undefined ? mapping.contribution_weight : (mapping.weight !== undefined ? mapping.weight : 0);
      const conn = new WeightedConnection(
        assessNode.node,
        'assess-out',
        loNode.node,
        'lo-in',
        weight,
        mapping.id
      );
      conn.updateCallback = updateConnectionWeight;
      await editor.addConnection(conn);
    }
  }

  // Create connections for LO -> PO
  for (const mapping of mappings.value) {
    const loNode = loNodes.find(ln => ln.lo.id === mapping.learning_outcome);
    const poNode = poNodes.find(pn => pn.po.id === mapping.program_outcome);
    
    if (loNode && poNode) {
      const weight = mapping.contribution_weight !== undefined ? mapping.contribution_weight : (mapping.weight !== undefined ? mapping.weight : 1.0);
      const conn = new WeightedConnection(
        loNode.node,
        'lo-out',
        poNode.node,
        'po-in',
        weight,
        mapping.id
      );
      conn.updateCallback = updateConnectionWeight;
      await editor.addConnection(conn);
    }
  }

  // Fit viewport
  AreaExtensions.zoomAt(area, editor.getNodes());
  
  isRendering.value = false;
}

// Create Assessment
async function createAssessment() {
  if (!selectedCourse.value) {
    alert('Please select a course first');
    return;
  }

  try {
    const response = await api.createAssessment({
      course: selectedCourse.value,
      name: newAssessment.value.name,
      assessment_type: newAssessment.value.type,
      total_points: newAssessment.value.points
    });

    const assess = response.data;
    assessments.value.push(assess);

    // Add node to editor (sol taraf)
    const node = new AssessmentNode(assess);
    await editor.addNode(node);
    const verticalSpacing = 200;
    const startY = 100;
    await area.translate(node.id, { 
      x: 100, 
      y: startY + (assessments.value.length - 1) * verticalSpacing 
    });

    // Reset form
    newAssessment.value = { name: '', type: 'midterm', points: 100 };
    
    alert('Assessment created successfully!');
  } catch (error) {
    console.error('Error creating Assessment:', error);
    alert('Failed to create Assessment');
  }
}

// Create Learning Outcome
async function createLearningOutcome() {
  if (!selectedCourse.value) {
    alert('Please select a course first');
    return;
  }

  try {
    const response = await api.createLearningOutcome({
      course: selectedCourse.value,
      code: newLO.value.code,
      description: newLO.value.description
    });

    const lo = response.data;
    learningOutcomes.value.push(lo);

    // Add node to editor (orta sütun)
    const node = new LONode(lo);
    await editor.addNode(node);
    const verticalSpacing = 200;
    const horizontalGap = 700;
    const startY = 100;
    await area.translate(node.id, { 
      x: 100 + horizontalGap, 
      y: startY + (learningOutcomes.value.length - 1) * verticalSpacing 
    });

    // Reset form
    newLO.value = { code: '', description: '' };
    
    alert('Learning Outcome created successfully!');
  } catch (error) {
    console.error('Error creating LO:', error);
    alert('Failed to create Learning Outcome');
  }
}

// Create Program Outcome
async function createProgramOutcome() {
  try {
    const response = await api.createProgramOutcome({
      code: newPO.value.code,
      description: newPO.value.description
    });

    const po = response.data;
    programOutcomes.value.push(po);

    // Add node to editor (sağ taraf, dikey sırada)
    const node = new PONode(po);
    await editor.addNode(node);
    const verticalSpacing = 200;
    const horizontalGap = 700;
    const startY = 100;
    await area.translate(node.id, { 
      x: 100 + horizontalGap * 2, 
      y: startY + (programOutcomes.value.length - 1) * verticalSpacing 
    });

    // Reset form
    newPO.value = { code: '', description: '' };
    
    alert('Program Outcome created successfully!');
  } catch (error) {
    console.error('Error creating PO:', error);
    alert('Failed to create Program Outcome');
  }
}

// Save all mappings
async function saveAllMappings() {
  if (!editor) return;

  try {
    const connections = editor.getConnections();
    const nodes = editor.getNodes();

    // Map node IDs to data IDs
    const assessNodeMap = new Map();
    const loNodeMap = new Map();
    const poNodeMap = new Map();

    for (const node of nodes) {
      if (node instanceof AssessmentNode) {
        assessNodeMap.set(node.id, node.assessmentData.id);
      } else if (node instanceof LONode) {
        loNodeMap.set(node.id, node.loData.id);
      } else if (node instanceof PONode) {
        poNodeMap.set(node.id, node.poData.id);
      }
    }

    // Create mapping requests
    const mappingPromises = connections.map(conn => {
      const sourceId = conn.source;
      const targetId = conn.target;
      
      // Assessment -> LO
      if (assessNodeMap.has(sourceId) && loNodeMap.has(targetId)) {
        return api.createAssessmentToLoMapping({
          assessment: assessNodeMap.get(sourceId),
          learning_outcome: loNodeMap.get(targetId),
          contribution_weight: conn.weight || 0
        });
      }

      // LO -> PO
      if (loNodeMap.has(sourceId) && poNodeMap.has(targetId)) {
        return api.createLoToPoMapping({
          learning_outcome: loNodeMap.get(sourceId),
          program_outcome: poNodeMap.get(targetId),
          weight: conn.weight || 1.0
        });
      }
      return null;
    }).filter(p => p !== null);

    await Promise.all(mappingPromises);
    
    alert('All mappings saved successfully!');
    await loadCourseData(); // Reload to sync
  } catch (error) {
    console.error('Error saving mappings:', error);
    alert('Failed to save mappings');
  }
}

// Auto-save handlers
async function handleConnectionCreated(connection) {
  const sourceNode = editor.getNode(connection.source);
  const targetNode = editor.getNode(connection.target);
  
  if (!sourceNode || !targetNode) return;

  try {
    let response;
    // Assessment -> LO
    if (sourceNode instanceof AssessmentNode && targetNode instanceof LONode) {
      response = await api.createAssessmentToLoMapping({
        assessment: sourceNode.assessmentData.id,
        learning_outcome: targetNode.loData.id,
        contribution_weight: connection.weight || 0
      });
    }
    // LO -> PO
    else if (sourceNode instanceof LONode && targetNode instanceof PONode) {
      response = await api.createLoToPoMapping({
        learning_outcome: sourceNode.loData.id,
        program_outcome: targetNode.poData.id,
        weight: connection.weight || 1.0
      });
    }

    if (response && response.data) {
      connection.dbId = response.data.id;
      console.log('Mapping created:', response.data);
    }
  } catch (error) {
    console.error('Error creating mapping:', error);
    // Optionally remove connection if save failed
    // await editor.removeConnection(connection.id);
  }
}

async function handleConnectionRemoved(connection) {
  if (!connection.dbId) return;

  try {
    const sourceNode = editor.getNode(connection.source);
    const targetNode = editor.getNode(connection.target);

    // Determine type based on nodes (if available) or try both endpoints?
    // Since we have dbId, we need to know which endpoint to call.
    // But connection object might not have node references if nodes are already removed?
    // Rete v2 connectionremoved event passes the connection object.
    // If nodes are removed first, we might lose context.
    // However, we can check the connection type if we stored it, or infer from nodes if they exist.
    
    // If nodes are still there:
    if (sourceNode instanceof AssessmentNode) {
      await api.deleteAssessmentToLoMapping(connection.dbId);
    } else if (sourceNode instanceof LONode) {
      await api.deleteMapping(connection.dbId);
    } else {
      // Fallback: try deleting from both? Or store type in connection?
      // For now, let's assume nodes exist or we can infer.
      // If nodes are removed, Rete removes connections.
      // If we clear editor, we should avoid calling delete API if we just want to clear UI.
      // But here we want to sync.
      // If user deletes a node, connections are removed. We should delete mappings.
      
      // If we can't determine type, we might fail.
      // Let's try to store type in connection when creating?
      // Or just try both delete endpoints (inefficient but works).
      
      // Better: check if we can find the mapping in our local lists
      const isAssessMap = assessmentMappings.value.find(m => m.id === connection.dbId);
      if (isAssessMap) {
        await api.deleteAssessmentToLoMapping(connection.dbId);
      } else {
        await api.deleteMapping(connection.dbId);
      }
    }
    console.log('Mapping deleted:', connection.dbId);
  } catch (error) {
    console.error('Error deleting mapping:', error);
  }
}

async function updateConnectionWeight(dbId, weight, connection) {
  if (!dbId) {
    console.warn('Cannot update weight: No DB ID');
    return;
  }

  try {
    const sourceNode = editor.getNode(connection.source);
    
    if (sourceNode instanceof AssessmentNode) {
      // Assessment -> LO
      await api.updateAssessmentToLoMapping(dbId, {
        contribution_weight: weight
      });
    } else if (sourceNode instanceof LONode) {
      // LO -> PO
      await api.updateMapping(dbId, {
        contribution_weight: weight
      });
    }
    console.log('Weight updated:', dbId, weight);
  } catch (error) {
    console.error('Error updating weight:', error);
  }
}

// Provide update function to child components
provide('updateConnectionWeight', updateConnectionWeight);

// Load courses on mount
onMounted(async () => {
  try {
    const response = await api.getCourses();
    courses.value = response.data;
    
    // Initialize editor after DOM is ready
    await initializeEditor();
  } catch (error) {
    console.error('Error loading courses:', error);
  }
});

// Cleanup on unmount
onUnmounted(() => {
  if (area) {
    area.destroy();
  }
});

// Watch for course selection
watch(selectedCourse, (newVal) => {
  if (newVal) {
    loadCourseData();
  }
});
</script>

<style scoped>
.mapping-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
  overflow: hidden;
}

.editor-header {
  background: white;
  padding: 0.75rem 0.5rem; /* Padding azaltıldı */
  border-bottom: 2px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.editor-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.3rem;
}

.btn-toggle {
  padding: 0.5rem 1rem;
  background: #757575;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.3s;
  white-space: nowrap;
}

.btn-toggle:hover {
  background: #616161;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.course-select {
  padding: 0.5rem 1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  min-width: 200px;
}

.btn-save {
  padding: 0.5rem 1.5rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background 0.3s;
}

.btn-save:hover:not(:disabled) {
  background: #45a049;
}

.btn-save:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.editor-content {
  display: flex;
  flex: 1;
  overflow: hidden; /* Scrollbarları gizle, Rete pan/zoom kullanacak */
  position: relative;
  min-height: 0;
}

.forms-panel {
  width: 240px; /* Panel genişliği azaltıldı */
  background: white;
  border-right: 2px solid #e0e0e0;
  padding: 1rem;
  overflow-y: auto;
  flex-shrink: 0;
  max-height: 100%;
  z-index: 10; /* Rete canvas üzerinde kalsın */
}

.form-section {
  margin-bottom: 1.5rem;
}

.form-section h3 {
  margin: 0 0 0.75rem 0;
  color: #555;
  font-size: 1rem;
}

.form-section form {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.form-input,
.form-textarea {
  padding: 0.4rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 0.85rem;
  font-family: inherit;
}

.form-textarea {
  min-height: 60px;
  resize: vertical;
}

.btn-create {
  padding: 0.6rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: background 0.3s;
}

.btn-create:hover {
  background: #1976d2;
}

.rete-container {
  flex: 1;
  position: relative;
  background: #fafafa;
  height: 100%;
  width: 100%; /* Tam genişlik */
  overflow: hidden !important; /* Rete.js pan/zoom kullanacak */
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #999;
}

/* Rete.js custom styles */
:deep(.rete) {
  width: 100%;
  height: 100%;
  overflow: hidden !important;
}

:deep(.rete-container) {
  overflow: hidden !important;
}

:deep(.rete > div) {
  overflow: hidden !important;
}

:deep(.node) {
  background: white;
  border: 2px solid #ddd;
  border-radius: 12px;
  padding: 12px;
  min-width: 200px; /* Biraz daha geniş */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

:deep(.node .input) {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

:deep(.node .output) {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: 8px;
}

:deep(.node .input-title),
:deep(.node .output-title) {
  margin: 0 8px;
  font-size: 0.9rem;
  color: #555;
}

:deep(.socket) {
  width: 20px;
  height: 20px;
  border: 3px solid #2196f3;
  background: white;
  border-radius: 50%;
  cursor: pointer;
  z-index: 2;
  flex-shrink: 0; /* Küçülmesini engelle */
}

/* Input socket'i içeri al */
:deep(.input .socket) {
  margin-left: -2px; 
}

/* Output socket'i içeri al */
:deep(.output .socket) {
  margin-right: -2px;
}

:deep(.socket:hover) {
  border-color: #1976d2;
  transform: scale(1.2);
}

:deep(.node.selected) {
  border-color: #2196f3;
  box-shadow: 0 6px 12px rgba(33, 150, 243, 0.3);
}

:deep(.node .description-control) {
  display: none;
}

:deep(.node.selected .description-control) {
  display: block;
}

/* Node Type Colors - Applied to wrapper via pipe */
:deep(.assessment .node) {
  border-color: #f97316;
  background: #ffae45;
}
:deep(.assessment .node .title) {
  background: #f97316;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  text-align: center;
}

:deep(.learning-outcome .node) {
  border-color: #3b82f6;
  background: #62a6ff;
}
:deep(.learning-outcome .node .title) {
  background: #3b82f6;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  text-align: center;
}

:deep(.program-outcome .node) {
  border-color: #10b981;
  background: #00db6a;
}
:deep(.program-outcome .node .title) {
  background: #10b981;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  text-align: center;
}

:deep(.connection path) {
  stroke-width: 2;
  stroke: #2196f3;
  transition: stroke 0.3s;
}

:deep(.connection:hover path) {
  stroke: #1976d2;
}
</style>
