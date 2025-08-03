# RAGAS Evaluation Guide

## Overview

This guide explains how to use RAGAS (Retrieval-Augmented Generation Assessment) to evaluate the Federal Ethics Chatbot's performance.

## What is RAGAS?

RAGAS is a framework for evaluating RAG (Retrieval-Augmented Generation) applications using the following metrics:

### Core Metrics

1. **Faithfulness** (0-1): Measures how well the generated answer is grounded in the retrieved context
2. **Answer Relevancy** (0-1): Evaluates how relevant the answer is to the given question
3. **Context Precision** (0-1): Measures the precision of the retrieved context
4. **Context Recall** (0-1): Evaluates the recall of the retrieved context
5. **Answer Correctness** (0-1): Compares the generated answer with ground truth
6. **Answer Similarity** (0-1): Measures semantic similarity to ground truth

## Test Dataset

The evaluation uses a comprehensive test dataset (`eval/test_dataset.json`) with 12 federal ethics scenarios covering:

- Gift acceptance violations
- Conflicts of interest
- Outside employment
- Use of government resources
- Financial conflicts
- Endorsement restrictions

Each test case includes:
- **Question**: The ethics scenario
- **User Context**: Role, agency, seniority level
- **Ground Truth**: Expected correct answer
- **Expected Violations**: Specific ethics rules violated
- **Expected Severity**: Minor, moderate, or serious
- **Expected Actions**: Recommended next steps

## Running RAGAS Evaluation

### Prerequisites

1. Ensure all dependencies are installed:
   ```bash
   uv sync
   ```

2. Configure environment variables:
   - `OPENAI_API_KEY`: Required for LLM evaluation
   - `TAVILY_API_KEY`: Required for web search (optional)
   - `LANGCHAIN_API_KEY`: Required for LangSmith tracing (optional)

### Quick Start

Run the complete evaluation:

```bash
python3 eval/scripts/run_ragas_evaluation.py
```

### Understanding Results

The evaluation generates comprehensive results in the `eval/output/` directory with unique timestamps:
- `eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.json`: Complete results with metadata
- `eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.csv`: Tabular format for analysis

Each evaluation run creates uniquely named files to preserve evaluation history and avoid overwriting previous results.

#### Score Interpretation

| Score Range | Performance Level | Interpretation |
|-------------|------------------|----------------|
| 0.8 - 1.0   | Excellent 🌟     | High quality responses |
| 0.7 - 0.8   | Good 👍          | Generally reliable |
| 0.6 - 0.7   | Fair 👌          | Acceptable with room for improvement |
| 0.5 - 0.6   | Needs Improvement 🔧 | Requires attention |
| 0.0 - 0.5   | Poor ⚠️          | Significant issues |

#### Key Metrics Focus

- **Faithfulness < 0.7**: Responses not well-grounded in retrieved context
- **Context Precision < 0.6**: Retrieval returning irrelevant documents
- **Context Recall < 0.6**: Missing relevant information in retrieval
- **Answer Correctness < 0.7**: Responses don't align with expected answers

## Evaluation Architecture

### Components

1. **RAGASEvaluationService**: Main evaluation orchestrator
2. **Test Dataset**: Curated ethics scenarios with ground truth
3. **AgenticWorkflowService**: Generates responses using the full RAG pipeline
4. **RAGAS Metrics**: Automated evaluation using OpenAI models

### Workflow

1. **Load Test Dataset**: Import ethics scenarios
2. **Generate Responses**: Process each scenario through the chatbot
3. **Extract Context**: Gather retrieved documents and web search results
4. **Run RAGAS**: Evaluate responses against ground truth
5. **Generate Report**: Create comprehensive evaluation report

## Customization

### Adding New Test Cases

Add scenarios to `eval/test_dataset.json`:

```json
{
  "question": "Your ethics scenario here",
  "user_context": {
    "role": "federal_employee",
    "agency": "YourAgency",
    "seniority": "GS-XX"
  },
  "ground_truth": "Expected correct answer",
  "expected_violations": ["Relevant ethics rules"],
  "expected_severity": "minor|moderate|serious",
  "expected_actions": ["Recommended actions"]
}
```

### Custom Metrics

Modify `eval/ragas_evaluation_service.py` to add custom metrics:

```python
from ragas.metrics import custom_metric

class RAGASEvaluationService:
    def __init__(self):
        self.metrics = [
            faithfulness,
            answer_relevancy,
            custom_metric,  # Add your custom metric
            # ... other metrics
        ]
```

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure OpenAI API key is configured
2. **Rate Limiting**: The script includes delays between requests
3. **Context Issues**: Vector database may need initialization
4. **Memory Issues**: Large datasets may require batch processing

### Debug Mode

Enable detailed logging by setting log level to DEBUG in configuration.

### Performance Optimization

- Use smaller test datasets for quick iterations
- Cache responses to avoid re-generating for metric experiments
- Consider parallel processing for large evaluations

## Best Practices

1. **Baseline Establishment**: Run evaluation before major changes
2. **Regular Monitoring**: Schedule periodic evaluations
3. **Metric Analysis**: Focus on metrics most relevant to your use case
4. **Ground Truth Quality**: Ensure high-quality expected answers
5. **Context Validation**: Verify retrieved context is relevant

## Integration with LangSmith

The evaluation automatically logs traces to LangSmith when configured:
- View detailed execution traces
- Analyze token usage and costs
- Monitor performance over time
- Debug specific evaluation steps

## Future Enhancements

Planned improvements:
- Custom ethics-specific metrics
- Automated evaluation scheduling
- Performance benchmarking
- A/B testing framework
- Real-time evaluation APIs