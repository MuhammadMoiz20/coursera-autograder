# Autograder Deployment Instructions

## Prerequisites
- Coursera Autograder CLI installed
- Access to Coursera course authoring tools
- Course ID, Item ID, and Part ID

## Deployment Steps

1.  **Prepare the Autograder:**
    Ensure `config.json` has the correct `partId` if you are using it for validation, though the grader script largely relies on the `partId` passed via environment variable by Coursera.

2.  **Build the Docker Image:**
    ```bash
    docker build -t cypress-autograder .
    ```

3.  **Create the Release Bundle:**
    ```bash
    docker save cypress-autograder | gzip > cypress-autograder.tar.gz
    ```

4.  **Upload to Coursera:**
    ```bash
    coursera-autograder upload cypress-autograder.tar.gz <COURSE_ID> <ITEM_ID> <PART_ID>
    ```

5.  **Configure Assignment Settings on Coursera:**
    -   **Part ID:** Ensure this matches the `partId` expected by your grading logic (and encryption key if using `partId` as secret).
    -   **Resources:**
        -   Memory Limit: 1024 MB (Python parser is lightweight)
        -   CPU Limit: 1 core
        -   Timeout: 60 seconds (Parsing is fast)
    -   **Environment Variables (Optional):**
        -   `CYPRESS_RESULTS_SECRET`: Set this if you are using a custom secret key for encryption.

## Testing the Deployment

1.  **Submit a Valid Result:**
    -   Create a `cypress-results.json` with passing tests.
    -   (Optional) Encrypt it if testing encryption.
    -   Submit the file.
    -   Verify you get a 100% score.

2.  **Submit a Failing Result:**
    -   Create a `cypress-results.json` with failing tests.
    -   Submit.
    -   Verify you get a partial score and feedback.

## Troubleshooting

-   **"Encrypted Cypress results detected but no decryption secret was provided":**
    -   Ensure `CYPRESS_RESULTS_SECRET` is set in the Coursera assignment settings, or that the `partId` matches the encryption key used.

-   **"Results file ... is not valid JSON":**
    -   The student might have submitted a corrupted file or a plaintext file when encryption was expected (or vice versa, though the grader tries to handle both).

-   **"No tests were found":**
    -   Check `cypressSpecPattern` in `config.json`. It might be filtering out all tests.
