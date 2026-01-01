# Backend Deployment Checklist

## Issues Fixed:
✅ Added FFmpeg installation to build command
✅ Added all required environment variables to render.yaml
✅ Updated CORS to allow deployed frontend domains
✅ Added rootDir: api to specify correct directory

## Root Cause of Error:
The error "Root directory 'reflector.py' does not exist" happened because:
- Render was looking for files in the repository root
- Your Python files are in the `api/` subdirectory
- Added `rootDir: api` to the render.yaml config

## Required Environment Variables:
You need to set these in your Render dashboard:

### Azure OpenAI (Required)
- `OPENAI_API_KEY` - Your Azure OpenAI API key
- `OPENAI_API_BASE` - Your Azure OpenAI endpoint (e.g., https://your-resource.openai.azure.com/)
- `OPENAI_DEPLOYMENT_NAME` - Your model deployment name

### Azure Speech Service (Required)
- `SPEECH_KEY` - Your Azure Speech Service key
- `SPEECH_REGION` - Your Azure region (e.g., eastus)

### Azure Blob Storage (Optional - has fallback)
- `AZURE_STORAGE_CONNECTION_STRING` - Your Azure Storage connection string

## Deployment Steps:
1. Push these changes to your repository
2. In Render dashboard, go to your service settings
3. Add the environment variables listed above
4. Redeploy the service

## Testing:
- Health check: `GET /health` should return `{"status": "still", "silence": True}`
- Main endpoint: `POST /process-audio` with audio file

## Common Issues:
- If transcription fails: Check SPEECH_KEY and SPEECH_REGION
- If reflection fails: Check OPENAI_API_KEY, OPENAI_API_BASE, and OPENAI_DEPLOYMENT_NAME
- If CORS errors: Frontend domain might not be in allowed origins list