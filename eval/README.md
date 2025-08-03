# RAGAS Evaluation Directory

This directory contains all evaluation-related files for the Federal Ethics Chatbot, organized at the project root level for better separation from production API code.

## Directory Structure

```
eval/
├── README.md                           # This file
├── __init__.py                         # Python package initialization
├── ragas_evaluation_service.py         # Main RAGAS evaluation service
├── test_dataset.json                   # Test scenarios with ground truth
├── ragas_demo.py                       # Interactive demonstration
├── scripts/
│   └── run_ragas_evaluation.py         # Main evaluation script
└── output/                            # Generated evaluation results
    ├── ragas_evaluation_YYYYMMDD_HHMMSS.json
    └── ragas_evaluation_YYYYMMDD_HHMMSS.csv
```

## Quick Start

### Run Evaluation
```bash
# From project root
python3 eval/scripts/run_ragas_evaluation.py
```

### View Demo
```bash
# From project root  
python3 eval/ragas_demo.py
```

### Results
- **JSON**: `eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.json`
- **CSV**: `eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.csv`
- Each run creates uniquely timestamped files

## Key Features

- ✅ **Comprehensive Test Dataset**: 12 federal ethics scenarios
- ✅ **6 RAGAS Metrics**: Faithfulness, relevancy, precision, recall, correctness, similarity
- ✅ **Unique Timestamped Results**: Preserves evaluation history
- ✅ **Structured Logging**: Detailed evaluation tracking
- ✅ **Clean Architecture**: Separated from production API code

## Dependencies

The evaluation system requires:
- `ragas>=0.3.0` - Evaluation framework
- `datasets>=4.0.0` - Data handling
- `langchain-tavily>=0.2.11` - Web search (updated)
- Access to `api/` directory for chatbot services

## Documentation

See `docs/ragas_evaluation_guide.md` for comprehensive documentation.