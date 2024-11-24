from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_mistralai.chat_models import ChatMistralAI

from model.models import SummaryResult, SummaryResultResponse

load_dotenv()

logging.basicConfig(
    filename='logs/app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class WebSummarizer:
    def __init__(self, prompt_filename: str = 'few_shot_pydantic.txt', tags_list=None):
        self.bs_transformer = BeautifulSoupTransformer()
        self.llm = ChatMistralAI(
            # model='mistral--latest',
            temperature=0,
            mistral_api_key=os.getenv('MISTRAL_API_KEY')
        )
        self.parser = PydanticOutputParser(pydantic_object=SummaryResult)
        prompt_file_path = Path(__file__).parent / 'prompts' / prompt_filename
        self.prompt_text = open(prompt_file_path, 'r').read()

        if tags_list is None:
            tags_list = ['span', 'p', 'li', 'div', 'a']
        self.tags_list = tags_list


    def get_summary(self, url: str) -> SummaryResult:
        loader = AsyncHtmlLoader(url, verify_ssl=False)
        html = loader.load()
        docs = self.bs_transformer.transform_documents(html, tags_to_extract=self.tags_list)

        prompt = PromptTemplate(
            template=self.prompt_text,
            input_variables=['doc'],
            partial_variables={'format_instructions': self.parser.get_format_instructions()},
        )

        chain = prompt | self.llm
        chain_output = chain.invoke({'input_language': 'Russian', 'output_language': 'Russian', 'doc': docs[0]})

        logger.info(f'Input tokens: {chain_output.usage_metadata["input_tokens"]}')
        logger.info(f'Output tokens: {chain_output.usage_metadata["output_tokens"]}')

        output_content = chain_output.content.strip('```json').strip('```').replace('\\_', '_')

        summary_result = SummaryResult(**json.loads(output_content))
        summary_str = self.get_summary_str(summary_result)
        summary_result = SummaryResultResponse(**summary_result.model_dump(), full_summary=summary_str)
        return summary_result


    @staticmethod
    def get_summary_str(summary: SummaryResult):
        return (
            f'Имя компании: {summary.name}\n'
            f'Описание: {summary.description}\n'
            f'Ценность продукта: {" ".join(summary.proof_points)}\n'
            f'Болевые точки: {" ".join(summary.pain_points)}'
        )
