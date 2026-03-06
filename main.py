import io
from PIL import Image

import base64
from playwright.async_api import async_playwright
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class HTMLContent(BaseModel):
    html_content: str
    print_background: bool = True


class HTMLMeasureResponse(BaseModel):
    scroll_width: int
    scroll_height: int


class HTMLConvertResponse(BaseModel):
    file_base64: str

async def load_page(html_content):
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()

    await page.set_content(html_content, wait_until="networkidle")

    return p, browser, page

@app.post("/measure", response_model=HTMLMeasureResponse)
async def measure_html(content: HTMLContent):
    try:
        p, browser, page = await load_page(content.html_content)

        scroll_size = await page.evaluate("""
            () => ({
                width: document.body.scrollWidth,
                height: document.body.scrollHeight
            })
        """)

        await page.close()
        await browser.close()
        await p.stop()

        return HTMLMeasureResponse(
            scroll_width=scroll_size["width"],
            scroll_height=scroll_size["height"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-pdf", response_model=HTMLConvertResponse)
async def convert_html_to_pdf(content: HTMLContent):
    try:
        p, browser, page = await load_page(content.html_content)

        image_bytes = await page.screenshot(full_page=True)

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pdf_buffer = io.BytesIO()
        image.save(pdf_buffer, format="PDF")

        pdf_bytes = pdf_buffer.getvalue()

        await page.close()
        await browser.close()
        await p.stop()

        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return HTMLConvertResponse(file_base64=pdf_base64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-image", response_model=HTMLConvertResponse)
async def convert_html_to_image(content: HTMLContent):
    try:
        p, browser, page = await load_page(content.html_content)

        image_bytes = await page.screenshot(
            full_page=True,
            type="png",
            omit_background=not content.print_background
        )

        await page.close()
        await browser.close()
        await p.stop()

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        return HTMLConvertResponse(file_base64=image_base64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)