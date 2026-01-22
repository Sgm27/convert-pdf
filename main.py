import base64
from playwright.async_api import async_playwright
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class HTMLContent(BaseModel):
    html_content: str
    print_background: bool = True

class HTMLConvertResponse(BaseModel):
    file_base64: str
    scroll_width: int
    scroll_height: int

@app.post("/convert", response_model=HTMLConvertResponse)
async def convert_html_to_pdf(content: HTMLContent):    
    async with async_playwright() as p:
        # Launch with args to improve font rendering
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--font-render-hinting=none',
                '--enable-font-antialiasing',
                '--disable-gpu',
            ]
        )
        
        page = await browser.new_page()

        await page.set_viewport_size({"width": 1280, "height": 720})

        await page.set_content(content.html_content, wait_until="networkidle")
        
        # Inject CSS to ensure proper font rendering and Windows-like appearance
        await page.add_style_tag(content="""
            @media print {
                * {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            }
            body {
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                text-rendering: optimizeLegibility;
            }
        """)

        scroll_size = await page.evaluate("""
            () => ({
                width: document.body.scrollWidth,
                height: document.body.scrollHeight
            })
        """)

        pdf_bytes = await page.pdf(
            width="13.33in",
            height="7.55in",
            print_background=content.print_background,
            prefer_css_page_size=False,
            display_header_footer=False,
            scale=1.0
        )

        await page.close()
        await browser.close()

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return HTMLConvertResponse(
        file_base64=pdf_base64,
        scroll_width=scroll_size["width"],
        scroll_height=scroll_size["height"]
    )