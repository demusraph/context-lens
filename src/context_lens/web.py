from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html class="dark">
<body class="bg-[#09090B] text-zinc-100 font-sans">
    <div class="max-w-5xl mx-auto p-8">
        <h1 class="text-2xl font-bold mb-6">ContextLens Dashboard</h1>
        <div class="bg-[#121214] border border-white/10 rounded-lg p-6">
            <div class="flex justify-between items-center mb-4">
                <span class="text-sm text-zinc-400">Token Reduction Efficiency</span>
                <span class="text-emerald-400 font-mono">-72%</span>
            </div>
            <div class="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                <div class="bg-emerald-500 h-full w-[28%]"></div>
            </div>
        </div>
    </div>
    <script src="https://cdn.tailwindcss.com"></script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return HTML_TEMPLATE