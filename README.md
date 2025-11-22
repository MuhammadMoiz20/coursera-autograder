# Cypress Results Autograder

A flexible Coursera autograder designed to process and grade Cypress test results. This autograder reads a JSON results file (which can be encrypted for security), calculates a score based on passing tests, and provides detailed feedback to students.

## Overview

Unlike traditional autograders that run tests inside the container, this autograder is designed for a workflow where:
1.  Students run Cypress tests in their local environment or a separate step.
2.  The tests generate a JSON results file (e.g., `cypress-results.json`).
3.  (Optional but recommended) The results file is encrypted to prevent tampering.
4.  The student submits the results file to Coursera.
5.  This autograder decrypts (if necessary), parses, and grades the submission.

## Features

-   **Secure Grading:** Supports OpenSSL-encrypted result files to ensure submission integrity.
-   **Detailed Feedback:** Provides a summary of passed/failed tests and specific error messages for failures.
-   **Flexible Configuration:** specific test patterns can be filtered via `config.json`.
-   **Lightweight:** Built on a slim Python image, requiring minimal resources.

## Project Structure

```
.
├── autograder/
│   ├── grader.py          # Main logic: parses JSON, decrypts, calculates score
│   └── util.py            # Utility functions for Coursera feedback
├── config.json            # Configuration (Part IDs, patterns)
├── Dockerfile             # Python environment with OpenSSL
├── README.md              # This documentation
└── DEPLOYMENT_INSTRUCTIONS.md
```

## Configuration

The `config.json` file controls the behavior of the grader:

```json
{
  "partId": "YOUR_PART_ID",
  "cypressSpecPattern": ".*", 
  "summary": "Description of the assignment"
}
```

-   `partId`: The unique identifier for the assignment part on Coursera.
-   `cypressSpecPattern`: A regex pattern to filter which tests count towards the score (useful if the results file contains tests for multiple parts).

## Encryption Setup (Recommended)

To prevent students from manually editing their scores in the JSON file, you should configure the test runner to encrypt the results.

The autograder expects encryption using OpenSSL with `aes-256-cbc` (default).

**Environment Variables:**
-   `CYPRESS_RESULTS_SECRET`: The secret key used for decryption. If not set, the grader may attempt to use the `partId` as the key.
-   `CYPRESS_RESULTS_SECRET_FILE`: Path to a file containing the secret.

## Local Testing

You can test the autograder locally using Docker.

1.  **Build the image:**
    ```bash
    docker build -t cypress-autograder .
    ```

2.  **Run with a sample submission:**
    Assuming you have a `cypress-results.json` in a `submission` folder:
    ```bash
    docker run --rm \
      -v "$(pwd)/submission:/shared/submission" \
      -e partId="YOUR_PART_ID" \
      cypress-autograder
    ```

## Submission Format

The autograder looks for files in the following order:
1.  `cypress-results.enc` (Encrypted)
2.  `cypress-results.json` (Plaintext)
3.  `[filename].enc` (if matching expected patterns)

## License

This project is intended for educational use on the Coursera platform.
