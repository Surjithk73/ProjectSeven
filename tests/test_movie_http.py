"""Real HTTP/process boundary smoke; no AI response is fabricated here."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import httpx


def test_three_independent_http_services(tmp_path):
    root = Path(__file__).parents[1]
    sockets = [socket.socket() for _ in range(3)]
    for sock in sockets:
        sock.bind(('127.0.0.1', 0))
    ports = [sock.getsockname()[1] for sock in sockets]
    for sock in sockets:
        sock.close()
    urls = [f'http://127.0.0.1:{port}' for port in ports]
    env = {**os.environ, 'CINEMA_STATE_DIR': str(tmp_path), 'CINEMA_THEATRE_URL': urls[1],
           'CINEMA_PAYMENT_URL': urls[0], 'PYTHONPATH': os.pathsep.join([str(root), str(root / 'demo/movie-client')])}
    processes = []
    try:
        for module, port in zip(['demo.providers.payment', 'demo.providers.theatre', 'movie_booking.app'], ports):
            processes.append(subprocess.Popen([sys.executable, '-m', 'uvicorn', module + ':create_app', '--factory',
                '--host', '127.0.0.1', '--port', str(port)], cwd=root, env=env, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0))
        for url in urls:
            for attempt in range(80):
                try:
                    if httpx.get(url + '/health', timeout=.4, trust_env=False).status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(.1)
            else:
                raise AssertionError('Demo HTTP service did not start')
        response = httpx.get(urls[2] + '/', trust_env=False)
        assert response.status_code == 200 and 'CinemaFlow' in response.text
        response = httpx.post(urls[2] + '/api/bookings', json={'show_id': 'show-001', 'seat_ids': ['B2'], 'idempotency_key': 'http-booking'}, trust_env=False)
        assert response.status_code == 200, response.text
        assert response.json()['status'] == 'confirmed'
        smoke = httpx.post(urls[2] + '/internal/smoke', timeout=25, trust_env=False)
        assert smoke.status_code == 200, smoke.text
        assert smoke.json()['show_id'].startswith('smoke-')
        switched = httpx.post(urls[2] + '/api/providers/payment/version', json={'version': 2}, trust_env=False)
        assert switched.status_code == 200
        broken = httpx.post(urls[2] + '/api/bookings', json={'show_id': 'show-001', 'seat_ids': ['B3'], 'idempotency_key': 'http-v2'}, trust_env=False)
        assert broken.status_code == 502 and 'detail' in broken.json()
        assert broken.json()['detail'].startswith('Payment failed: GPay V2')
        assert httpx.get(urls[0] + '/openapi.json', trust_env=False).json()['info']['version'] == '2.0.0'
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            process.wait(timeout=10)
