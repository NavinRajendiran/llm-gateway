# Free LLM Gateway

**OpenAI-compatible API** that automatically routes requests across **all major free LLM providers** based on remaining quota, speed and priority.

Designed for easy deployment on **Render free tier**.

## Supported Providers (v1.1)

| Priority | Provider                  | Key Required | Notes                              |
|----------|---------------------------|--------------|------------------------------------|
| 100      | **Groq**                  | Yes          | Fastest                            |
| 95       | **Google Gemini**         | Yes          | Excellent free tier                |
| 90       | **OpenRouter Free**       | Yes          | Many `:free` models                |
| 85       | **Kilo Code**             | No           | Free pool, auto-router             |
| 80       | **LLM7.io**               | No           | Anonymous tier available           |
| 75       | **SiliconFlow**           | Yes          | Strong Chinese + open models       |
| 70       | **NVIDIA NIM**            | Yes          | 100+ models                        |
| 65       | **Cloudflare Workers AI** | Yes          | 10k neurons/day                    |
| 60       | **Aion Labs**             | Yes          | Roleplay / storytelling            |
| 55       | **Z AI (Zhipu)**          | Yes          | GLM models                         |
| 50       | **Cohere**                | Yes          | Non-commercial only                |
| 45       | **ModelScope**            | Yes          | Alibaba / Qwen heavy               |
| 40       | **Gonka Broker**          | Yes          | Rotating free models               |
| 35       | **OVHcloud**              | No           | EU, IP-based free tier             |

The gateway only uses providers for which you have provided a key (or that don't require one).

## Deploy on Render (Free)

1. Push this repository to GitHub
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New → Web Service**
3. Connect the repo (it will detect `render.yaml`)
4. Add the API keys you have in the **Environment** section
5. Deploy

You will get a URL like:
```
https://free-llm-gateway-xxxx.onrender.com
```

## Usage

```bash
export OPENAI_BASE_URL=https://your-service.onrender.com/v1
export OPENAI_API_KEY=your-gateway-key
```

Works with:
- OpenAI Python/JS SDK
- Cursor / Continue / Aider
- LangChain / LlamaIndex
- Any OpenAI-compatible client

### Example

```bash
curl https://your-service.onrender.com/v1/chat/completions \
  -H "Authorization: Bearer your-gateway-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Explain quantum computing simply"}],
    "max_tokens": 400
  }'
```

### Model selection
- `auto` or `free` → gateway picks the best currently available provider
- Specific model names (e.g. `llama-3.3-70b-versatile`, `gemini-2.5-flash`, etc.)

## Keep-alive (recommended)

Render free services sleep after 15 minutes of inactivity.  
Ping the health endpoint every 10–14 minutes with a free cron service:

```
GET https://your-service.onrender.com/health
```

## Local development

```bash
cp .env.example .env
# fill in at least 1-2 API keys
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Method | Path                     | Description                        |
|--------|--------------------------|------------------------------------|
| GET    | `/`                      | Status + active providers          |
| GET    | `/health`                | Health check                       |
| GET    | `/v1/models`             | List all available models          |
| POST   | `/v1/chat/completions`   | Chat completions (OpenAI format)   |
| GET    | `/stats`                 | Current quota usage per provider   |

---

Based on the excellent list: [awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis)
