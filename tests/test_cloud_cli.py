from pathlib import Path
from types import SimpleNamespace
import json

import pytest

from test_model_access import credential,fake_credentials
from test_dashboard_jobs import configured_source


def test_cli_cloud_is_explicit_and_private(tmp_path,monkeypatch,fake_credentials,capsys):
    from apishield.cli import main
    raw=tmp_path/'private.json';raw.write_bytes(credential())
    config=configured_source(tmp_path)
    captured=[]
    def run(config,operation,store,**kwargs):
        captured.append(kwargs['model_connection'])
        return {'status':'needs_input'}
    monkeypatch.setattr('apishield.engine.run_job',run)
    assert main(['repair','--config',str(config),'--jobs-dir',str(tmp_path/'jobs'),
                 '--provider','google_cloud','--credentials',str(raw)])==2
    assert captured[0].provider=='google_cloud'
    for path in (tmp_path/'jobs').rglob('*'):
        if path.is_file():
            assert b'PRIVATE-FIXTURE' not in path.read_bytes() and str(raw).encode() not in path.read_bytes()
    assert 'PRIVATE-FIXTURE' not in capsys.readouterr().out


@pytest.mark.parametrize('flags',[['--provider','google_cloud'],['--provider','developer','--credentials','private.json'],
                                ['--candidate','offline.json','--provider','google_cloud','--credentials','private.json']])
def test_cli_rejects_incompatible_provider_flags(flags,tmp_path):
    from apishield.cli import main
    with pytest.raises(SystemExit) as failure:
        main(['repair','--config','unused.json','--jobs-dir',str(tmp_path/'jobs'),*flags])
    assert failure.value.code==2


def test_live_instrumentation_refuses_thirteenth_call_and_restores_client(tmp_path,monkeypatch):
    from research.live_quality import instrument_calls
    from google.genai.models import Models
    from google.genai.types import GenerateContentConfig
    invoked=[];calls=[]
    def generate(self,**kwargs):
        invoked.append(True)
        return SimpleNamespace(text='{}',usage_metadata=None)
    monkeypatch.setattr(Models,'generate_content',generate)
    with instrument_calls(tmp_path,calls):
        for _ in range(12):
            Models.generate_content(None,model='fixture',contents='synthetic',config=GenerateContentConfig(max_output_tokens=4096))
        with pytest.raises(ValueError,match='12'):
            Models.generate_content(None)
    assert len(invoked)==len(calls)==12 and Models.generate_content is generate


def test_live_records_safe_failure_and_restores_after_write_failure(tmp_path,monkeypatch):
    from research import live_quality
    from google.genai.models import Models
    from google.genai.types import GenerateContentConfig
    def generate(self,**kwargs): raise RuntimeError('PRIVATE-TOKEN')
    monkeypatch.setattr(Models,'generate_content',generate)
    calls=[]
    with live_quality.instrument_calls(tmp_path,calls):
        with pytest.raises(RuntimeError):
            Models.generate_content(None,model='fixture',contents='synthetic',config=GenerateContentConfig())
    assert 'PRIVATE-TOKEN' not in json.dumps(calls)
    assert Models.generate_content is generate
    monkeypatch.setattr(live_quality,'atomic_json',lambda *args:(_ for _ in ()).throw(OSError('disk unavailable')))
    with pytest.raises(OSError):
        with live_quality.instrument_calls(tmp_path,[]):
            Models.generate_content(None,model='fixture',contents='synthetic',config=GenerateContentConfig())
    assert Models.generate_content is generate


@pytest.mark.parametrize('diagnostic',['billing_address is missing from function inputs','Provider refuses this request','Cannot collect selected test'])
def test_abstention_requires_review_of_generated_diagnostic(diagnostic):
    from research.live_quality import accepted_outcome
    item={'status':'needs_input','calls':1,'error':diagnostic,'source_unchanged':True,'held_out_passed':None}
    assert accepted_outcome(item,abstain=True) is None
    assert accepted_outcome({**item,'calls':0},abstain=True) is False
    assert accepted_outcome({**item,'source_unchanged':False},abstain=True) is False
    assert accepted_outcome({**item,'status':'validated','held_out_passed':True},abstain=True) is False
    assert accepted_outcome({**item,'status':'validated','held_out_passed':True},abstain=False) is True
