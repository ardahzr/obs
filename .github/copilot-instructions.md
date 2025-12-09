# PO Manager - AI Coding Agent Instructions

## Project Overview
**PO Manager** is an academic outcome management system for tracking student performance through Learning Outcomes (LO) and Program Outcomes (PO). Built as a Django + Vue.js SPA with visual node-based mapping using Rete.js v2.

**Data Flow**: `Assessment → Learning Outcome → Program Outcome`
- Assessments (exams/quizzes) contribute weighted percentages to LOs
- LOs contribute weighted percentages to POs  
- Student grades flow through this hierarchy to compute PO scores

## Architecture

### Backend: Django REST Framework
- **Location**: `po_manager/core/`
- **Models** (`models.py`): Course, Assessment, LearningOutcome, ProgramOutcome, AssessmentToLoMapping, LoToPoMapping, Student, Grade
- **Key Pattern**: All mappings use `unique_together` constraints on FK pairs + `contribution_weight` decimal field
- **ViewSets** (`views.py`): Standard ModelViewSet pattern with custom `@action` decorators for nested relationships
  - Example: `LearningOutcome.mappings()` GET/POST endpoint at `/learning-outcomes/{id}/mappings/`
- **Serializers** (`serializers.py`): Use nested serialization for detail views (e.g., `CourseDetailSerializer`)
- **Database**: SQLite at `po_manager/db.sqlite3` (use `python manage.py migrate` for schema changes)

### Frontend: Vue 3 + Rete.js v2
- **Location**: `frontend/src/`
- **State Management**: Composition API with `ref()`, NO Pinia/Vuex currently used
- **API Layer**: Centralized axios instance at `services/api.js` (base URL: `http://127.0.0.1:8000/api/`)
- **Routing**: Single-page app with view switching via `currentView` ref in App.vue (no vue-router active)

### Critical Rete.js v2 Patterns
**Reference**: https://retejs.org/llms-full.txt

**Node Editors**:
1. `ReteEditor.vue` - 2-column LO→PO mapping (left-to-right flow)
2. `OBSMappingView.vue` - 3-column Assessment→LO→PO mapping

**Custom Node Implementation**:
```javascript
class LONode extends ClassicPreset.Node {
  width = 220; height = 120;
  constructor(lo) {
    super('Learning Outcome');
    this.loData = lo; // Store backend data reference
    this.addOutput('lo-out', new ClassicPreset.Output(mappingSocket, 'Connect to PO'));
  }
}
```

**Connection Handling** - Multiple connections to same input allowed:
```javascript
connection.addPreset(() => ({
  canMakeConnection(from, to) {
    return (from.side === 'output' && to.side === 'input') || 
           (from.side === 'input' && to.side === 'output');
  },
  makeConnection(from, to, context) {
    // Custom WeightedConnection with default weight
    editor.addConnection(new WeightedConnection(sourceNode, source.key, targetNode, target.key, defaultWeight));
  }
}));
```

**Layout Strategy**: Vertical columns with fixed X positions, incremental Y spacing
- ReteEditor: LO nodes at x=100, PO nodes at x=800, verticalSpacing=200px
- OBSMappingView: Assessment x=80, LO x=580, PO x=1080, verticalSpacing=180px

**Cleanup Pattern**: Always clear connections BEFORE nodes when switching courses:
```javascript
for (const conn of editor.getConnections()) await editor.removeConnection(conn.id);
for (const node of editor.getNodes()) await editor.removeNode(node.id);
```

## Development Workflows

### Starting the Application
```bash
./start.sh              # Starts both backend (port 8000) and frontend (port 5173)
./status.sh             # Check running processes and ports
./stop.sh               # Stop all processes
```

