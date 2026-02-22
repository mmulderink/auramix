# Rat Assistant App

This app connects to a running Rat Assistant backend and shows the animated canvas with a chat log.

## Run the backend

From the project root:

```bash
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

## Run the frontend

```bash
cd app
npm install
npm run dev -- --host
```

## Phone connection

1. Make sure your phone and computer are on the same Wi-Fi.
2. Find your computer's LAN IP (e.g., 192.168.1.10).
3. Set `VITE_WS_URL` to `ws://<LAN-IP>:8000/ws` in `app/.env`.
4. Open the Vite dev server URL on your phone.
