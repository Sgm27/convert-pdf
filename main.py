import base64
import os
from playwright.async_api import async_playwright
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class HTMLContent(BaseModel):
    html_content: str

class HTMLConvertResponse(BaseModel):
    file_base64: str

@app.post("/convert", response_model=HTMLConvertResponse)
async def convert_html_to_pdf(content: HTMLContent):    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_viewport_size({"width": 1280, "height": 720})

        await page.set_content(content.html_content, wait_until="networkidle")

        pdf_bytes = await page.pdf(
            width="13.33in",
            height="7.5in",
            print_background=True
        )

        await page.close()
        await browser.close()

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return HTMLConvertResponse(file_base64=pdf_base64)