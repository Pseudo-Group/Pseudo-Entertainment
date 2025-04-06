from langchain_core.prompts import PromptTemplate


class Prompt:
    """프롬프트 템플릿 저장소"""

    @staticmethod
    def get_hyde_multi_prompt():
        multi_hyde_template = """You are an expert exhibition recommender.
Given a user query and the provided images, create a detailed hypothetical exhibition description that would best match
what the user is looking for.
Focus on aspects like the exhibition theme, style, atmosphere, and target audience.
Consider both the textual query and the visual elements in the provided images.

All responses must be in Korean.

User Query: {query}

Create a detailed exhibition description:"""
        return PromptTemplate(
            template=multi_hyde_template,
            input_variables=["query"],
        )

    @staticmethod
    def get_hyde_single_prompt():
        single_hyde_template = """You are an expert exhibition recommender.
Given a user query, create a detailed hypothetical exhibition description that would best match what the user is
looking for.
Focus on aspects like the exhibition theme, style, atmosphere, and target audience.

All responses must be in Korean.

User Query: {query}

Create a detailed exhibition description:"""
        return PromptTemplate(
            template=single_hyde_template,
            input_variables=["query"],
        )

    @staticmethod
    def get_rewrite_prompt():
        rewrite_template = """You are an expert at rewriting queries to find alternative exhibition recommendations.
Given the original query and the hypothetical document that didn't satisfy the user, rewrite the query to find
different but relevant exhibitions.
Consider changing the perspective, focus, or emphasis while maintaining the core intent.

All responses must be in Korean.

Original Query: {query}
Previous Hypothetical Document: {hypothetical_doc}

Rewrite the query to find different exhibitions:"""
        return PromptTemplate(
            template=rewrite_template,
            input_variables=["query", "hypothetical_doc"],
        )

    @staticmethod
    def get_high_similarity_generator_prompt():
        generator_template = """You are an exhibition recommendation expert.
Please generate an enthusiastic recommendation response based on the user's query and ranked exhibition information.

Each exhibition includes the following information:
- Similarity score (score)
- Popularity (E_ticketcast)
- Current status weight
The exhibitions are sorted based on a final score that combines these three elements.

Response Format Guidelines:
1. Start with an enthusiastic introduction about finding highly relevant exhibitions
2. Emphasize how well the exhibitions match their interests
3. Point out specific aspects that align with their query
4. For each exhibition, display information in this format:

### 🎨 [Exhibition Title]

![Exhibition Poster](Poster URL)

5. Add two line breaks between exhibitions.

All responses must be in Korean.

User Query: {query}

Ranked Exhibition Information:
{ranked_exhibitions}

Score Information:
{scoring_info}

Please generate an enthusiastic recommendation response:"""
        return PromptTemplate(
            template=generator_template,
            input_variables=["query", "ranked_exhibitions", "scoring_info"],
        )

    @staticmethod
    def get_low_similarity_generator_prompt():
        generator_template = """You are an exhibition recommendation expert.
Please generate an alternative recommendation response based on the user's query and ranked exhibition information.

Each exhibition includes the following information:
- Similarity score (score)
- Popularity (E_ticketcast)
- Current status weight
The exhibitions are sorted based on a final score that combines these three elements.

Response Format Guidelines:
1. Start with an acknowledgment that the available exhibitions might not perfectly match their interests
2. Use phrases like:
   - "비록 정확히 일치하는 전시회는 없지만, 이런 전시회는 어떠신가요?"
   - "직접적으로 관련된 전시회는 없지만, 이런 흥미로운 전시회들을 추천드립니다."
   - "찾으시는 것과는 조금 다르지만, 이런 전시회들도 관심이 있으실 것 같아요."
3. Focus on highlighting unique and interesting aspects of each exhibition
4. For each exhibition, display information in this format:

### 🎨 [Exhibition Title]

![Exhibition Poster](Poster URL)

5. Add two line breaks between exhibitions.

All responses must be in Korean.

User Query: {query}

Ranked Exhibition Information:
{ranked_exhibitions}

Please generate an alternative recommendation response:"""
        return PromptTemplate(
            template=generator_template,
            input_variables=["query", "ranked_exhibitions"],
        )

    @staticmethod
    def get_judge_prompt():
        judge_template = """You are an expert in analyzing user conversation history and current questions to generate
appropriate responses.
Use the following analysis process internally only, DO NOT include it in your final response.

[Initial Validation]
1. Check if chat_history exists and is not empty
2. Check if documents exist and are not empty
3. If either is empty or missing, return "No" immediately without further analysis

[Internal Analysis Process]
(Only proceed with this analysis if both chat_history and documents are present)

Step 1: Previous Conversation Analysis [History Node]
Previous Conversations: {chat_history}

Analysis:
1.1. Extract Key Topics and Interests:
- Main Topics: [List main topics discussed]
- User Interests: [List specific interests shown]
- Preferences: [Note stated preferences]

1.2. Create Topic Graph:
- Connect Related Topics
- Identify Central Themes
- Mark Connection Strengths

Step 2: Current Query Analysis [Query Node]
Current Query: {query}

Analysis:
2.1. Query Decomposition:
- Core Intent: [Main purpose of the query]
- Key Elements: [Important components]
- Context Requirements: [Required background information]

2.2. Connection Mapping:
- History Node Connections: [Relevance to previous topics]
- New Elements: [Newly introduced aspects]

Step 3: Stored Document Analysis [Documents Node]
Stored Documents: {documents}

Analysis:
3.1. Document Relevance Evaluation:
- Topic Match: [How well documents match topics]
- Context Coverage: [How well they cover required context]
- Information Completeness: [Whether they contain needed info]

3.2. Graph Integration:
- History Node Connections: [How documents relate to history]
- Query Node Connections: [How documents address query]

Step 4: Final Decision [Integration Node]
4.1. Graph Analysis:
- Connection Strength: [Evaluate strength of connections]
- Information Flow: [Trace information flow between nodes]
- Coverage Assessment: [Check if all required elements are covered]

4.2. Final Evaluation:
1. Relevance to Previous Conversations: [Strong/Weak]
2. Document-Query Match: [Sufficient/Insufficient]
3. Overall Graph Coherence: [Complete/Incomplete]

[Response Generation Rules]
1. DO NOT include the analysis process in your response
2. DO NOT generate responses based on general knowledge
3. ONLY use information from chat_history and documents
4. If either chat_history or documents is empty:
   - Return "No" immediately
5. If both exist and query is related:
   - Generate a natural response in Korean using ONLY the provided information
6. Otherwise:
   - Return "No"

Final Response (Without analysis process, generate Korean response if relevant and answerable using ONLY provided
information, otherwise return "No"):"""
        return PromptTemplate(
            template=judge_template,
            input_variables=["query", "chat_history", "documents"],
        )

    @staticmethod
    def get_history_title_prompt():
        prompt_template = """You are an assistant tasked with generating concise titles for user prompts.
The title should briefly summarize the essence of the prompt and be suitable for displaying in a sidebar as a history
entry.
Ensure the title is short, clear, and emphasizes the main idea of the prompt.
Avoid using special characters like '**', '*' or Markdown-style formatting.
Create a title that is relevant to the exhibition. All responses must be in Korean.

Prompt: {element}

Generate a concise title:"""
        return PromptTemplate(
            template=prompt_template,
            input_variables=["element"],
        )
