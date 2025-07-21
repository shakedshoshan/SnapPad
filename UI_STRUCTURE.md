# SnapPad UI Structure

This document describes the new organized UI structure for SnapPad.

## Overview

The UI components have been reorganized into a modular structure under the `ui/` directory to improve maintainability and code organization.

## Directory Structure

```
ui/
├── __init__.py          # Package initialization
├── components.py        # Basic UI components
├── workers.py          # Background worker threads
├── notes.py            # Note-related UI components
├── windows.py          # Window classes
└── dashboard.py        # Main dashboard class
```

## Module Descriptions

### `ui/__init__.py`
Package initialization file that makes the `ui` directory a Python package.

### `ui/components.py`
Contains basic UI components used throughout the application:
- **LoadingSpinner**: Animated loading indicator with dots
- **ClickableLabel**: Clickable label widget for clipboard history items

### `ui/workers.py`
Contains background worker threads for time-consuming operations:
- **OpenAIWorker**: Background thread for OpenAI API calls

### `ui/notes.py`
Contains note-related UI components:
- **EditableNoteWidget**: Complex widget for displaying and editing notes with inline editing capabilities
- **AddNoteDialog**: Dialog window for adding new notes

### `ui/windows.py`
Contains window classes:
- **NotesWindow**: Dedicated window for displaying all notes in a larger format

### `ui/dashboard.py`
Contains the main dashboard class:
- **Dashboard**: Main dashboard window that orchestrates all UI components

## Benefits of This Structure

1. **Modularity**: Each module has a specific responsibility
2. **Maintainability**: Easier to find and modify specific components
3. **Reusability**: Components can be easily imported and reused
4. **Testability**: Individual components can be tested in isolation
5. **Scalability**: New components can be added without cluttering the main file

## Import Changes

The main application now imports the Dashboard from the new location:

```python
# Old import
from dashboard import Dashboard

# New import
from ui.dashboard import Dashboard
```

## Migration Notes

- The original `dashboard.py` file has been backed up as `dashboard_backup.py`
- All functionality remains the same
- No changes to the application's behavior
- All imports have been updated to use the new structure

## Future Development

When adding new UI components:
1. Determine the appropriate module based on functionality
2. Add the component to the relevant file
3. Update imports in other files as needed
4. Consider creating new modules if the functionality doesn't fit existing ones

## File Sizes

- `ui/components.py`: ~5.2KB (172 lines)
- `ui/workers.py`: ~1.8KB (50 lines)
- `ui/notes.py`: ~30KB (821 lines)
- `ui/windows.py`: ~22KB (569 lines)
- `ui/dashboard.py`: ~43KB (1120 lines)

Total UI code: ~102KB (2732 lines) - organized into logical modules instead of one large file. 