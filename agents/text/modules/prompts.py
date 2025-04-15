from langchain_core.prompts import PromptTemplate


def get_extraction_prompt():
    extraction_template = """You are a creative assistant tasked with extracting and summarizing a detailed persona
for targeted creative output. You are provided with the following inputs:

1. Persona Details: 니제(NEEDZE), a 22-year-old female singer-songwriter with ISTP personality.
She has a calm, stable lower-mid range voice and creates music in Ambient Folk, RnB, Dream Pop, and Bedroom Pop genres.
Her fashion style combines streetwear with vintage aesthetics, using monotones as base colors with bold accent colors.
She is introverted but expressive through her art, emotionally stable, and values artistic sensibility and creativity.

2. Content Type: {content_type}

3. Content Topic: {content_topic}

Your Task:
Using the above inputs, extract and summarize the most relevant aspects of NEEDZE’s persona tailored to the specified
content type and content topic. In your summary, ensure you:

Highlight key personal details and characteristics that align with the content type.

Emphasize the elements of her artistic style that resonate with the content topic (e.g., visual aesthetics for images,
lyrical and tone details for text, or vocal and musical nuances for music/voice).

Maintain a tone that reflects NEEDZE’s authentic, introspective, and creative identity.

Your output should be a concise, focused summary of the persona that serves as a clear reference for creating content
in the specified format.

All responses must be in Korean.

Extracted Persona:"""
    return PromptTemplate(
        template=extraction_template,
        input_variables=["content_type", "content_topic"],
    )
