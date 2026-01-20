# Web UI Update Summary - Guideline Template System

## Overview
Updated the web interface to support the new Universal File Converter v3.0.0 with Guideline Template System, including 4 conversion modes:
1. **Excel Classic** - Original Excel to DOCX conversion
2. **Universal** - 30+ file format conversion to Markdown
3. **Guideline Template** - AI-optimized 5-section template conversion
4. **Custom Template** - User-defined templates with variable injection

---

## Files Updated

### 1. **templates/index.html** (Main Page - REWRITTEN)
**Changes:**
- Restructured for multi-mode support
- Added dynamic sidebar with mode selector
- Added format dropdowns for universal mode
- Template type selector for Guideline mode
- Custom template selector for Custom mode
- Mode-specific sections that toggle based on selection

**Key Sections:**
```html
<!-- Mode Selection -->
<select id="conversionMode" onchange="switchMode(this.value)">
    <option value="classic">📊 Excel Classic (DOCX)</option>
    <option value="universal">🌍 Universal (Markdown)</option>
    <option value="guideline">📋 Guideline Template</option>
    <option value="custom">🎨 Custom Template</option>
</select>

<!-- Dynamic Mode Sections -->
<div id="classicMode" class="mode-section active">...</div>
<div id="universalMode" class="mode-section hidden">...</div>
<div id="guidelineMode" class="mode-section hidden">...</div>
<div id="customMode" class="mode-section hidden">...</div>
```

---

### 2. **templates/partials/index_steps.html** (UNCHANGED)
- Kept for backward compatibility with Classic mode
- Excel upload → Sheet selection → Preview → Configuration → Convert workflow

---

### 3. **templates/partials/universal_steps.html** (NEW)
**Purpose:** Support for Universal File Converter (30+ formats)

**Features:**
- File input accepting any file type
- Output format selector (Markdown, Text)
- Preserve formatting option
- Extract images option
- File description field

**Steps:**
1. Choose any file (PDF, DOCX, PPTX, Images, Code, Notebooks, etc.)
2. Configure output format and options
3. Convert to Markdown

---

### 4. **templates/partials/guideline_steps.html** (NEW)
**Purpose:** 5-Section Guideline Template Conversion

**Features:**
- File input for any source format
- Template type selector (Excel/CSV, Word, Process, Policy)
- Visual template cards with descriptions
- Guideline formatting toggle
- Text formatting preview panel
- Real-time preview of Guideline formatting rules

**Steps:**
1. Choose any file to convert
2. Select template type (Excel, Document, Process, Policy)
3. Configure Guideline formatting options
4. Preview formatting before conversion
5. Convert with applied formatting

**Guideline Rules Applied:**
- **Bold** Actors (Phòng ban, chức danh)
- **Bold** Actions (Hành động, hoạt động)
- **Bold** Objects (Tài liệu, công cụ)
- **> Quote** Identifiers (ID, Email, URL, file paths)
- Variable replacement (`<VARIABLE_NAME>` → actual value)

---

### 5. **templates/partials/custom_template_steps.html** (NEW)
**Purpose:** User-defined Template with Variable Injection

**Features:**
- File input for source
- Predefined template selector (Excel, Document, Process, Policy)
- Custom template textarea (paste your own)
- Dynamic variable input fields
- Variable validation and extraction
- Guideline formatting toggle for final output

**Steps:**
1. Choose source file
2. Select or create custom template
3. System extracts variables from template
4. Fill in variable values
5. Optional: Apply Guideline formatting
6. Convert with variable injection

**Template Syntax:**
```
Use {{VARIABLE_NAME}} for dynamic content
Example: {{SECTION_A}}, {{SOURCE_URL}}, {{SUMMARY}}
```

---

### 6. **templates/partials/index_styles.html** (EXTENDED)
**New CSS Classes Added:**

#### Mode Management
- `.mode-section` - Container for each conversion mode
- `.mode-section.active` - Visible mode

#### Template Cards
- `.template-selector` - Grid of template options
- `.template-card` - Individual template option
- `.template-card:hover` - Hover effect
- `.template-card.selected` - Selected state
- `.template-sections` - Section description

#### Forms & Inputs
- `.form-group` - Form element container
- `.checkbox-group` - Checkbox with label
- `.form-group textarea` - Large text input
- `.variable-tag` - Highlighted variable name
- `.variables-list` - Container for variable tags
- `.variables-injection` - Variable input section
- `.variable-input-group` - Single variable input

#### Buttons
- `.btn` - Base button style
- `.btn-primary` - Primary action (blue)
- `.btn-secondary` - Secondary action (gray)
- `.btn-success` - Success action (green)

