# Email Phishing Detection Tool - Final Deliverable Guide
## BSC Cybersecurity FYP - CSEC 3100D
### De Montfort University

---

## PROJECT OVERVIEW

**Student:** Shamsudin Aminullah (P2771339)  
**Supervisor:** Dunja Majstorovic  
**Project Title:** Phishing Email Detection Tool  
**First Deliverable:** 25% (Already Submitted)  
**Final Deliverable:** 75% (To be Completed)

---

## MARKING BREAKDOWN FOR FINAL DELIVERABLE (75%)

### 1. **Report + Viva + System (RVS) - 70%**

#### **A. Main Report (25%)**
- **Word Count:** 7,000 - 10,000 words (excluding references, max 3 pages)
- **Format:** PDF or Word document submitted to TurnItIn
- **Sections:**
  - **Presentation (5%):** Acknowledgements, length, spelling, grammar, style, table of contents, page numbers, referencing
  - **Description of Major Components (10%):** Clear explanation of problem, objectives, and rationale for design/implementation decisions
  - **Development Lifecycle (5%):** Software development methodology applied, validation/verification at each stage
  - **Critical Analysis & Reflection (5%):** What worked, what didn't, what could be done differently, appraisal of product

#### **B. Viva (Oral Presentation) - 15% (MANDATORY)**
- **Timing & Coverage (10%):** Professional demonstration filling available time appropriately, all important use cases covered
- **Question Handling (5%):** Ability to defend your system and technical decisions

#### **C. The System (40%)**
- **Product (30%):** System meets objectives from project contract and FYP requirements, completeness
- **Robustness & Usability (10%):** Usability, robustness, and correctness of the tool

---

## MARKING SCALE
- **< 30%:** Clear Fail
- **30-39%:** Marginal Fail
- **40-49%:** Bare Pass
- **50-59%:** Clear Pass
- **60-69%:** Very Good
- **70-79%:** Excellent
- **80-89%:** Exceptional
- **> 90%:** Innovation/Distinction

---

## TECHNICAL REQUIREMENTS (Based on First Deliverable)

### System Architecture
The tool should include:

1. **Front-End (User Interface)**
   - Web-based dashboard for email upload
   - Support for .eml and .msg file formats
   - Error handling for unsupported formats
   - Results display showing: Safe/Phishing verdict, confidence score, threat indicators
   - Clear visualization of suspicious features

2. **Back-End (Processing Engine)**
   - Email file parser
   - Feature extraction from:
     - Email headers (sender domain, routing information)
     - URLs (embedded links, domain reputation)
     - Body text (suspicious keywords, text patterns)
   - Feature structuring for ML model input

3. **Machine Learning Model**
   - Training data preparation and preprocessing
   - Model selection and training
   - Confidence scoring mechanism
   - Threat classification (Phishing vs. Benign/Safe)

4. **Database (Optional but Recommended)**
   - Store scan history with User, Scan_Job, Extracted_Features, Scan_Result entities
   - Enable security analysts to review past scans

---

## STEP-BY-STEP IMPLEMENTATION GUIDE

### PHASE 1: CORE BACKEND DEVELOPMENT (Weeks 1-3)

#### Task 1: Email Parser & Feature Extraction
**Deliverable:** Python module(s) for email parsing

**What to implement:**
```python
# Example structure
- email_parser.py: Parse .eml and .msg files
- feature_extractor.py: Extract headers, URLs, body text
- feature_engineering.py: Generate feature vectors
- suspicious_patterns.py: Keyword/pattern detection
```

**Key Features:**
- Extract sender domain (check for spoofing)
- Extract all URLs and check for suspicious patterns
- Parse email headers for authentication (SPF, DKIM, DMARC)
- Identify suspicious keywords and phishing indicators
- Generate numerical feature vectors (e.g., URL count, keyword count, domain legitimacy score)

**Test with:**
- Sample legitimate emails
- Sample phishing emails
- Edge cases (corrupted files, unusual formats)

---

#### Task 2: Machine Learning Model Development
**Deliverable:** Trained ML model with evaluation metrics

**What to implement:**
- Choose dataset: Public phishing email datasets (e.g., Enron phishing, SpamAssassin)
- Prepare features from extracted email data
- Train model (consider: Logistic Regression, Random Forest, or Neural Network)
- Evaluate: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- Fine-tune threshold for classification

