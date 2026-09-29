from datetime import datetime
import subprocess
import sys

import pytest

from westpa.cli.tools.w_progress import format_progress, read_progress


class Test_W_Progress:
    """Test class for w_progress tool."""

    def test_completed_run(self, ref_50iter):
        progress = read_progress(self.h5_filepath, max_total_iterations=50)

        assert progress['n_iter'] == 51
        assert progress['n_completed'] == 50
        assert progress['n_particles'] == 9985
        assert len(progress['recent_walltimes']) == 5
        assert progress['avg_walltime'] > 0
        assert progress['eta'] == 0

    def test_eta(self, ref_50iter):
        progress = read_progress(self.h5_filepath, max_total_iterations=60)

        assert progress['eta'] == pytest.approx(10 * progress['avg_walltime'])

    def test_initialized_run(self, ref_initialized):
        progress = read_progress(self.h5_filepath, max_total_iterations=2)

        assert progress['n_iter'] == 1
        assert progress['n_completed'] == 0
        assert progress['n_segs'] == 10
        assert progress['n_complete'] == 0
        assert progress['n_particles'] == 0
        assert progress['recent_walltimes'] == []
        assert progress['eta'] is None

    def test_file_open_for_writing(self, ref_50iter):
        # Lock west.h5 from another process like w_run does
        code = f"import h5py, time; f = h5py.File({self.h5_filepath!r}, 'r+'); print('ready', flush=True); time.sleep(60)"
        writer = subprocess.Popen([sys.executable, '-c', code], stdout=subprocess.PIPE, text=True)
        try:
            assert writer.stdout.readline().strip() == 'ready'
            progress = read_progress(self.h5_filepath)
        finally:
            writer.kill()
            writer.wait()

        assert progress['n_iter'] == 51

    def test_format_progress(self):
        progress = {
            'mtime': datetime(2026, 1, 2, 3, 4, 5).timestamp(),
            'n_iter': 37,
            'n_completed': 36,
            'max_total_iterations': 50,
            'n_segs': 100,
            'n_complete': 82,
            'n_failed': 2,
            'n_particles': 9985,
            'walltime': 642.0,
            'recent_walltimes': [12.4, 11.8, 13.1],
            'avg_walltime': 12.43,
            'eta': 174.07,
        }
        expected = """\
Last written:              2026-01-02 03:04:05
Current iteration:         37
Progress:                  36 / 50 iterations (72.0%)
Segments complete:         82 / 100
Segments failed:           2
Recent walltimes:          0:00:12, 0:00:12, 0:00:13
Avg iteration time:        0:00:12
Completed walltime:        0:10:42
Completed segments:        9985
ETA:                       0:02:54
"""
        assert format_progress(progress) == expected