#### Other Elements
- `.step-header` - Step title with number
- `.step-number` - Numbered step indicator
- `.steps-container` - All steps container
- `.formatting-preview` - Preview output display
- `.divider` - Section divider
- `.guideline-options` - Guideline settings panel

---

### 7. **templates/partials/guideline_scripts.html** (NEW)
**JavaScript Functions for Guideline Features:**

#### Mode Switching
- `switchMode(mode)` - Switch between Classic/Universal/Guideline/Custom modes
- `goToStep(stepId)` - Navigate between steps within a mode

#### File Handling
- `handleUniversalFileInput()` - Universal mode file upload
- `handleGuidelineFileInput()` - Guideline mode file upload
- `handleCustomFileInput()` - Custom template mode file upload

#### Template Management
- `selectTemplate(templateType)` - Select Guideline template type
- `loadPredefinedTemplate()` - Load template from backend
- `extractVariablesFromTemplate(template)` - Extract {{VAR}} from template
- `renderVariablesInputs()` - Create input fields for variables

#### Conversion
- `convertWithGuideline()` - POST to `/api/v2/convert-with-guideline`
- `convertUniversal()` - POST to `/api/v2/convert`
- `convertWithCustomTemplate()` - POST to `/api/v2/convert-with-custom-template`

#### Preview & Formatting
- `previewGuidelineFormatting()` - Show how text will be formatted
- `showLoadingOverlay(show, message)` - Loading indicator

#### Utilities
- `handleConversionSuccess(result)` - Show download link after conversion
- Event listeners for checkboxes, textarea changes

---

## API Endpoints Called

### Universal Mode
- **POST** `/api/v2/convert` - Convert any file to Markdown

### Guideline Mode
- **POST** `/api/v2/convert-with-guideline` - Convert with 5-section template
- **POST** `/api/v2/format-text-guideline` - Preview formatting
- **GET** `/api/v2/predefined-template?template_type=...` - Get template

### Custom Template Mode
- **POST** `/api/v2/convert-with-custom-template` - Convert with custom template + variables
- **GET** `/api/v2/predefined-template?template_type=...` - Load predefined template

---

## User Experience Flow

### Mode 1: Excel Classic (Original)
```
Choose File → Select Sheet → Preview → Config → Convert → Download DOCX
```

### Mode 2: Universal (New)
```
Choose Any File → Select Format Options → Convert → Download Markdown
```

### Mode 3: Guideline (New)
```
Choose File → Select Template Type → Preview Formatting → Convert → Download MD
```

### Mode 4: Custom Template (New)
```
Choose File → Paste/Select Template → Fill Variables → Convert → Download MD
```

---

## Visual Enhancements

### Colors & Styling
- **Primary Blue:** #667eea (buttons, links, headers)
- **Success Green:** #28a745 (success states)
- **Light Background:** #f8faff (panels, cards)
- **Hover Effects:** Smooth transitions, scale, shadow
- **Icons:** Emoji icons for visual clarity

### Layout
- **Responsive Grid:** Template cards adapt to screen size
- **Sticky Sidebar:** Mode selector stays accessible
- **Step Navigation:** Clear numbered steps
- **Form Spacing:** Consistent padding and margins

### Interactive Elements
- **Template Cards:** Hover highlight, selection border
- **Input Fields:** Focus states with blue outline
- **Checkboxes:** Color-coded with Guideline rules
- **Loading Overlay:** Backdrop blur effect
- **Buttons:** Ripple effect on hover

---

## Backward Compatibility

✅ **Fully Compatible:**
- Original Excel to DOCX mode works exactly as before
- All existing HTML/CSS/JS for Classic mode preserved
- New features are additive, not breaking changes
- Sidebar toggles mode visibility seamlessly

---

## Testing Checklist

- [ ] Switch between all 4 modes
- [ ] File upload in each mode
- [ ] Template selection and preview
- [ ] Variable extraction from custom templates
- [ ] Guideline formatting preview
- [ ] Conversion success and download
- [ ] Responsive design on mobile
- [ ] Loading states and error handling
- [ ] Tab navigation and focus management

---

## Future Enhancements

1. **Drag & Drop** - Drag files onto upload area
2. **History** - Save recent conversions
3. **Batch Processing** - Convert multiple files
4. **Template Editor** - Visual template builder
5. **Export Presets** - Save conversion settings
6. **Analytics** - Track conversion usage

---

## Notes

- All API endpoints return JSON responses
- File downloads are triggered via response headers
- Guideline formatting is optional for all modes
- Custom templates support nested variable replacement
- Form validation prevents incomplete conversions
- Loading states prevent double submissions

