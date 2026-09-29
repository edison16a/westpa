'''Live progress dashboard for a running WESTPA simulation.'''

import os
from datetime import timedelta

import numpy as np

from westpa.core.h5io import WESTPAH5File
from westpa.core.segment import Segment


def read_progress(we_h5filename, max_total_iterations=None, n_recent=5):
    '''Return a dict of progress info from ``we_h5filename``.

    ETA is iterations left times the mean walltime of the last ``n_recent``
    iterations. None if ``max_total_iterations`` isn't set or nothing has
    finished yet.'''

    # w_run keeps west.h5 locked while it runs. Open without locking and read
    # whatever was last flushed.
    with WESTPAH5File(we_h5filename, 'r', locking=False) as h5file:
        n_iter = int(h5file.attrs['west_current_iteration'])
        n_completed = max(n_iter - 1, 0)
        summary = h5file['summary'][:n_completed]
        try:
            seg_status = h5file.get_iter_group(n_iter)['seg_index']['status']
        except KeyError:
            seg_status = np.empty((0,), dtype=np.uint8)

    # Ignore NaN and zero walltimes (truncated runs can leave these)
    walltimes = summary['walltime']
    recent_walltimes = walltimes[np.isfinite(walltimes) & (walltimes > 0)][-n_recent:]
    avg_walltime = float(recent_walltimes.mean()) if len(recent_walltimes) else None

    eta = None
    if max_total_iterations and avg_walltime is not None:
        eta = max(max_total_iterations - n_completed, 0) * avg_walltime

    return {
        'mtime': os.path.getmtime(we_h5filename),
        'n_iter': n_iter,
        'n_completed': n_completed,
        'max_total_iterations': max_total_iterations,
        'n_segs': len(seg_status),
        'n_complete': int(np.count_nonzero(seg_status == Segment.SEG_STATUS_COMPLETE)),
        'n_failed': int(np.count_nonzero(seg_status == Segment.SEG_STATUS_FAILED)),
        'n_particles': int(summary['n_particles'].sum()),
        'walltime': float(np.nansum(walltimes)),
        'recent_walltimes': recent_walltimes.tolist(),
        'avg_walltime': avg_walltime,
        'eta': eta,
    }


def _duration(seconds):
    '''Format seconds as H:MM:SS, or 'unknown' for None.'''
    if seconds is None:
        return 'unknown'
    return str(timedelta(seconds=round(seconds)))
