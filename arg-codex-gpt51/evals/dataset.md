使用 RAG 生成基于 RAG 的问答系统的合成测试集
概述
在本教程中，我们将探索 Ragas 中的测试集生成模块，为基于检索增强生成 (RAG) 的问答机器人创建一个合成测试集。我们的目标是设计一个 Ragas 航空助手，能够回答客户关于各种主题的咨询，包括：

航班预订
航班变更和取消
行李政策
查看预订
航班延误
机上服务
特别援助
为了确保我们的合成数据集尽可能真实且多样化，我们将创建不同的客户画像。每个画像代表不同的旅行者类型和行为，帮助我们构建全面且具有代表性的测试集。这种方法确保我们能够彻底评估 RAG 模型的有效性和稳健性。

我们开始吧！

下载和加载文档
运行以下命令下载虚拟的 Ragas Airline 数据集，并使用 LangChain 加载文档。

! git clone https://huggingface.co/datasets/vibrantlabsai/ragas-airline-dataset

from langchain_community.document_loaders import DirectoryLoader

path = "ragas-airline-dataset"
loader = DirectoryLoader(path, glob="\*_/_.md")
docs = loader.load()
建立 LLM 和嵌入模型

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import openai

generator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
openai_client = openai.OpenAI()
generator_embeddings = OpenAIEmbeddings(client=openai_client, model="text-embedding-3-small")
创建知识图谱
利用文档创建基础知识图谱

from ragas.testset.graph import KnowledgeGraph
from ragas.testset.graph import Node, NodeType

kg = KnowledgeGraph()

for doc in docs:
kg.nodes.append(
Node(
type=NodeType.DOCUMENT,
properties={"page_content": doc.page_content, "document_metadata": doc.metadata}
)
)

kg
输出

KnowledgeGraph(nodes: 8, relationships: 0)
设置变换
在本教程中，我们将使用完全由节点构建的知识图谱创建一个单跳查询数据集。为了增强我们的知识图谱并改进查询生成，我们应用了三个关键转换：

标题提取：使用语言模型从每个文档中提取清晰的章节标题（例如，从 flight cancellations.md 中提取“航空公司发起的航班取消” ）。这些标题突出特定主题，并为生成有针对性的问题提供直接的背景信息。
标题拆分：根据提取的标题将文档拆分为易于管理的子部分。这增加了节点数量，并确保生成更精细、更符合上下文的查询。
关键词提取：识别核心主题关键词（例如关键座位信息），作为语义种子点，丰富生成的查询的多样性和相关性。

from ragas.testset.transforms import apply_transforms
from ragas.testset.transforms import HeadlinesExtractor, HeadlineSplitter, KeyphrasesExtractor

headline_extractor = HeadlinesExtractor(llm=generator_llm, max_num=20)
headline_splitter = HeadlineSplitter(max_tokens=1500)
keyphrase_extractor = KeyphrasesExtractor(llm=generator_llm)

transforms = [
headline_extractor,
headline_splitter,
keyphrase_extractor
]

apply_transforms(kg, transforms=transforms)

Applying HeadlinesExtractor: 100%|██████████| 8/8 [00:00<?, ?it/s]
Applying HeadlineSplitter: 100%|██████████| 8/8 [00:00<?, ?it/s]
Applying KeyphrasesExtractor: 100%|██████████| 25/25 [00:00<?, ?it/s]
配置用于查询生成的用户角色
用户画像提供了背景信息和视角，确保生成的查询自然流畅、针对特定用户且多样化。通过针对不同的用户视角定制查询，我们的测试集涵盖了广泛的场景：

首次乘机指南：生成包含详细分步指导的查询，满足需要清晰说明的新手的需求。
常旅客：为经验丰富的旅行者提供简洁、高效的查询。
愤怒的商务舱乘客：以严厉、紧急的语气提出问题，反映出很高的期望和立即解决问题的要求。

from ragas.testset.persona import Persona

