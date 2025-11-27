
import sys
from pathlib import Path
from ragas import Dataset, experiment
from ragas.metrics import DiscreteMetric
from ragas.llms import llm_factory
import traceback
from openai import AsyncOpenAI

# Add the parent directory to sys.path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clients import get_llm
from src import orchestration

# Create an InstructorLLM instance that supports structured outputs
from src.config import get_settings
settings = get_settings()
llm = llm_factory(
    model="qwen-max",
    provider="openai",
    client=AsyncOpenAI(
        base_url=settings.qwen_api_base,
        api_key=settings.qwen_api_key,
    ),
)

def load_dataset(name: str):
    dataset = Dataset.load(
        name=name,
        backend="local/csv",
        root_dir="evals")
    return dataset



# Define correctness metric
def get_correctness_metric():
    return DiscreteMetric(
        name="correctness",
        prompt="""Compare the model response to the expected answer and determine if it's correct.

    Consider the response correct if it:
    1. Contains the key information from the expected answer
    2. Is factually accurate based on the provided context
    3. Adequately addresses the question asked

    Return 'pass' if the response is correct, 'fail' if it's incorrect.

    Question: {question}
    Expected Answer: {expected_answer}
    Model Response: {response}

    Evaluation:""",
        allowed_values=["pass", "fail"],
    )


def get_faithfulness_metric():
    """Faithfulness measures if the generated answer is factually consistent with the provided context.

    It evaluates whether the statements in the answer can be inferred from the context without introducing
    hallucinated information.
    """
    return DiscreteMetric(
        name="faithfulness",
        prompt="""Analyze the faithfulness of the model response with respect to the provided context.

    Given a question, context, and answer, your task is to:
    1. Break down the answer into individual factual statements
    2. For each statement, determine if it can be directly inferred from the context
    3. If a statement cannot be directly inferred or introduces information not present in the context,
       mark it as unfaithful

    Return 'pass' if all statements in the answer are faithful to the context, 'fail' if any statement
    is not directly supported by the context.

    Question: {question}
    Context: {context}
    Model Response: {response}

    Evaluation:""",
        allowed_values=["pass", "fail"],
    )


def get_answer_relevance_metric():
    """Answer Relevance measures how relevant the generated answer is to the given question.

    It evaluates whether the answer directly addresses the question without including irrelevant or
    redundant information.
    """
    return DiscreteMetric(
        name="answer_relevance",
        prompt="""Evaluate the relevance of the model response to the given question.

    Consider the response relevant if it:
    1. Directly addresses the question asked
    2. Does not contain unnecessary or redundant information
    3. Is focused on the specific query without digressions

    Return 'pass' if the response is relevant to the question, 'fail' if it is not relevant or
    contains significant irrelevant information.

    Question: {question}
    Model Response: {response}

    Evaluation:""",
        allowed_values=["pass", "fail"],
    )


def get_context_precision_metric():
    """Context Precision measures how useful the retrieved context is for generating the answer.

    It evaluates whether the retrieved context was actually helpful in generating the answer.
    """
    return DiscreteMetric(
        name="context_precision",
        prompt="""Evaluate the precision of the retrieved context for generating the answer.

    For each context segment, determine if it was useful in generating the given answer:
    1. Does the context contain information that directly contributes to the answer?
    2. Is the context relevant to the question being answered?
    3. Could the answer be generated without this context?

    Return 'pass' if the retrieved context is precise and useful, 'fail' if the context is
    not helpful for generating the answer.

    Question: {question}
    Retrieved Context: {context}
    Model Response: {response}

    Evaluation:""",
        allowed_values=["pass", "fail"],
    )


