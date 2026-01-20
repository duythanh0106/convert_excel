# 🎯 Web UI Quick Reference Card

## At a Glance

### Files Modified
| File | Changes | Type |
|------|---------|------|
| `templates/index.html` | ✏️ Rewritten | HTML |
| `templates/partials/index_styles.html` | ➕ Extended | CSS |

### Files Created
| File | Purpose | Type |
|------|---------|------|
| `templates/partials/universal_steps.html` | Universal converter workflow | HTML |
| `templates/partials/guideline_steps.html` | Guideline template workflow | HTML |
| `templates/partials/custom_template_steps.html` | Custom template workflow | HTML |
| `templates/partials/guideline_scripts.html` | All JavaScript logic | JS |
| `WEB_UI_UPDATE_SUMMARY.md` | Change summary | Docs |
| `WEB_UI_IMPLEMENTATION_GUIDE.md` | Implementation guide | Docs |
| `WEB_UI_FILE_STRUCTURE.md` | File structure reference | Docs |
| `WEB_UI_README.md` | Comprehensive guide | Docs |
| `WEB_UI_COMPLETION_CHECKLIST.md` | Completion checklist | Docs |

---

## 4 Conversion Modes

```
┌──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│     CLASSIC      │    UNIVERSAL     │    GUIDELINE     │     CUSTOM       │
├──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ Excel to DOCX    │  Any to Markdown │ 5-Section Templ. │ User Template    │
│ Original mode    │ 30+ formats      │ AI-optimized     │ + Variables      │
│ 6 steps          │ 2 steps          │ 3 steps          │ 3 steps          │
│ Best for: Excel  │ Best for: All    │ Best for: KB     │ Best for: Custom │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

---

## Guideline Template Types

```
┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│ Excel/CSV List      │ Word Document       │ Process/SOP         │ Policy/Guideline    │
├─────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
│ A. Source           │ A. Source           │ A. Source           │ A. Source           │
│ B. Summary          │ B. Summary          │ B. Summary          │ B. Summary          │
│ C. Metrics          │ C. Key Points       │ C. Key Points       │ C. Key Points       │
│ D. Insights         │ D. Deep Summary     │ D. Process Steps    │ D. Analysis         │
│ E. Structured       │ E. Optimized        │ E. Optimized        │ E. Optimized        │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

---

## Guideline Formatting Rules

| Element | Format | Example |
|---------|--------|---------|
| **Actor** | **Bold** | **Phòng ban Kỹ thuật** |
| **Action** | **Bold** | **Tạo tài liệu** |
| **Object** | **Bold** | **Tài liệu quy trình** |
| **ID** | > Quote | > user@email.com |
| **Variable** | Replace | {{SUMMARY}} |

---

## JavaScript Key Functions

```javascript
// Mode Control
switchMode('guideline')              // Switch conversion mode
goToStep('guideline-step-2')        // Navigate steps

// File Upload
handleGuidelineFileInput()            // Upload file

// Template Management
selectTemplate('excel_list')          // Select template type
loadPredefinedTemplate()              // Load template
extractVariablesFromTemplate(t)       // Parse {{VAR}}

// Conversion
convertWithGuideline()                // POST /api/v2/convert-with-guideline
previewGuidelineFormatting()          // POST /api/v2/format-text-guideline

// UI Control
showLoadingOverlay(true)              // Show spinner
handleConversionSuccess(result)       // Show download
```

---

## CSS Key Classes

```css
/* Modes */
.mode-section { display: none; }
.mode-section.active { display: block; }

/* Templates */
.template-card { cursor: pointer; }
.template-card.selected { background: #e8f0ff; }

/* Forms */
.form-group { flex-direction: column; }
.checkbox-group { display: flex; align-items: center; }

/* Steps */
.step { display: none; }
.step.active { display: block; }

/* Buttons */
.btn { padding: 12px 24px; }
.btn-primary { background: #667eea; }
.btn-success { background: #28a745; }

/* Variables */
.variable-tag { background: #667eea; color: white; }
```

---

## API Endpoints

```
Classic Mode (Existing):
  POST /upload
  POST /api/v1/*

Universal Mode:
  POST /api/v2/convert

Guideline Mode:
  POST /api/v2/convert-with-guideline
  POST /api/v2/format-text-guideline
  GET /api/v2/predefined-template?template_type=...

Custom Mode:
  POST /api/v2/convert-with-custom-template
  GET /api/v2/predefined-template?template_type=...
```

---

## Template Variable Syntax

