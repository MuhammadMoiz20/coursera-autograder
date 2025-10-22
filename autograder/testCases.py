# dependencies
import random, json, sys

sys.path.append('solutions/')

def createTests(numTestCases, partId=None):
    # Test cases for MERN Notes App
    # Each test case represents a different aspect of the application
    
    # Use provided partId or default to a generic one
    if partId is None or partId == "None":
        partId = "MernNotesApp"  # Default fallback
    
    # Create test cases with partId as the key for easier matching
    testCases = {
        partId: {
            "partId": partId,
            "tests": [
                {
                    "name": "Project Structure",
                    "type": "file_structure",
                    "required_files": [
                        "package.json",
                        "src/index.jsx",
                        "src/components/App.jsx",
                        "src/components/Note.jsx",
                        "src/services/datastore.js",
                        "src/style.scss"
                    ]
                },
                {
                    "name": "Package.json Configuration",
                    "type": "component",
                    "required_patterns": [
                        {
                            "file": "package.json",
                            "pattern": r'"react"',
                            "description": "React dependency"
                        },
                        {
                            "file": "package.json",
                            "pattern": r'"react-dom"',
                            "description": "React DOM dependency"
                        },
                        {
                            "file": "package.json",
                            "pattern": r'"firebase"',
                            "description": "Firebase dependency"
                        },
                        {
                            "file": "package.json",
                            "pattern": r'"react-draggable"',
                            "description": "React Draggable dependency"
                        },
                        {
                            "file": "package.json",
                            "pattern": r'"react-markdown"',
                            "description": "React Markdown dependency"
                        }
                    ]
                },
                {
                    "name": "App Component Structure",
                    "type": "component",
                    "required_patterns": [
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'import React',
                            "description": "React import"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'import Note',
                            "description": "Note component import"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'useState',
                            "description": "useState hook usage"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'useEffect',
                            "description": "useEffect hook usage"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'onNotesValueChange',
                            "description": "Firebase listener setup"
                        }
                    ]
                },
                {
                    "name": "Note Component Structure",
                    "type": "component",
                    "required_patterns": [
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'import React',
                            "description": "React import"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'import Draggable',
                            "description": "React Draggable import"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'import ReactMarkdown',
                            "description": "React Markdown import"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'PropTypes',
                            "description": "PropTypes validation"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'useState',
                            "description": "useState hook usage"
                        }
                    ]
                },
                {
                    "name": "Firebase Integration",
                    "type": "component",
                    "required_patterns": [
                        {
                            "file": "src/services/datastore.js",
                            "pattern": r'import firebase',
                            "description": "Firebase import"
                        },
                        {
                            "file": "src/services/datastore.js",
                            "pattern": r'firebaseConfig',
                            "description": "Firebase configuration"
                        },
                        {
                            "file": "src/services/datastore.js",
                            "pattern": r'onNotesValueChange',
                            "description": "Notes listener function"
                        },
                        {
                            "file": "src/services/datastore.js",
                            "pattern": r'createNote',
                            "description": "Create note function"
                        },
                        {
                            "file": "src/services/datastore.js",
                            "pattern": r'updateNote',
                            "description": "Update note function"
                        },
                        {
                            "file": "src/services/datastore.js",
                            "pattern": r'deleteNote',
                            "description": "Delete note function"
                        }
                    ]
                },
                {
                    "name": "Note Creation Functionality",
                    "type": "functionality",
                    "required_patterns": [
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'createNote',
                            "description": "Create note function"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'noteInput',
                            "description": "Note input state"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'fbCreateNote',
                            "description": "Firebase create note call"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'onKeyPress',
                            "description": "Enter key handling"
                        }
                    ]
                },
                {
                    "name": "Note Editing Functionality",
                    "type": "functionality",
                    "required_patterns": [
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'isEditing',
                            "description": "Edit mode state"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'handleEdit',
                            "description": "Edit handler function"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'handleDone',
                            "description": "Done editing handler"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'editTitle',
                            "description": "Edit title state"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'editText',
                            "description": "Edit text state"
                        }
                    ]
                },
                {
                    "name": "Drag and Drop Functionality",
                    "type": "functionality",
                    "required_patterns": [
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'onDrag',
                            "description": "Drag handler"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'position',
                            "description": "Position prop for Draggable"
                        },
                        {
                            "file": "src/components/Note.jsx",
                            "pattern": r'bringToFront',
                            "description": "Bring to front functionality"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'onMove',
                            "description": "Move handler in App"
                        },
                        {
                            "file": "src/components/App.jsx",
                            "pattern": r'zIndex',
                            "description": "Z-index management"
                        }
                    ]
                }
            ]
        }
    }

    return testCases
