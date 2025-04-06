import math

from agents.base_node import BaseNode
from agents.manager.modules.state import GraphState
from agents.manager.modules.chains import Chain
from agents.models import Model


"""아래는 전부 예시 코드들입니다."""
class Single2HyDENode(BaseNode):
    """가상의 문서를 생성하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Single2HyDENode"
        self.chain = Chain.set_hyde_chain(mode="single")

    def process(self, state: GraphState) -> GraphState:
        hypothetical_doc = self.chain.invoke({"query": state["query"]})
        return {"hypothetical_doc": hypothetical_doc}


class Multi2HyDENode(BaseNode):
    """가상의 문서를 생성하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Multi2HyDENode"
        self.chain = Chain.set_hyde_chain(mode="multi")

    def process(self, state: GraphState) -> GraphState:
        hypothetical_doc = self.chain.invoke(
            {"query": state["query"], "image": state["image"]}
        )
        return {"hypothetical_doc": hypothetical_doc}


class EmbedderNode(BaseNode):
    """문서 임베딩을 생성하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "EmbedderNode"
        self.model = Model.get_embedding_model()

    def process(self, state: GraphState) -> GraphState:
        embedding = self.model.embed_query(state["hypothetical_doc"])
        return {"embedding": embedding}


class MongoRetrieverNode(BaseNode):
    """MongoDB에서 유사한 문서를 검색하는 노드"""

    def __init__(
        self,
        exact=True,
        embedding_name="E_embedding",
        limit=15,
        collection=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = "MongoRetrieverNode"
        self.collection = collection
        self.exact = exact
        self.embedding_name = embedding_name
        self.limit = limit

    def process(self, state: GraphState) -> GraphState:
        # MongoDB에서 문서 검색
        pipeline = [
            {
                "$vectorSearch": {
                    "exact": self.exact,
                    "index": self.embedding_name,
                    "path": self.embedding_name,
                    "queryVector": state["embedding"],
                    "limit": self.limit,
                }
            },
            {
                "$project": {
                    "E_text": 1,
                    "E_original_id": 1,
                }
            },
        ]

        documents = list(self.collection.aggregate(pipeline))
        return {"documents": documents}


class MongoAggregationNode(BaseNode):
    """문서를 집계하는 노드"""

    def __init__(self, collection=None, **kwargs):
        super().__init__(**kwargs)
        self.name = "MongoAggregationNode"
        self.collection = collection

    def process(self, state: GraphState) -> GraphState:
        # reranked_documents에서 E_original_id 추출
        original_ids = [doc["E_original_id"] for doc in state["documents"]]

        # MongoDB 파이프라인 구성
        pipeline = [
            {"$match": {"_id": {"$in": original_ids}}},
            {
                "$project": {
                    "E_title": 1,
                    "E_context": 1,
                    "E_poster": 1,
                    "E_price": 1,
                    "E_place": 1,
                    "E_date": 1,
                    "E_link": 1,
                    "E_ticketcast": 1,
                }
            },
        ]

        # MongoDB에서 문서 검색
        aggregated_documents = list(self.collection.aggregate(pipeline))
        return {"aggregated_documents": aggregated_documents}


class SimilarityRerankerNode(BaseNode):
    """문서 유사도를 기반으로 재정렬하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "SimilarityRerankerNode"
        self.model = Model.get_rerank_model()

    def process(self, state: GraphState) -> GraphState:
        # 문서가 없는 경우 빈 리스트 반환
        if not state["aggregated_documents"]:
            return {"reranked_documents": []}

        # 텍스트 추출
        doc_texts = [doc["E_context"] for doc in state["aggregated_documents"]]

        # 재정렬 수행
        reranked_results = self.model.rerank(documents=doc_texts, query=state["query"])

        # 재정렬된 문서 생성
        reranked_documents = []
        for result in reranked_results:
            doc_index = result["index"] if isinstance(result, dict) else result.index
            doc = state["aggregated_documents"][doc_index].copy()
            doc["score"] = (
                result["relevance_score"]
                if isinstance(result, dict)
                else result.relevance_score
            )
            reranked_documents.append(doc)

        return {"reranked_documents": reranked_documents}


