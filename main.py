import logging
import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from routers.vlr_router import router as vlr_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vlr_api.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VLR.GG API by Nan (Modified by 9nan)",
    description="An Unofficial REST API for [vlr.gg](https://www.vlr.gg/), a site for Valorant Esports match and news coverage. Originally made by [Nan](https://github.com/axsddlr), modified and enhanced by [9nan](https://github.com/9nan)",
    docs_url="/",
    redoc_url=None,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "syntaxHighlight.theme": "agate",
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
        "requestSnippetsEnabled": True,
        "customCssUrl": "/static/custom.css",
        "requestSnippets": {
            "generators": {
                "curl_bash": {
                    "title": "cURL (bash)",
                    "syntax": "bash"
                },
                "curl_powershell": {
                    "title": "cURL (PowerShell)",
                    "syntax": "powershell"
                },
                "curl_cmd": {
                    "title": "cURL (CMD)",
                    "syntax": "bash"
                }
            }
        }
    },
    version="2.0.1"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(vlr_router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "VLR.GG API is running"}

@app.get("/custom.css", include_in_schema=False)
async def custom_css():
    """Custom CSS for dark theme enhancement"""
    css_content = """
    /* Dark theme enhancements */
    .swagger-ui {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    .swagger-ui .topbar {
        background-color: #2d2d2d !important;
        border-bottom: 1px solid #404040 !important;
    }
    
    .swagger-ui .topbar .download-url-wrapper {
        background-color: #2d2d2d !important;
    }
    
    .swagger-ui .info {
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
    }
    
    .swagger-ui .scheme-container {
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
    }
    
    .swagger-ui .opblock {
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
    }
    
    .swagger-ui .opblock .opblock-summary {
        background-color: #2d2d2d !important;
        border-bottom: 1px solid #404040 !important;
    }
    
    .swagger-ui .opblock .opblock-summary:hover {
        background-color: #3d3d3d !important;
    }
    
    .swagger-ui .opblock.opblock-get {
        border-color: #61affe !important;
    }
    
    .swagger-ui .opblock.opblock-post {
        border-color: #49cc90 !important;
    }
    
    .swagger-ui .opblock.opblock-put {
        border-color: #fca130 !important;
    }
    
    .swagger-ui .opblock.opblock-delete {
        border-color: #f93e3e !important;
    }
    
    .swagger-ui .btn {
        background-color: #404040 !important;
        border-color: #404040 !important;
        color: #ffffff !important;
    }
    
    .swagger-ui .btn:hover {
        background-color: #505050 !important;
        border-color: #505050 !important;
    }
    
    .swagger-ui .btn.execute {
        background-color: #49cc90 !important;
        border-color: #49cc90 !important;
    }
    
    .swagger-ui .btn.execute:hover {
        background-color: #5dd4a0 !important;
        border-color: #5dd4a0 !important;
    }
    
    .swagger-ui input[type="text"], 
    .swagger-ui input[type="password"], 
    .swagger-ui input[type="email"], 
    .swagger-ui input[type="url"], 
    .swagger-ui input[type="tel"], 
    .swagger-ui input[type="search"], 
    .swagger-ui input[type="number"], 
    .swagger-ui textarea, 
    .swagger-ui select {
        background-color: #1a1a1a !important;
        border: 1px solid #404040 !important;
        color: #ffffff !important;
    }
    
    .swagger-ui input[type="text"]:focus, 
    .swagger-ui input[type="password"]:focus, 
    .swagger-ui input[type="email"]:focus, 
    .swagger-ui input[type="url"]:focus, 
    .swagger-ui input[type="tel"]:focus, 
    .swagger-ui input[type="search"]:focus, 
    .swagger-ui input[type="number"]:focus, 
    .swagger-ui textarea:focus, 
    .swagger-ui select:focus {
        border-color: #61affe !important;
        box-shadow: 0 0 0 2px rgba(97, 175, 254, 0.2) !important;
    }
    
    .swagger-ui .response-col_status {
        background-color: #2d2d2d !important;
    }
    
    .swagger-ui .response-col_links {
        background-color: #2d2d2d !important;
    }
    
    .swagger-ui .response-col_description__inner {
        background-color: #2d2d2d !important;
    }
    
    .swagger-ui .highlight-code {
        background-color: #1a1a1a !important;
    }
    
    .swagger-ui .highlight-code pre {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Custom VLR.GG branding */
    .swagger-ui .topbar .topbar-wrapper .link {
        content: "🎮 VLR.GG API" !important;
    }
    
    .swagger-ui .topbar .topbar-wrapper .link::after {
        content: " - High Performance Valorant Esports API" !important;
        font-size: 14px !important;
        color: #61affe !important;
    }
    """
    
    from fastapi.responses import Response
    return Response(content=css_content, media_type="text/css")

