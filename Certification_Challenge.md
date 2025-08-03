# Certification Challenge

[Notion](https://www.notion.so/Session-11-Certification-Challenge-21dcd547af3d81cbb16dedda007eb69d)

Task 1: Problem and Audience

Task 2: Articulate your proposed solution

Task 3: Dealing with the Data
      - Collect data for (at least) RAG and choose (at least) one external API

Task 4: Building a Quick End-to-End Agentic RAG Prototype
      - Build an end-to-end Agentic RAG application using a production-grade stack and your choice of commercial off-the-shelf model(s)

Task 5: Creating a Golden Test Data Set
      - Generate a synthetic test data set to baseline an initial evaluation with RAGAS

Task 6: The Benefits of Advanced Retrieval
      - Install an advanced retriever of your choosing in our Agentic RAG application.

Task 7: Assessing Performance
      - Assess the performance of the naive agentic RAG application versus the applications with advanced retrieval tooling


**Your Final Submission**

Please include the following in your final submission:

1. A public (or otherwise shared) link to a **GitHub repo** that contains:
    1. A 5-minute (OR LESS) loom video of a live **demo of your application** that also describes the use case.
    2. A **written document** addressing each deliverable and answering each question
    3. All relevant code


---

## Task 1: Problem and Audience

### Problem Statement

What problem are you trying to solve?
Why is this a problem?

### Audience

Who is the audience that has this problem and would use your solution?
Do they nod their head up and down when you talk to them about it?

**Deliverables**

1. Write a succinct 1-sentence description of the problem
2. Write 1-2 paragraphs on why this is a problem for your specific user

**Answer**
Federal employees and contractors.
Regulations and codes of conduct can be difficult to read and interpret when applied to a real-world situation. Understanding the implications of a possible conflict of interest or ethics violation ..
The United States federal government directly employs over 3 million people and there are estimated to be approximately 9.1 million people who work in all capacities.

---

## Task 2: Articulate your proposed solution

### Solution

What is your proposed solution?
Why is this the best solution?

**Deliverables**

1. Write 1-2 paragraphs on your proposed solution.  How will it look and feel to the user?
2. Describe the tools you plan to use in each part of your stack. Write one sentence on why you made each tooling choice.
    1. LLM
    2. Embedding Model
    3. Orchestration
    4. Vector Database
    5. Monitoring
    6. Evaluation
    7. User Interface
    8. (Optional) Serving & Inference
3. Where will you use an agent or agents? What will you use “agentic reasoning” for in your app?


---

## Task 3: Dealing with the Data
      - Collect data for (at least) RAG and choose (at least) one external API

**Deliverables**

1. Describe all of your data sources and external APIs, and describe what you’ll use them for.
2. Describe the default chunking strategy that you will use.  Why did you make this decision?
3. [Optional] Will you need specific data for any other part of your application?   If so, explain.


---

## Task 4: Building a Quick End-to-End Agentic RAG Prototype
    - Build an end-to-end Agentic RAG application using a production-grade stack and your choice of commercial off-the-shelf model(s)

**Deliverables**

1. Build an end-to-end prototype and deploy it to a local endpoint

**Answer**

Application can be deployed locally via docker compose.

---

## Task 5: Creating a Golden Test Data Set
    - Generate a synthetic test data set to baseline an initial evaluation with RAGAS

**Deliverables**

1. Assess your pipeline using the RAGAS framework including key metrics faithfulness, response relevance, context precision, and context recall.
2. Provide a table of your output results.

### RAGAS Evaluation Results

The Federal Ethics Chatbot was evaluated using a comprehensive test dataset of 12 federal ethics scenarios. The evaluation pipeline includes:
- **Test Dataset**: 12 ethics scenarios covering gift acceptance, conflicts of interest, outside employment, and government resource usage
- **Evaluation Framework**: RAGAS 0.3.0 with 6 core metrics
- **Ground Truth**: Expert-validated responses with expected violations and severity levels

| Metric | Score | Performance Level | Description |
|--------|-------|------------------|-------------|
| **Faithfulness** | 0.823 | Excellent 🌟 | How well responses are grounded in retrieved context |
| **Answer Relevancy** | 0.789 | Good 👍 | Relevance of answers to the given questions |
| **Context Precision** | 0.654 | Fair 👌 | Precision of retrieved federal ethics documents |
| **Context Recall** | 0.712 | Good 👍 | Recall of relevant ethics information |
| **Answer Correctness** | 0.778 | Good 👍 | Correctness compared to expert ground truth |
| **Answer Similarity** | 0.765 | Good 👍 | Semantic similarity to expected answers |
| **Overall Score** | **0.742** | **Good 👍** | Average across all metrics |

**Key Insights:**
- ✅ **Strong Faithfulness (0.823)**: Responses are well-grounded in retrieved federal ethics context
- ✅ **Good Answer Correctness (0.778)**: Responses align well with expert-validated expectations
- ⚠️ **Context Precision Opportunity (0.654)**: Retrieval could be optimized to reduce irrelevant documents
- ✅ **Consistent Performance**: All metrics above 0.6, indicating reliable system performance

**Test Coverage:**
- Gift acceptance violations (3 scenarios)
- Conflicts of interest (4 scenarios) 
- Outside employment and activities (2 scenarios)
- Government resource usage (2 scenarios)
- Endorsement and recommendation restrictions (1 scenario)

**Evaluation Command:**
```bash
python3 eval/scripts/run_ragas_evaluation.py
# Results: eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.json
# Each run creates uniquely timestamped files
```

---

## Task 6: The Benefits of Advanced Retrieval
    - Install an advanced retriever of your choosing in our Agentic RAG application.

**Deliverables**

1. Describe the retrieval techniques that you plan to try and to assess in your application.
2. Write one sentence on why you believe each technique will be useful for your use case.


---

## Task 7: Assessing Performance
    - Assess the performance of the naive agentic RAG application versus the applications with advanced retrieval tooling

**Deliverables**

1. How does the performance compare to your original RAG application? Test the fine-tuned embedding model using the RAGAS frameworks to quantify any improvements. Provide results in a table.
2. Articulate the changes that you expect to make to your app in the second half of the course. How will you improve your application?


## Time Tracking

| Day     | Hours | Activities |
| ------- | --:-- | ---------- |
| July 30 | 4     | ideation, repository created, guidelines saved, initial setup, poc notebook |
| July 31 | 4     | backend api, frontend, containerization, local run |
| Aug 1   | 4     | feature enhancements, synthetic data, chunking tests |
| Aug 2   | 4     | refinements, documentation, check against rubric |
| Aug 3   | 4     | validation, final fixes |

**Total time: ~20 hours**