class PopularityRerankerNode(BaseNode):
    """인기도를 기반으로 재정렬하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "PopularityRerankerNode"

    def calculate_score(self, doc):
        """전시회 점수 계산"""
        try:
            # 1. 기본 유사도 점수 (0-1 범위)
            base_score = float(doc.get("score", 0))

            # 2. 인기도 정규화 (0-1 범위로 변환)
            popularity = int(doc.get("E_ticketcast", 0))
            # 인기도 로그 스케일링 (1을 더해 0 처리)
            log_popularity = math.log(popularity + 1)
            # 최대값을 10000으로 가정하고 정규화
            max_log_popularity = math.log(10001)  # 최대값보다 1 큰 값으로 설정
            normalized_popularity = log_popularity / max_log_popularity

            # 최종 점수 계산 (유사도 70%, 인기도 30%)
            final_score = base_score * 0.7 + normalized_popularity * 0.3

            return final_score
        except Exception as e:
            print(f"Error in calculate_score: {e}")
            return 0.0

    def process(self, state: GraphState) -> GraphState:
        try:
            # 각 문서에 대한 점수 계산
            docs_with_scores = []
            for doc in state["reranked_documents"]:
                score = self.calculate_score(doc)
                doc_with_score = doc.copy()
                doc_with_score["final_score"] = score
                docs_with_scores.append(doc_with_score)

            # 점수 기준으로 정렬
            sorted_docs = sorted(
                docs_with_scores, key=lambda x: x["final_score"], reverse=True
            )

            # 점수 정보 저장
            scoring_info = {
                "max_score": max(d["final_score"] for d in docs_with_scores),
                "min_score": min(d["final_score"] for d in docs_with_scores),
                "scores": {d["E_title"]: d["final_score"] for d in docs_with_scores},
            }

            return {
                "popularity_ranked_documents": sorted_docs,
                "scoring_info": scoring_info,
            }

        except Exception as e:
            print(f"Error in PopularityRerankerNode: {e}")
            return {
                "popularity_ranked_documents": state["aggregated_documents"],
                "scoring_info": {},
            }


class HighSimilarityGeneratorNode(BaseNode):
    """유사도가 높은 경우의 응답을 생성하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "HighSimilarityGeneratorNode"
        self.chain = Chain.set_high_similarity_generator_chain()

    def process(self, state: GraphState) -> GraphState:
        try:
            # LLM에 전달할 컨텍스트 준비
            context = {
                "query": state["query"],
                "ranked_exhibitions": state["popularity_ranked_documents"],
                "scoring_info": state["scoring_info"],
            }

            # 응답 생성
            response = self.chain.invoke(context)

            return {"response": response}

        except Exception as e:
            print(f"Error in HighSimilarityGeneratorNode: {e}")
            return {"response": "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."}


class LowSimilarityGeneratorNode(BaseNode):
    """유사도가 낮은 경우의 응답을 생성하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "LowSimilarityGeneratorNode"
        self.chain = Chain.set_low_similarity_generator_chain()

    def process(self, state: GraphState) -> GraphState:
        try:
            # LLM에 전달할 컨텍스트 준비
            context = {
                "query": state["query"],
                "ranked_exhibitions": state["reranked_documents"],
            }

            # 응답 생성
            response = self.chain.invoke(context)

            return {"response": response}

        except Exception as e:
            print(f"Error in LowSimilarityGeneratorNode: {e}")
            return {"response": "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."}


class ReWriterNode(BaseNode):
    """문서를 재작성하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ReWriterNode"

    def process(self, state: GraphState) -> GraphState:
        # rewrite 체인 실행
        chain = Chain.set_rewrite_chain()
        rewritten_doc = chain.invoke(
            {"query": state["query"], "hypothetical_doc": state["hypothetical_doc"]}
        )
        return {"hypothetical_doc": rewritten_doc}


class JudgeNode(BaseNode):
    """사용자 쿼리를 평가하고 Rerank 시키는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "JudgeNode"

    def process(self, state: GraphState) -> GraphState:
        # 쿼리 평가 로직 구현
        chain = Chain.set_judge_chain()
        judge_answer = chain.invoke(
            {
                "query": state["query"],
                "chat_history": state["chat_history"],
                "documents": state["documents"],
            },
        )
        return {"judge_answer": judge_answer}


class SupervisorNode(BaseNode):
    """입력 유형을 감지하고 적절한 처리 경로를 결정하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "SupervisorNode"

    def process(self, state: GraphState) -> GraphState:
        return