**Key Decisions to Document:**
- Why you chose this algorithm
- Data preprocessing steps
- Feature selection rationale
- Hyperparameter choices
- Cross-validation strategy

---

### PHASE 2: USER INTERFACE & SERVER (Weeks 3-4)

#### Task 3: Web Dashboard (Frontend)
**Technology Options:**
- HTML/CSS/JavaScript (vanilla)
- React, Vue, or Flask/Django templates
- Bootstrap or Tailwind for styling

**Required Features:**
- File upload interface (drag-and-drop preferred)
- Form validation
- Progress indicator during processing
- Results display:
  - Large "SAFE" or "PHISHING" badge with color coding
  - Confidence percentage
  - List of threat indicators found
  - Recommended actions
- Error messages for invalid files

**Design Tips:**
- Keep it simple and professional
- Use clear visual hierarchy
- Mobile-responsive layout
- Accessibility considerations (WCAG)

---

#### Task 4: Backend Server/API
**Technology Options:**
- Flask or Django (Python)
- Express.js (Node.js)
- FastAPI (Python)

**API Endpoints Needed:**
```
POST /upload - Accept email file
POST /analyze - Run detection
GET /results/{job_id} - Retrieve results
GET /history - Scan history (optional)
```

**Server Responsibilities:**
- Receive uploaded files
- Call feature extraction
- Invoke ML model
- Format and return results
- Handle errors gracefully

---

### PHASE 3: TESTING & QUALITY ASSURANCE (Week 5)

#### Task 5: Comprehensive Testing
**Unit Tests:**
- Test email parser with various formats
- Test feature extraction accuracy
- Test ML model predictions

**Integration Tests:**
- Test file upload → processing → results pipeline
- Test API endpoints

**End-to-End Tests:**
- Upload real emails
- Verify results are correct
- Test error scenarios (corrupted files, very large files, etc.)

**Document:**
- Test cases with expected outcomes
- Test results summary
- Coverage report

---

### PHASE 4: DOCUMENTATION & REPORTING (Week 5-6)

#### Task 6: Write Main Report (7,000-10,000 words)

**Structure:**

1. **Introduction (10%)**
   - Hook: State the phishing problem
   - Background on phishing attacks (build on your literature review)
   - Problem statement
   - Project objectives

2. **System Design & Architecture (20%)**
   - Overall system architecture diagram
   - Component descriptions with rationale
   - Design decisions and justifications
   - Technology choices (Python, Flask, ML library) and why

3. **Implementation (20%)**
   - Email parsing approach
   - Feature extraction methods
   - ML model selection and training
   - Front-end implementation details
   - Code organization and structure

4. **Testing & Validation (15%)**
   - Test strategy and methodology
   - Test results (with metrics)
   - Validation against requirements
   - Known limitations

5. **Critical Analysis (15%)**
   - System strengths
   - Weaknesses and limitations
   - What worked well
   - What would be improved next time
   - Lessons learned

6. **Conclusion & Future Work (10%)**
   - Summary of achievements
   - How objectives were met
   - Recommendations for future enhancement
   - Final thoughts

7. **References**
   - Proper academic formatting
   - 20-30 references minimum

**Writing Tips:**
- Use formal academic tone
- Include diagrams, flowcharts, screenshots
- Reference your code and testing
- Bold or italicize important concepts
- Proofread multiple times

---

#### Task 7: Prepare for Viva/Demonstration

**What the Examiners Want to See:**

1. **Live System Demonstration (10 minutes)**
   - Upload a benign email → Show "Safe" result with explanation
   - Upload a phishing email → Show "Phishing" detection with threat indicators
   - Discuss false positives/negatives
   - Show system error handling

2. **Technical Understanding (Questions)**
   - Explain your feature extraction approach
   - Justify ML algorithm choice
   - Discuss how you gathered training data
   - Explain your evaluation metrics
   - What would you do differently?
   - How would you improve accuracy?

3. **Code Review (if requested)**
   - Be prepared to show key code snippets
   - Explain critical algorithms
   - Discuss code quality and organization

**Preparation Checklist:**
- ✓ Test system thoroughly (no crashes)
- ✓ Prepare 3-5 sample emails (mix of phishing and legitimate)
- ✓ Create 5-10 slides summarizing your project
- ✓ Practice your demonstration speech
- ✓ Prepare answers to likely questions
- ✓ Have code on laptop ready to show
- ✓ Document any known issues/limitations

