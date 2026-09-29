import pytest

from westpa.cli.tools.w_progress import read_progress


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
