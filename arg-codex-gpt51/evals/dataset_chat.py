# -*- coding: utf-8 -*-
"""
基于Ragas的测试集生成器，用于生成华为基本法文档的问答测试集
"""

import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import openai
from ragas.testset.graph import KnowledgeGraph
from ragas.testset.graph import Node, NodeType
from ragas.testset.transforms import apply_transforms
from ragas.testset.transforms import HeadlinesExtractor, HeadlineSplitter, KeyphrasesExtractor
from ragas.testset.synthesizers.single_hop.specific import (
    SingleHopSpecificQuerySynthesizer,
)
from ragas.testset import TestsetGenerator
from ragas.testset.persona import Persona
from src.clients import get_llm, get_embedder

llm = get_llm()
embedder = get_embedder()

# 建立LLM和嵌入模型
generator_llm = LangchainLLMWrapper(llm)
generator_embeddings = embedder

def create_knowledge_graph(docs):
    """Create a knowledge graph from documents, splitting large documents into chunks."""
    kg = KnowledgeGraph()

    # Initialize text splitter with reasonable chunk sizes
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,  # Reduced from default to stay within token limits
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", "。", "!", "?", "!", ";", ":", " ", ""]
    )

    for doc in docs:
        # Check document length and split if necessary
        if len(doc.page_content) > 10000:  # If document is large, split it
            split_docs = text_splitter.split_documents([doc])
            for i, split_doc in enumerate(split_docs):
                # Update metadata to indicate this is a chunk
                split_metadata = doc.metadata.copy()
                split_metadata['chunk_index'] = i
                split_metadata['total_chunks'] = len(split_docs)

                kg.nodes.append(
                    Node(
                        type=NodeType.DOCUMENT,
                        properties={
                            "page_content": split_doc.page_content,
                            "document_metadata": split_metadata
                        }
                    )
                )
        else:
            # For smaller documents, add as-is
            kg.nodes.append(
                Node(
                    type=NodeType.DOCUMENT,
                    properties={
                        "page_content": doc.page_content,
                        "document_metadata": doc.metadata
                    }
                )
            )

    return kg





# 设置变换
def set_transforms(kg):
    """Apply transformations to the knowledge graph."""
    headline_extractor = HeadlinesExtractor(llm=generator_llm, max_num=20)
    headline_splitter = HeadlineSplitter(max_tokens=1500)
    keyphrase_extractor = KeyphrasesExtractor(llm=generator_llm)

    transforms = [
        headline_extractor,
        headline_splitter,
        keyphrase_extractor
    ]

    apply_transforms(kg, transforms=transforms)





# 配置用于查询生成的用户角色
def create_personas():
    persona_1 = Persona(
        name="术研发专家",
        role_description="注于技术创新和产品研发，体现华为对核心技术发展和自主知识产权建设的重视",
    )
    persona_2 = Persona(
        name="市场战略分析师",
        role_description="关注市场拓展和客户价值创造，体现华为以客户为中心和追求市场领先地位的理念。",
    )
    
    personas = [persona_1, persona_2]
    return personas




# 配置查询分布
def create_query_distribution():
    query_distibution = [
        (
            SingleHopSpecificQuerySynthesizer(llm=generator_llm, property_name="headlines"),
            0.5,
        ),
        (
            SingleHopSpecificQuerySynthesizer(
                llm=generator_llm, property_name="keyphrases"
            ),
            0.5,
        ),
    ]
    return query_distibution


def generate_chat_dataset():
    # 加载文档
    path = "documents/"
    loader = DirectoryLoader(path, glob="**/*.md")
    docs = loader.load()
    # 利用文档创建基础知识图谱
    kg = create_knowledge_graph(docs)
    set_transforms(kg)
    personas = create_personas()
    query_distibution = create_query_distribution()
    generator = TestsetGenerator(
        llm=generator_llm,
        embedding_model=generator_embeddings,
        knowledge_graph=kg,
        persona_list=personas,
    )

    testset = generator.generate(testset_size=10, query_distribution=query_distibution)
    testset.to_pandas().to_csv("evals/datasets/chat_dataset.csv", index=False)
