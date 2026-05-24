# Final Deliverable - Marks Breakdown Summary

## OVERALL STRUCTURE (75% of Final Grade)

```
75% Final Deliverable
├── 70% Report + Viva + System (RVS)
│   ├── 25% Main Report (7000-10000 words)
│   │   ├── 5% Presentation (grammar, formatting, referencing)
│   │   ├── 10% Description of Major Components
│   │   ├── 5% Development Lifecycle (methodology & validation)
│   │   └── 5% Critical Analysis & Reflection
│   ├── 15% Viva (Oral Presentation) - MANDATORY
│   │   ├── 10% Timing, Delivery & System Coverage
│   │   └── 5% Question Handling
│   └── 40% The System (Software Product)
│       ├── 30% Product (meets objectives, completeness)
│       └── 10% Robustness & Usability
└── 5% (Other factors - innovation, exceptional achievement)
```

---

## DETAILED MARKING CRITERIA

### A. REPORT (25%)

#### 1. Presentation (5%)
**What's assessed:**
- Spelling and grammar
- Written style and clarity
- Professional formatting
- Table of contents
- Page numbers
- Proper referencing (Harvard or IEEE)
- Acknowledgements
- Overall document appearance

**To achieve high marks:**
- Proofread multiple times
- Use consistent formatting
- Include proper references (20-30 minimum)
- Add clear headings and subheadings
- Include diagrams and screenshots where relevant

---

#### 2. Description of Major Components (10%)
**What's assessed:**
- Clear explanation of the problem and objectives
- Detailed description of each major system component:
  - Email parser
  - Feature extraction engine
  - ML classification model
  - Web dashboard/UI
  - Backend API/server
- Rationale for each design decision
- Why you chose specific technologies/algorithms

**To achieve high marks:**
- Explain the "why" not just the "what"
- Link design decisions to project requirements
- Discuss trade-offs and alternatives considered
- Use architecture diagrams
- Show how components interact

---

#### 3. Development Lifecycle (5%)
**What's assessed:**
- Evidence of software development methodology (Agile, Waterfall, etc.)
- Description of major development stages
- How validation was applied at each stage
- How verification was applied at each stage
- Testing approach and coverage

**To achieve high marks:**
- Describe a clear development process
- Show testing at multiple stages (unit, integration, end-to-end)
- Discuss how you ensured quality
- Document validation against requirements
- Include metrics and test results

---

#### 4. Critical Analysis & Reflection (5%)
**What's assessed:**
- What went well in the project
- What didn't work as expected
- What could be done differently next time
- Appraisal of the product (strengths & weaknesses)
- Analysis of your approach and tools used
- Honest reflection on limitations

