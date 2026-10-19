"""Standalone CinemaFlow UI/BFF; providers remain separate HTTP processes."""
import os
from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from pydantic import BaseModel, Field

from .booking import BookingClient


class BookingRequest(BaseModel):
    show_id: str = Field(min_length=1, max_length=160)
    seat_ids: list[str] = Field(min_length=1, max_length=8)
    idempotency_key: str = Field(min_length=1, max_length=160)


def create_app():
    app = FastAPI(title='CinemaFlow')
    static = Path(__file__).parent / 'static'
    app.mount('/static', StaticFiles(directory=static), name='static')

    def provider(name):
        default = 'http://127.0.0.1:8101' if name == 'theatre' else 'http://127.0.0.1:8102'
        return os.environ.get(f'CINEMA_{name.upper()}_URL', default).rstrip('/')

    def local(request):
        import ipaddress
        try:
            allowed = ipaddress.ip_address(request.client.host).is_loopback
        except ValueError:
            allowed = request.client.host == 'testclient'
        if not allowed:
            raise HTTPException(403, 'Provider controls are local to this computer')
        from urllib.parse import urlsplit
        origin = request.headers.get('origin')
        if origin and urlsplit(origin).netloc != request.headers.get('host'):
            raise HTTPException(403, 'Cross-origin controls are blocked')

    @app.exception_handler(httpx.HTTPError)
    async def provider_error(request, error):
        response = getattr(error, 'response', None)
        detail = 'Provider connection failed; check that both provider services are running.'
        if response is not None:
            try:
                detail = response.json().get('detail', detail)
            except ValueError:
                pass
        return JSONResponse(status_code=502, content={'detail': detail, 'recovery': 'Open APIShield to check the active API contracts.'})

    @app.exception_handler(KeyError)
    async def contract_error(request, error):
        return JSONResponse(status_code=502, content={'detail': 'The provider response no longer matches this client.',
            'recovery': 'Check for API changes in APIShield, review the proposed update, and merge it to deploy.'})

    @app.get('/')
    def index():
        return FileResponse(static / 'index.html')

    @app.get('/health')
    def health():
        return {'status': 'ok', 'application': 'CinemaFlow', 'revision': os.environ.get('CINEMA_DEPLOYED_SHA', 'working-files'),
                'pid': os.getpid(), 'instance': os.environ.get('CINEMA_INSTANCE_ID', 'manual')}

    @app.get('/api/providers')
    def providers():
        results = []
        for name in ('theatre', 'payment'):
            try:
                response = httpx.get(provider(name) + '/health', timeout=3, trust_env=False)
                response.raise_for_status()
                results.append({'id': name, **response.json()})
            except httpx.HTTPError:
                results.append({'id': name, 'status': 'unreachable', 'version': None})
        return results

    @app.get('/api/shows')
    def shows():
        with httpx.Client(base_url=provider('theatre'), timeout=10, trust_env=False) as theatre:
            return BookingClient(theatre).theatre.list_shows()

    @app.get('/api/shows/{show_id}/seats')
    def seats(show_id: str):
        with httpx.Client(base_url=provider('theatre'), timeout=10, trust_env=False) as theatre:
            return BookingClient(theatre).theatre.get_seats(show_id)

    @app.post('/api/bookings')
    def book(body: BookingRequest):
        with httpx.Client(base_url=provider('theatre'), timeout=10, trust_env=False) as theatre, httpx.Client(
                base_url=provider('payment'), timeout=10, trust_env=False) as payment:
            return BookingClient(theatre, payment).book(body.show_id, body.seat_ids, body.idempotency_key)

    @app.post('/api/providers/{name}/version')
    def switch(name: str, body: dict, request: Request):
        local(request)
        if name not in {'theatre', 'payment'}:
            raise HTTPException(404, 'Unknown provider')
        response = httpx.post(provider(name) + '/admin/version', json=body, timeout=5, trust_env=False)
        response.raise_for_status()
        return response.json()

    @app.post('/internal/smoke')
    def smoke(request: Request):
        local(request)
        key = 'smoke-' + uuid.uuid4().hex
        with httpx.Client(base_url=provider('theatre'), timeout=10, trust_env=False) as theatre, httpx.Client(
                base_url=provider('payment'), timeout=10, trust_env=False) as payment:
            client = BookingClient(theatre, payment)
            shows = client.theatre.list_shows()
            if not shows or not isinstance(shows[0].get('id'), str):
                raise HTTPException(502, 'Deployed client cannot browse showtimes')
            client.theatre.get_seats(shows[0]['id'])
            available = client.theatre.get_seats(key)
            if not any(seat.get('id') == 'A1' and seat.get('available') is True for seat in available):
                raise HTTPException(502, 'Deployed client cannot read the isolated show seat availability')
            return client.book(key, ['A1'], key)

    return app