persona_first_time_flier = Persona(
name="First Time Flier",
role_description="Is flying for the first time and may feel anxious. Needs clear guidance on flight procedures, safety protocols, and what to expect throughout the journey.",
)

persona_frequent_flier = Persona(
name="Frequent Flier",
role_description="Travels regularly and values efficiency and comfort. Interested in loyalty programs, express services, and a seamless travel experience.",
)

persona_angry_business_flier = Persona(
name="Angry Business Class Flier",
role_description="Demands top-tier service and is easily irritated by any delays or issues. Expects immediate resolutions and is quick to express frustration if standards are not met.",
)

personas = [persona_first_time_flier, persona_frequent_flier, persona_angry_business_flier]
使用合成器生成查询
合成器负责将丰富的节点和角色转换为查询。它们通过选择节点属性（例如，“实体”或“关键词”），将其与角色、风格和查询长度配对，然后使用 LLM 根据节点内容生成查询-答案对来实现这一点。

使用两个实例 SingleHopSpecificQuerySynthesizer 来定义查询分布：

基于标题的合成器– 使用提取的文档标题生成查询，从而生成引用特定部分的结构化问题。
基于关键词的合成器——围绕关键概念形成查询，生成更广泛的主题性问题。
两个合成器的权重相同（各为 0.5），确保具体查询和概念查询的平衡组合，最终增强测试集的多样性。

from ragas.testset.synthesizers.single_hop.specific import (
SingleHopSpecificQuerySynthesizer,
)

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
测试集生成

from ragas.testset import TestsetGenerator

generator = TestsetGenerator(
llm=generator_llm,
embedding_model=generator_embeddings,
knowledge_graph=kg,
persona_list=personas,
)
现在我们可以生成测试集了。

testset = generator.generate(testset_size=10, query_distribution=query_distibution)
testset.to_pandas()

Generating Scenarios: 100%|██████████| 2/2 [00:00<?, ?it/s]
Generating Samples: 100%|██████████| 10/10 [00:00<?, ?it/s]
输出
用户输入 参考上下文 参考 合成器名称
0 如果我的行李延误、丢失或……我该怎么办？ 【行李政策】本部分提供…… 如果您的行李延误、丢失或损坏，…… 单跳特定查询合成器
1 航空公司在飞行期间提供哪些帮助？ 航班延误\n\n 航班延误可能由以下原因造成…… 根据延迟时间的长短，Ragas Ai... 单跳特定查询合成器
2 第一步：在特定情况下检查票价规则…… 航班取消\n\n 航班取消... 第一步：查看票价规则需要登录…… 单跳特定查询合成器
3 我如何才能在 Ragas 网站上查看我的预订信息？ [管理预订\n\n 管理您的预订... 要在线访问您的 Ragas Airli 预订... 单跳特定查询合成器
4 Ragas Airlines 提供哪些援助？ [特别协助\n\nRagas 航空公司提供... Ragas Airlines 提供特殊协助服务…… 单跳特定查询合成器
5 如果我的行李延误了，我应该采取哪些步骤？ 【行李政策】本节提供详细信息…… 如果您的行李延误、丢失或损坏…… 单跳特定查询合成器
6 我该如何重新提交行李索赔申请？ 【行李潜在问题及解决方案……】 如需重新提交行李问题索赔，…… 单跳特定查询合成器
7 航班延误的主要原因是什么？ 航班延误 航班延误可能由以下原因造成…… 航班延误可能是由天气状况造成的…… 单跳特定查询合成器
8 我如何申请报销额外费用？ [2. 因延误而产生的额外费用…… 申请报销额外费用…… 单跳特定查询合成器
9 乘客发起的取消属于什么情况？ 航班取消 航班取消可能…… 乘客主动取消航班的情况是指…… 单跳特定查询合成器
最后想说的话
在本教程中，我们探讨了如何使用 Ragas 库生成测试集，主要侧重于单跳查询。在接下来的教程中，我们将深入研究多跳查询，并扩展这些概念，以涵盖更丰富的测试集场景。