**To achieve high marks:**
- Be honest and critical (don't just praise your work)
- Identify genuine limitations
- Suggest realistic improvements
- Show learning and maturity
- Discuss both technical and project management aspects

---

### B. VIVA/DEMONSTRATION (15%)

#### 1. Timing, Delivery & System Coverage (10%)
**What's assessed:**
- Professional presentation of the system
- Demonstrates all important use cases:
  - Uploading a benign email → "Safe" result
  - Uploading a phishing email → "Phishing" with threat indicators
  - Error handling (invalid file formats, corrupted files)
- Fills the allotted time appropriately
- Smooth demonstration with no crashes
- Clear explanation of what's happening

**To achieve high marks:**
- Practice your demo thoroughly
- Prepare sample emails in advance
- Have backup demo videos if possible
- Explain features clearly
- Show system stability and error handling
- Time your presentation well (aim for ~20-25 minutes)

---

#### 2. Question Handling (5%)
**What's assessed:**
- Understanding of your own system
- Ability to explain technical decisions
- Defending your design choices
- Answering follow-up questions confidently
- Showing genuine knowledge (not memorized)

**Likely questions:**
- "Why did you choose this ML algorithm over others?"
- "How did you handle feature engineering?"
- "What's the accuracy of your model and why?"
- "How would you improve the system?"
- "How does your feature extraction handle edge cases?"
- "Why did you use this technology for the backend?"
- "What were the main challenges you faced?"
- "How would you deploy this in production?"

**To achieve high marks:**
- Know your code inside and out
- Be ready to show code snippets
- Explain your evaluation metrics
- Discuss limitations honestly
- Show critical thinking about improvements

---

### C. THE SYSTEM (40%)

#### 1. Product - Completeness (30%)
**What's assessed:**
- System meets ALL objectives from your project contract
- Completeness of implementation:
  - Email parser (supports .eml, .msg formats)
  - Feature extraction (headers, URLs, body text)
  - ML model (trained and working)
  - User interface (functional and usable)
  - Backend/API (processes emails correctly)
  - Results display (shows classification and threat indicators)

**To achieve high marks:**
- Implement all features from your first deliverable plan
- No incomplete sections
- All components working together seamlessly
- System meets the requirements you outlined
- Demonstrate with multiple test cases

---

#### 2. Robustness & Usability (10%)
**What's assessed:**
- **Usability:**
  - Intuitive interface
  - Clear instructions
  - Easy file upload
  - Clear results display
  - Helpful error messages
  
- **Robustness:**
  - Handles edge cases
  - Doesn't crash on unexpected input
  - Proper error handling
  - Validates input appropriately
  
- **Correctness:**
  - ML model predicts accurately
  - Feature extraction works correctly
  - Results are reliable

**To achieve high marks:**
- Design a clean, professional UI
- Test extensively with various inputs
- Handle errors gracefully
- Provide clear feedback to users
- Ensure consistent, correct results
- Document limitations

---

## SCALING THE MARKS

### Excellent (70-79%)
✓ Comprehensive report with strong analysis  
✓ Well-designed, fully functional system  
✓ Professional demonstration  
✓ Confident answers to questions  
✓ Minor limitations discussed honestly  

### Exceptional (80-89%)
✓ Outstanding report with deep technical insight  
✓ Sophisticated, robust system  
✓ Excellent demonstration with no issues  
✓ Expert-level answers and critical thinking  
✓ Novel approaches or exceptional implementation  

### Distinction (>90%)
✓ Exceptional in all areas  
✓ Research-level contributions  
✓ Innovative solutions  
✓ Outstanding presentation and defense  

---

## CRITICAL REQUIREMENTS (Do Not Miss!)

⚠️ **MANDATORY:** Viva/oral presentation
- If you don't complete viva, you get 0% for the entire 75% deliverable
- You must present and defend your system

📝 **WORD COUNT:** 7000-10000 words for main report
- Less than 7000: Marks deducted
- More than 10000: Marks deducted
- References don't count toward word count

✅ **COMPLETENESS:** All features from project contract must be implemented
- Email parser: required
- Feature extraction: required
- ML model: required
- User interface: required
- Working system: required

---

## QUICK CHECKLIST

### For the Report:
- [ ] 7000-10000 words (excluding references)
- [ ] All sections included (intro, design, implementation, testing, analysis, conclusion)
- [ ] Spelling and grammar checked
- [ ] Proper formatting and page numbers
- [ ] 20-30 academic references
- [ ] Diagrams and screenshots included
- [ ] Critical analysis and honest reflection
- [ ] Submitted to TurnItIn

### For the System:
- [ ] Email parser working
- [ ] Feature extraction complete
- [ ] ML model trained and evaluated
- [ ] Web interface functional
- [ ] Backend API working
- [ ] File upload support (.eml, .msg)
- [ ] Results display with threat indicators
- [ ] Error handling implemented
- [ ] Thoroughly tested

### For the Viva:
- [ ] System demonstrates without crashing
- [ ] Can explain all design decisions
- [ ] Prepared to answer technical questions
- [ ] Have sample emails ready
- [ ] Slides prepared (10-15 slides)
- [ ] Code snippets ready to show
- [ ] Practiced the demonstration
- [ ] Ready to discuss limitations

---

## MARK TARGETS

**Aim for:**
- **Report:** 20-25 points out of 25 (80-100%)
- **Viva:** 12-15 points out of 15 (80-100%)
- **System:** 35-40 points out of 40 (87-100%)

**Total:** 67-80 points out of 75 (89-107%, excellent to exceptional)

---

**Remember:** The examiners want to see:
1. A complete, working system
2. Deep understanding of your implementation
3. Honest critical reflection
4. Professional presentation
5. Confidence in defending your work

You've already done the hard planning work in the first deliverable. Now it's time to build and present it!

Good luck! 🎓
