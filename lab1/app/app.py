import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from model.web_summarizer import WebSummarizer
from model.models import SummaryResultResponse


load_dotenv()
app = FastAPI()

logging.basicConfig(
    filename='logs/app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class URLInput(BaseModel):
    url: str

    @classmethod
    @field_validator('url')
    def url_validator(cls, field):
        if not (field.startswith("http://") or field.startswith("https://")):
            logger.error(f'Invalid` URL format: {field}')
            raise HTTPException(status_code=400, detail='Invalid URL')

        return field

model = WebSummarizer()

@app.post('/summarize', response_model=SummaryResultResponse)
async def summarize_url(input_data: URLInput):
    """
    Get summary for company website.
    Get info for matching with leads and writing personalized emails using. Uses Mistral-7B

    Args:
        input_data: Company URL for summary

    Returns:
        SummaryResultResponse model with company name, description of product, proof points and paint points
    """
    url = input_data.url
    logger.info(f'Received URL: {url}')

    try:
        summary = model.get_summary(url)
        logger.info(f'Successfully summarized URL: {url}')

    except Exception as e:
        logger.error(f'Exception during processing URL: {url} - {e}')
        raise HTTPException(status_code=500, detail=f'Model failed to process URL: {e}')

    return summary