# Add static file serving for CSS
from fastapi.staticfiles import StaticFiles
import os

# Create static directory if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")

# Write CSS to static file
css_file_path = "static/custom.css"
with open(css_file_path, "w", encoding="utf-8") as f:
    f.write("""
    /* Dark theme enhancements */
    .swagger-ui {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    .swagger-ui .topbar {
        background-color: #2d2d2d !important;
        border-bottom: 1px solid #404040 !important;
    }
    
    .swagger-ui .topbar .download-url-wrapper {
        background-color: #2d2d2d !important;
    }
    
    .swagger-ui .info {
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
    }
    
    .swagger-ui .scheme-container {
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
    }
    
    .swagger-ui .opblock {
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
    }
    
    .swagger-ui .opblock .opblock-summary {
        background-color: #2d2d2d !important;
        border-bottom: 1px solid #404040 !important;
    }
    
    .swagger-ui .opblock .opblock-summary:hover {
        background-color: #3d3d3d !important;
    }
    
    .swagger-ui .opblock.opblock-get {
        border-color: #61affe !important;
    }
    
    .swagger-ui .opblock.opblock-post {
        border-color: #49cc90 !important;
    }
    
    .swagger-ui .opblock.opblock-put {
        border-color: #fca130 !important;
    }
    
    .swagger-ui .opblock.opblock-delete {
        border-color: #f93e3e !important;
    }
    
    .swagger-ui .btn {
        background-color: #404040 !important;
        border-color: #404040 !important;
        color: #ffffff !important;
    }
    
    .swagger-ui .btn:hover {
        background-color: #505050 !important;
        border-color: #505050 !important;
    }
    
    .swagger-ui .btn.execute {
        background-color: #49cc90 !important;
        border-color: #49cc90 !important;
    }
    
    .swagger-ui .btn.execute:hover {
        background-color: #5dd4a0 !important;
        border-color: #5dd4a0 !important;
    }
    
    .swagger-ui input[type="text"], 
    .swagger-ui input[type="password"], 
    .swagger-ui input[type="email"], 
    .swagger-ui input[type="url"], 
    .swagger-ui input[type="tel"], 
    .swagger-ui input[type="search"], 
    .swagger-ui input[type="number"], 
    .swagger-ui textarea, 
    .swagger-ui select {
        background-color: #1a1a1a !important;
        border: 1px solid #404040 !important;
        color: #ffffff !important;
    }
    
    .swagger-ui input[type="text"]:focus, 
    .swagger-ui input[type="password"]:focus, 
    .swagger-ui input[type="email"]:focus, 
    .swagger-ui input[type="url"]:focus, 
    .swagger-ui input[type="tel"]:focus, 
    .swagger-ui input[type="search"]:focus, 
    .swagger-ui input[type="number"]:focus, 
    .swagger-ui textarea:focus, 
    .swagger-ui select:focus {
        border-color: #61affe !important;
        box-shadow: 0 0 0 2px rgba(97, 175, 254, 0.2) !important;
    }
    
    .swagger-ui .response-col_status {
        background-color: #2d2d2d !important;
    }
    
    .swagger-ui .response-col_links {
        background-color: #2d2d2d !important;
    }
    
    .swagger-ui .response-col_description__inner {
        background-color: #2d2d2d !important;
    }
    
    .swagger-ui .highlight-code {
        background-color: #1a1a1a !important;
    }
    
    .swagger-ui .highlight-code pre {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Custom VLR.GG branding */
    .swagger-ui .topbar .topbar-wrapper .link {
        content: "🎮 VLR.GG API" !important;
    }
    
    .swagger-ui .topbar .topbar-wrapper .link::after {
        content: " - High Performance Valorant Esports API" !important;
        font-size: 14px !important;
        color: #61affe !important;
    }
    """)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting VLR.GG API server...")
    # Initialize the global VLR client
    from api.async_client import get_vlr_client
    await get_vlr_client()
    logger.info("VLR client initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down VLR.GG API server...")

if __name__ == "__main__":
    # Configure uvicorn for better performance
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=3001,
        workers=1,  # Single worker for async operations
        loop="asyncio",
        access_log=True,
        log_level="info",
        reload=False  # Disable reload in production
    )
