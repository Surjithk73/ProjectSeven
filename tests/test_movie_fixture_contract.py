import json
from pathlib import Path
import runpy
import httpx


def test_public_hold_fixture_contains_required_v1_and_v2_fields(monkeypatch):
    root=Path(__file__).parents[1]
    monkeypatch.syspath_prepend(str(root/'demo/movie-client'))
    transport=httpx.MockTransport
    responses=[]
    def capture(handler):
        def handle(request):
            response=handler(request)
            if request.url.path=='/holds':responses.append(response.json())
            return response
        return transport(handle)
    monkeypatch.setattr(httpx,'MockTransport',capture)
    fixture=runpy.run_path(str(root/'demo/movie-client/tests/test_booking.py'))
    fixture['test_booking_preserves_exact_amount_destination_and_key']()
    def required(schema,value):
        for field in schema.get('required',[]):
            assert field in value, 'Public fixture omits required provider field: '+field
        for field,child in schema.get('properties',{}).items():
            if field in value and isinstance(value[field],dict):required(child,value[field])
    for version in [1,2]:
        doc=json.loads((root/f'demo/contracts/theatre-v{version}.json').read_text())
        required(doc['paths']['/holds']['post']['responses']['200']['content']['application/json']['schema'],responses[0])
