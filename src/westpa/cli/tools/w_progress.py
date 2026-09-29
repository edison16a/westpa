'''Live progress dashboard for a running WESTPA simulation.'''

import os

from westpa.core.h5io import WESTPAH5File


def read_progress(we_h5filename):
    '''Return a dict of progress info from ``we_h5filename``.'''

    # w_run keeps west.h5 locked while it runs. Open without locking and read
    # whatever was last flushed.
    with WESTPAH5File(we_h5filename, 'r', locking=False) as h5file:
        n_iter = int(h5file.attrs['west_current_iteration'])
        n_completed = max(n_iter - 1, 0)

    return {
        'mtime': os.path.getmtime(we_h5filename),
        'n_iter': n_iter,
        'n_completed': n_completed,
    }
