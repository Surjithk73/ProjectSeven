from pathlib import Path
import pytest


def test_environment_report_and_port_conflict(tmp_path):
    from demo.setup import environment_report
    import socket
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0)); listener.listen()
        report = environment_report([listener.getsockname()[1]])
    assert report['ports'][0]['available'] is False
    assert report['python']


def test_reset_refuses_unmanaged_or_dirty_source(tmp_path):
    from demo.setup import reset_rehearsal
    with pytest.raises(ValueError, match='managed'):
        reset_rehearsal(tmp_path)
    (tmp_path / '.apishield-demo-state').touch()
    (tmp_path / 'personal.txt').write_text('preserve')
    reset_rehearsal(tmp_path)
    assert (tmp_path / 'personal.txt').read_text() == 'preserve'


def test_baseline_export_preserves_shipping_files(tmp_path):
    from demo.setup import export_client
    (tmp_path / 'shipping.txt').write_text('keep')
    export_client(tmp_path)
    assert (tmp_path / 'shipping.txt').read_text() == 'keep'
    assert (tmp_path / 'movie_booking/app.py').is_file()
    assert (tmp_path / 'movie_booking/tests/test_booking.py').is_file()
    assert (tmp_path / '.github/workflows/cinema-client.yml').is_file()
    with pytest.raises(ValueError, match='exists'):
        export_client(tmp_path)


def test_service_ports_are_valid_and_distinct():
    from demo.setup import service_ports
    assert service_ports(8200, 8201, 8202) == (8200, 8201, 8202)
    for ports in [(8100, 8100, 8102), (0, 8101, 8102), (8100, 8101, 65536)]:
        with pytest.raises(ValueError, match='ports'):
            service_ports(*ports)
