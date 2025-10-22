# MERN Autograder Deployment Instructions

## Prerequisites
- Coursera Autograder CLI installed
- Access to Coursera course authoring tools
- Course ID, Item ID, and Part ID

## Deployment Steps

1. **Upload the autograder:**
   ```bash
   coursera-autograder upload mern-autograder.tar.gz <COURSE_ID> <ITEM_ID> <PART_ID>
   ```

2. **Configure assignment settings:**
   - Part ID: `MernNotesApp`
   - Memory Limit: 8192 MB
   - CPU Limit: 2 cores
   - Timeout: 300 seconds

3. **Test the deployment:**
   - Submit a test assignment
   - Verify feedback delivery
   - Check scoring accuracy

## Test Results

### Complete Project Test
```json
Found submission files: ['package.json', 'src']
Installing dependencies...
Running test 1: Project Structure
Running test 2: Package.json Configuration
Running test 3: App Component Structure
Running test 4: Note Component Structure
Running test 5: Firebase Integration
Running test 6: Note Creation Functionality
Running test 7: Note Editing Functionality
Running test 8: Drag and Drop Functionality
{"fractionalScore": 1.0, "feedback": "\ud83c\udf89 Excellent! You passed all test cases!\n\n\ud83d\udccb Test Results:\n\u2705 Test 1: Project Structure\n\u2705 Test 2: Package.json Configuration\n\u2705 Test 3: App Component Structure\n\u2705 Test 4: Note Component Structure\n\u2705 Test 5: Firebase Integration\n\u2705 Test 6: Note Creation Functionality\n\u2705 Test 7: Note Editing Functionality\n\u2705 Test 8: Drag and Drop Functionality"}
```

### Incomplete Project Test
```json
{"fractionalScore": 0.0, "feedback": "Missing required files: src. Please ensure you have submitted a complete React project."}
Found submission files: ['package.json']
```

## Troubleshooting

If you encounter issues:
1. Check Docker logs for errors
2. Verify file permissions
3. Test with sample submissions
4. Contact support if needed

## Support

For technical support, refer to:
- Coursera Autograder Documentation
- This project's README.md
- Implementation Guide