---

### PHASE 5: FINAL SUBMISSION (Week 6)

#### Submission Checklist:
- [ ] Main report (7000-10000 words) as PDF
- [ ] Source code (well-organized and commented)
- [ ] README file with setup instructions
- [ ] Test results and test cases
- [ ] Database schema (if applicable)
- [ ] Any supplementary materials (diagrams, screenshots)
- [ ] Viva presentation slides (10-15 slides)
- [ ] Sample email files for demonstration
- [ ] All files properly named and dated

---

## TECHNOLOGY STACK RECOMMENDATIONS

### Recommended Stack (Modern & Professional)

**Backend:**
- Python 3.9+
- Flask or FastAPI for API
- scikit-learn or TensorFlow for ML
- pandas for data processing
- email library (built-in) for parsing

**Frontend:**
- HTML5 + CSS3 + JavaScript (or React/Vue)
- Bootstrap 5 for responsive design
- Axios or Fetch for API calls

**Database (Optional):**
- SQLite for development
- PostgreSQL for production

**Development Tools:**
- Git for version control
- Virtual environment (venv)
- Pytest for unit testing
- Jupyter Notebook for data exploration

### Alternative Stack
- Node.js + Express + React
- Django + React
- Any combination you're comfortable with

---

## KEY SUCCESS FACTORS

### 1. **Completeness (30%)**
   - Implement ALL features (parser, feature extraction, model, UI, API)
   - Handle edge cases and errors
   - Meet all project contract requirements

### 2. **Code Quality (20%)**
   - Well-organized, modular code
   - Clear variable/function names
   - Proper comments and documentation
   - Follows best practices

### 3. **Documentation (25%)**
   - Comprehensive main report
   - Clear technical explanations
   - Rationale for all major decisions
   - Critical reflection and analysis

### 4. **Testing & Robustness (15%)**
   - Thorough test coverage
   - Handle errors gracefully
   - No crashes or unexpected behavior
   - Validate against multiple email formats

### 5. **Demonstration & Communication (10%)**
   - Professional viva presentation
   - Ability to explain decisions
   - Answer questions confidently
   - Show genuine understanding

---

## COMMON PITFALLS TO AVOID

1. **Not testing thoroughly** - Ensure system works with various emails
2. **Poor documentation** - Explain your decisions in detail
3. **Weak ML model** - Use proper evaluation metrics, don't rely on accuracy alone
4. **Incomplete report** - Aim for ~9000 words, include all required sections
5. **Unprepared for viva** - Practice your demo and Q&A
6. **Ignoring edge cases** - Handle corrupted files, unusual formats, very large files
7. **Not meeting word count** - 7000-10000 words is a requirement
8. **Poor code organization** - Keep code modular and maintainable
9. **Inconsistent formatting** - Follow consistent style throughout report and code
10. **Last-minute submission** - Start early, review thoroughly

---

## TIMELINE SUGGESTION

- **Week 1-2:** Email parser + feature extraction
- **Week 3:** ML model training + evaluation
- **Week 4:** Frontend + Backend API
- **Week 5:** Testing + documentation + report writing
- **Week 6:** Final review + polishing + viva prep

---

## RESOURCES & REFERENCES

### Phishing Detection Research
- Fette, I., Sadeh, N., & Tomasic, A. (2007). Learning to detect phishing emails
- Abu-Nimeh, S., et al. (2007). A comparison of machine learning techniques for phishing detection
- Sahingoz, O. K., et al. (2019). Machine learning based phishing detection from URLs

### Datasets
- Enron Email Dataset with phishing labels
- SpamAssassin public dataset
- UCI Machine Learning Repository

### Tools & Libraries
- scikit-learn documentation
- pandas for data manipulation
- NLTK for text processing
- email library for parsing

---

## CONTACT & SUPPORT

**Supervisor:** Dunja Majstorovic  
**Email:** (Check your university email)

Remember: Your supervisor is your best resource. Schedule regular meetings and ask for feedback on your progress!

---

**Last Updated:** May 22, 2026  
**Status:** Ready for Implementation

Good luck with your final year project! You've got this! 🚀
