'''
Automatically launch workers given the job list and GPU settings.
Can only be run on a single machine (compute node)

Standalone module, cross-platform
'''

from os.path import join, dirname, realpath
from argparse import ArgumentParser
from subprocess import run
from multiprocessing import Pool

worker_path = join(dirname(realpath(__file__)), 'worker.py')


def worker_func(args):
    opts, gpu_id = args
    cmd = 'CUDA_VISIBLE_DEVICES=' + str(gpu_id) + ' python "' + worker_path + '" "' + opts.job_list + '"'
    if opts.shutdown:
        cmd += ' -s'
    run(cmd, shell=True)

def main():
    parser = ArgumentParser()
    parser.add_argument('job_list', type=str,
        help='List of jobs to execute')
    parser.add_argument('-r', '--reset', action='store_true', default=False,
        help='Reset counters for a given job list')
    parser.add_argument('-s', '--shutdown', action='store_true', default=False,
        help='Power off the machine when all jobs are done')
    parser.add_argument('--n-gpu', type=int, default=1,
        help='Number of GPUs')
    parser.add_argument('--n-worker-per-gpu', type=int, default=1,
        help='Number of workers per each GPU')        
    opts = parser.parse_args()

    if opts.reset:
        run(['python', worker_path, opts.job_list, '-r'])
        return

    workers = []
    for i in range(opts.n_gpu):
        workers += opts.n_worker_per_gpu*[[opts, i]]
    pool = Pool(len(workers))
    list(pool.imap_unordered(worker_func, workers))

if __name__ == "__main__":
    main()