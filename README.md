# MERN Notes App Autograder

A comprehensive Coursera autograder for evaluating MERN (MongoDB, Express, React, Node.js) Notes App submissions. This autograder tests React components, Firebase integration, drag-and-drop functionality, and overall project structure.

## Overview

This autograder is designed to evaluate student submissions for a React-based notes application with the following key features:
- React component structure and functionality
- Firebase real-time database integration
- Drag-and-drop note positioning
- Note creation, editing, and deletion
- Markdown rendering
- Category-based note organization
- Responsive design

## Project Structure

```
Mern_Autograder/
├── autograder/
│   ├── grader.py          # Main grading logic
│   ├── testCases.py       # Test case definitions
│   ├── util.py           # Utility functions
│   └── Dockerfile        # Container configuration
├── sample-submissions/
│   ├── complete-project/  # Example passing submission
│   └── incomplete-project/ # Example failing submission
└── README.md             # This documentation
```

## Test Cases

The autograder evaluates 8 comprehensive test cases:

### 1. Project Structure
- Verifies presence of required files:
  - `package.json`
  - `src/index.jsx`
  - `src/components/App.jsx`
  - `src/components/Note.jsx`
  - `src/services/datastore.js`
  - `src/style.scss`

### 2. Package.json Configuration
- Checks for required dependencies:
  - `react`
  - `react-dom`
  - `firebase`
  - `react-draggable`
  - `react-markdown`

### 3. App Component Structure
- Validates React imports and hooks usage
- Checks for Firebase integration setup
- Verifies component structure

### 4. Note Component Structure
- Validates React Draggable integration
- Checks for React Markdown usage
- Verifies PropTypes validation
- Confirms useState hook usage

### 5. Firebase Integration
- Validates Firebase configuration
- Checks for required Firebase functions:
  - `onNotesValueChange`
  - `createNote`
  - `updateNote`
  - `deleteNote`

### 6. Note Creation Functionality
- Verifies note creation logic
- Checks input handling
- Validates Firebase integration

### 7. Note Editing Functionality
- Validates edit mode implementation
- Checks state management for editing
- Verifies form handling

### 8. Drag and Drop Functionality
- Validates drag handlers
- Checks position management
- Verifies z-index layering

## Usage

### Building the Docker Image

```bash
cd autograder
docker build -t mern-autograder .
```

### Testing Locally

```bash
# Test with complete project
docker run --rm \
  -v "$(pwd)/sample-submissions/complete-project:/shared/submission" \
  -e partId="MernNotesApp" \
  mern-autograder

# Test with incomplete project
docker run --rm \
  -v "$(pwd)/sample-submissions/incomplete-project:/shared/submission" \
  -e partId="MernNotesApp" \
  mern-autograder
```

### Coursera Integration

1. **Upload to Coursera:**
   ```bash
   # Build the image
   docker build -t mern-autograder .
   
   # Save as tar file
   docker save mern-autograder | gzip > mern-autograder.tar.gz
   
   # Upload using Coursera CLI
   coursera-autograder upload mern-autograder.tar.gz <course-id> <item-id> <part-id>
   ```

2. **Configure Assignment:**
   - Set the part ID to `MernNotesApp`
   - Configure resource limits (recommended: 2 CPU, 8192 MB memory)
   - Set timeout to 300 seconds

## Expected Student Submission Format

Students should submit a complete React project with the following structure:

```
submission/
├── package.json
├── src/
│   ├── index.jsx
│   ├── components/
│   │   ├── App.jsx
│   │   └── Note.jsx
│   ├── services/
│   │   └── datastore.js
│   └── style.scss
└── [other files as needed]
```

## Grading Criteria

- **Perfect Score (1.0):** All 8 test cases pass
- **Partial Credit:** Each test case is worth 1/8 of the total score
- **Zero Score:** Missing required files or critical functionality

## Feedback Messages

The autograder provides detailed feedback including:
- ✅ Passed test indicators
- ❌ Failed test indicators with specific error messages
- Overall score and summary
- Specific guidance on what needs to be fixed

## Technical Requirements

### Docker Environment
- Base image: Ubuntu 20.04
- Node.js 18.x
- Python 3.8+
- Build tools and dependencies

### Submission Requirements
- Must be a complete React project
- All required files must be present
- Dependencies must be properly configured
- Code must follow React best practices

## Troubleshooting

### Common Issues

1. **Missing Files Error:**
   - Ensure all required files are present
   - Check file paths and naming

2. **Dependency Issues:**
   - Verify package.json includes all required dependencies
   - Check for typos in dependency names

3. **Build Failures:**
   - Ensure code compiles without errors
   - Check for syntax errors

### Debug Mode

To enable debug output, set the environment variable:
```bash
export DEBUG=1
```

## Contributing

To modify the autograder:

1. Update test cases in `testCases.py`
2. Modify grading logic in `grader.py`
3. Test with sample submissions
4. Rebuild Docker image
5. Test on Coursera platform

## License

This autograder is designed for educational use with Coursera's platform. Please ensure compliance with Coursera's terms of service and your institution's policies.