**Manual Start**:
```bash
# Terminal 1 - Backend
cd po_manager && source ../venv/bin/activate && python manage.py runserver

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

### Database Management
- **Migrations**: Run after model changes: `python manage.py makemigrations && python manage.py migrate`
- **Seed Data**: 
  - `python manage.py shell < seed_program_outcomes.py` - Creates 11 standard POs
  - `python manage.py shell < seed_cse311.py` - Sample course with full mapping data
- **Admin**: `http://127.0.0.1:8000/admin/` (create superuser: `python manage.py createsuperuser`)

### Frontend Development
- **Vite Dev Server**: Auto-restarts on `.vue` file changes
- **Hard Refresh**: Use `Ctrl+Shift+R` after Rete.js changes (cache issues)
- **API Testing**: Backend must be running on port 8000 or update `services/api.js`

## Project-Specific Conventions

### Naming Patterns
- **Models**: PascalCase singular (`LearningOutcome`, not `LearningOutcomes`)
- **Serializers**: ModelName + `Serializer` suffix
- **ViewSets**: ModelName + `ViewSet` suffix  
- **Vue Components**: PascalCase with descriptive names (`ReteEditor`, `OBSMappingView`)
- **API Endpoints**: kebab-case plurals (`/learning-outcomes/`, `/assessment-to-lo-mappings/`)

### Weight/Contribution Conventions
- **LO-PO Mapping**: Default weight = 1.0 (no prompt in ReteEditor)
- **Assessment-LO Mapping**: Default weight = 50% (percentage in OBSMappingView)
- Backend stores as `DecimalField(max_digits=5, decimal_places=2)`

### UI Layout Philosophy
- **Horizontal Navbar**: Logo left, nav center, user/actions right (56px height)
- **Full-Screen Editors**: No padding, `calc(100vh - 56px)` height for max canvas space
- **Collapsible Panels**: Forms hidden by default (`showForms` / `showPanel` refs)
- **Overflow Handling**: Parent containers scroll, Rete canvas uses `overflow: visible !important`

### CORS & API Integration
- Backend has `CORS_ALLOW_ALL_ORIGINS = True` in `settings.py`
- Frontend hardcoded to `http://127.0.0.1:8000/api/` (not configurable via env vars currently)
- All API calls go through `services/api.js` - **NEVER use axios directly in components**

## Common Pitfalls

1. **Rete.js Connection Bugs**: If connections don't draw, check:
   - `canMakeConnection` returns true for valid socket pairs
   - `makeConnection` actually calls `editor.addConnection()`
   - Connection plugin preset defined BEFORE `editor.use(area)`

2. **Node Overlap**: Increase `verticalSpacing` and/or adjust node dimensions (width x height)

3. **Stale Connections**: When re-rendering, MUST clear connections before nodes or duplicates appear

4. **Weight Persistence**: Connections created in UI have default weights - only saved to backend via "Save All Mappings" button

5. **Course Filter Bug**: Always filter LOs/Assessments by `course == selectedCourse` (double equals for loose comparison)

## Testing & Debugging

- **Django Logs**: Check `/tmp/django.log` for backend errors
- **Browser DevTools**: Check Network tab for API call failures (CORS, 404s, validation errors)
- **Rete.js Inspector**: Use `editor.getNodes()` / `editor.getConnections()` in browser console
- **Database Inspection**: Use `python manage.py dbshell` or SQLite browser

## File References
- API Endpoints: `po_manager/core/urls.py`
- Model Relationships: `po_manager/core/models.py` 
- Rete.js Setup: `frontend/src/components/ReteEditor.vue` lines 137-215
- Connection Validation: `ReteEditor.vue` lines 153-189, `OBSMappingView.vue` lines 190-220
- Node Layout Logic: `ReteEditor.vue` lines 260-300, `OBSMappingView.vue` lines 270-330

## External Dependencies
- **Rete.js v2.0.6**: Node editor framework (breaking changes from v1)
- **rete-vue-plugin v2.1.2**: Vue 3 renderer (use `VuePresets.classic.setup()`)
- **Django 5.2**: Latest LTS with modern async support
- **Vite 7.2.1**: Dev server (note: `vueDevTools` disabled due to localStorage errors)
