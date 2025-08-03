#!/usr/bin/env python3
"""
Debug RAGAS TestsetGenerator to understand why it generates 0 samples
"""

import sys
sys.path.append('../../api')

# Load settings to get API keys
from api.app.core.settings import settings
import os
os.environ["OPENAI_API_KEY"] = settings.openai_api_key

from ragas.testset import TestsetGenerator
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
import logging

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

# Create longer test documents (over 100 tokens each)
test_docs = [
    Document(
        page_content="Federal employees must not accept gifts from prohibited sources. A prohibited source includes any person who is seeking official action from the employee's agency, has interests that may be substantially affected by performance or nonperformance of the employee's official duties, or does business or seeks to do business with the employee's agency. This prohibition helps maintain public trust and prevents conflicts of interest that could compromise the integrity of government operations. Employees should be particularly careful about gifts from contractors, regulated entities, and other parties with business before their agency. The standards of ethical conduct provide specific guidance on what constitutes an acceptable gift and what must be declined or reported to ethics officials.",
        metadata={"source": "ethics_doc_1.pdf", "filename": "ethics_doc_1.pdf", "page": 1}
    ),
    Document(
        page_content="An employee may not use his public office for his own private gain, for the endorsement of any product, service or enterprise, or for the private gain of friends, relatives, or persons with whom the employee is affiliated in a nongovernmental capacity. This includes using government time, property, equipment, or other resources for private purposes. Employees must be careful not to leverage their official position to benefit themselves or others inappropriately. For example, an employee cannot use government letterhead for personal correspondence, use government computers for private business, or use their official title to endorse commercial products. The prohibition extends to allowing others to use the employee's name or position for private gain without proper authorization.",
        metadata={"source": "ethics_doc_2.pdf", "filename": "ethics_doc_2.pdf", "page": 1}
    ),
    Document(
        page_content="Federal employees are prohibited from engaging in financial transactions using nonpublic information or allowing the improper use of nonpublic information to further their own private interest or that of another. This includes information gained through their official duties that is not available to the general public and could be used for financial gain. Employees must be particularly careful about stock trading, real estate transactions, and other investments that could be affected by information they obtain through their work. The prohibition applies not only to the employee's own transactions but also to providing such information to family members, friends, or business associates who might use it for their financial benefit. Violations of this provision can result in serious criminal and civil penalties.",
        metadata={"source": "ethics_doc_3.pdf", "filename": "ethics_doc_3.pdf", "page": 1}
    )
]

print(f"Testing with {len(test_docs)} documents")
for i, doc in enumerate(test_docs):
    print(f"Doc {i+1}: {len(doc.page_content)} chars, metadata: {doc.metadata}")

# Initialize generator with simple settings
generator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4.1", temperature=0.7))
generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

generator = TestsetGenerator(
    llm=generator_llm,
    embedding_model=generator_embeddings
)

print("\nGenerating testset...")
try:
    # Try with very small testset_size
    dataset = generator.generate_with_langchain_docs(test_docs, testset_size=2)
    
    print(f"Generated dataset type: {type(dataset)}")
    print(f"Dataset length: {len(dataset)}")
    
    if len(dataset) > 0:
        print("Sample test case:")
        sample = dataset[0]
        print(f"  Type: {type(sample)}")
        print(f"  Dir: {dir(sample)}")
        if hasattr(sample, 'eval_sample'):
            print(f"  Eval sample type: {type(sample.eval_sample)}")
            print(f"  User input: {sample.eval_sample.user_input}")
            print(f"  Response: {sample.eval_sample.response}")
        else:
            print(f"  Sample content: {sample}")
    else:
        print("No samples generated!")
        
except Exception as e:
    print(f"Error during generation: {e}")
    import traceback
    traceback.print_exc()