def get_context_recall_metric():
    """Context Recall measures how completely the retrieved context covers the information needed
    to generate the reference answer.

    It evaluates whether all the necessary information for generating the answer was retrieved.
    """
    return DiscreteMetric(
        name="context_recall",
        prompt="""Evaluate the recall of the retrieved context for generating the reference answer.

    Determine if the retrieved context contains all the necessary information to generate the
    reference answer:
    1. Does the context include all key facts needed for the reference answer?
    2. Is there any important information missing from the context that would be needed?
    3. Could the reference answer be fully generated from the retrieved context?

    Return 'pass' if the retrieved context has high recall (contains all necessary information),
    'fail' if important information is missing.

    Question: {question}
    Retrieved Context: {context}
    Reference Answer: {expected_answer}

    Evaluation:""",
        allowed_values=["pass", "fail"],
    )


# Initialize all metrics
correctness_metric = get_correctness_metric()
faithfulness_metric = get_faithfulness_metric()
answer_relevance_metric = get_answer_relevance_metric()
context_precision_metric = get_context_precision_metric()
context_recall_metric = get_context_recall_metric()


@experiment()
async def run_experiment(row):
    try:
        question = row["user_input"]

        # Query the RAG system
        rag_response = orchestration.chat("codex-gpt51", question, orchestration.SearchOptions())
        model_response = rag_response.answer

        # Get retrieved contexts
        retrieved_contexts = [
            doc.content for doc in rag_response.citations
        ]
        context_str = "\n\n".join(retrieved_contexts)

        # Evaluate all metrics asynchronously
        correctness_score = await correctness_metric.ascore(
            question=question,
            expected_answer=row["reference"],
            response=model_response,
            llm=llm
        )

        faithfulness_score = await faithfulness_metric.ascore(
            question=question,
            context=context_str,
            response=model_response,
            llm=llm
        )

        answer_relevance_score = await answer_relevance_metric.ascore(
            question=question,
            response=model_response,
            llm=llm
        )

        context_precision_score = await context_precision_metric.ascore(
            question=question,
            context=context_str,
            response=model_response,
            llm=llm
        )

        context_recall_score = await context_recall_metric.ascore(
            question=question,
            context=context_str,
            expected_answer=row["reference"],
            llm=llm
        )

        # Return evaluation results
        result = {
            **row,
            "model_response": model_response,
            "correctness_score": correctness_score.value,
            "correctness_reason": correctness_score.reason,
            "faithfulness_score": faithfulness_score.value,
            "faithfulness_reason": faithfulness_score.reason,
            "answer_relevance_score": answer_relevance_score.value,
            "answer_relevance_reason": answer_relevance_score.reason,
            "context_precision_score": context_precision_score.value,
            "context_precision_reason": context_precision_score.reason,
            "context_recall_score": context_recall_score.value,
            "context_recall_reason": context_recall_score.reason, # MLflow trace ID for debugging (explained later)
            "retrieved_documents": retrieved_contexts
        }

        print("result:", result)

        return result
    except Exception as e:
        print("Error in run_experiment:", e)
        traceback.print_exc()
        raise e

def get_mean_score(experiment_results, score_name):
    score = 0.0
    if len(experiment_results) == 0:
        return score
    for item in experiment_results:
        item_score = item[score_name]
        if item_score == 'pass':
            item_score = 1.0
        elif item_score == 'fail':
            item_score = 0.0
        if isinstance(item_score, str):
            item_score = float(item_score)
        score += item_score
    return score / len(experiment_results)

async def run():
    dataset = load_dataset("chat_dataset")
    print("dataset loaded successfully", dataset)
    experiment_results = await run_experiment.arun(dataset)
    print("Experiment completed successfully!")
    print("Experiment results:", experiment_results)
    
    # print all avg scores
    avg_scores = {
        "correctness_score": get_mean_score(experiment_results, "correctness_score"),
        "faithfulness_score": get_mean_score(experiment_results, "faithfulness_score"),
        "answer_relevance_score": get_mean_score(experiment_results, "answer_relevance_score"),
        "context_precision_score": get_mean_score(experiment_results, "context_precision_score"),
        "context_recall_score": get_mean_score(experiment_results, "context_recall_score"),
    }
    print("Average scores:", avg_scores)


    # Save experiment results to CSV
    experiment_results.save()
    csv_path = Path(".") / "experiments" / f"{experiment_results.name}.csv"
    print(f"\nExperiment results saved to: {csv_path.resolve()}")