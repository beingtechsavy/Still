# Still

*"This is not an app. This is a ritual."*

A minimalist, mobile-first reflective experience facilitating a linear journey: Arrival → Voice Unloading → Stillness → Reflection → Closure.

## Architecture

- **Frontend**: Next.js (App Router), Tailwind CSS.
- **Backend**: FastAPI, Azure Speech Services, Azure OpenAI.
- **Infrastructure**: Azure Static Web Apps, Azure Container Apps.

## Development

### Frontend
```bash
cd web
npm install
npm run dev
```

### Backend
```bash
cd api
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
uvicorn main:app --reload
```