```
Use {{VARIABLE_NAME}} in templates

Example:
  ## {{TITLE}}
  {{SUMMARY}}
  ### Key Points
  {{KEY_POINTS}}

System will:
  1. Extract variable names
  2. Create input fields
  3. Replace with user values
```

---

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Blue | #667eea | Buttons, links |
| Success Green | #28a745 | Success actions |
| Light Gray | #f8faff | Backgrounds |
| Border Gray | #e0e6ff | Borders |
| Text Dark | #333 | Headings |
| Text Gray | #666 | Body text |

---

## Responsive Breakpoints

```
Desktop:  1200px+ (sidebar + main side-by-side)
Tablet:   768-1199px (stacked layout)
Mobile:   <768px (single column, full width)
```

---

## Development Checklist

- [x] All files created
- [x] All CSS written
- [x] All JavaScript implemented
- [x] API endpoints integrated
- [x] Responsive design tested
- [x] Documentation completed
- [x] No syntax errors
- [x] Ready for production

---

## Testing Quick Start

```javascript
// Test mode switching
switchMode('guideline')
console.log(currentMode)  // Should be 'guideline'

// Test file upload
document.getElementById('guidelineFileInput').value = 'file'

// Test template selection
selectTemplate('excel_list')
console.log(currentTemplate)  // Should be 'excel_list'

// Test API call
fetch('/api/v2/predefined-template?template_type=excel')
  .then(r => r.json())
  .then(console.log)
```

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Mode not switching | Check browser console for errors |
| File not uploading | Verify file type and size |
| Variables not showing | Use {{VAR}} format (double braces) |
| API errors | Check backend is running |
| CSS not applied | Clear browser cache |
| JS errors | Check console (F12) |

---

## Documentation Map

```
WEB_UI_README.md
  ├─ Overview of all 4 modes
  ├─ How it works (step-by-step)
  └─ Future enhancements

WEB_UI_UPDATE_SUMMARY.md
  ├─ Files modified/created
  ├─ Features implemented
  └─ API endpoints

WEB_UI_IMPLEMENTATION_GUIDE.md
  ├─ Quick start for users
  ├─ How it works behind scenes
  └─ Testing scenarios

WEB_UI_FILE_STRUCTURE.md
  ├─ Complete file hierarchy
  ├─ CSS architecture
  ├─ JavaScript architecture
  └─ Data flow diagrams

WEB_UI_COMPLETION_CHECKLIST.md
  ├─ All completed tasks
  ├─ Feature status
  └─ Sign-off
```

---

## Key Statistics

| Metric | Value |
|--------|-------|
| HTML Files | 4 (3 new, 1 modified) |
| CSS Lines | 900+ |
| JavaScript Lines | 410+ |
| Functions | 14 |
| API Endpoints | 5 |
| Documentation Files | 5 |
| Modes Supported | 4 |
| Template Types | 4 |
| Guideline Rules | 5 |

---

## Getting Started

### For Users
1. Open http://localhost:5000
2. Select conversion mode
3. Upload file
4. Configure options
5. Click convert
6. Download result

### For Developers
1. Review WEB_UI_README.md
2. Check WEB_UI_FILE_STRUCTURE.md
3. Inspect CSS in index_styles.html
4. Review JS in guideline_scripts.html
5. Test in browser console

### For DevOps
1. Deploy updated templates/
2. Restart Flask server
3. Verify endpoints in /api/v2
4. Check logs for errors

---

## Support Resources

| Resource | Location |
|----------|----------|
| User Guide | WEB_UI_README.md |
| Technical Docs | WEB_UI_FILE_STRUCTURE.md |
| Implementation | WEB_UI_IMPLEMENTATION_GUIDE.md |
| API Reference | API_DOCUMENTATION.md |
| Guideline Rules | GUIDELINE_SYSTEM.md |

---

## Version Info

- **Version:** 3.0.0
- **Status:** ✅ Production Ready
- **Last Updated:** 2024
- **Compatibility:** All modern browsers
- **Responsive:** Yes (Desktop, Tablet, Mobile)

---

## Next Steps

1. ✅ Deploy files
2. ✅ Test all modes
3. ⏳ Gather user feedback
4. ⏳ Monitor performance
5. ⏳ Add batch processing (Phase 2)

---

## Quick Links

- Main Page: `http://localhost:5000`
- Admin: `http://localhost:5000/admin` (if available)
- API Docs: See `API_DOCUMENTATION.md`
- Guideline Guide: See `GUIDELINE_SYSTEM.md`

---

**🎉 All Done! Ready to Use!**

