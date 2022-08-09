'''
Automatically launch workers given the job list and GPU settings.
Can only be run on a single machine (compute node)

Standalone module, cross-platform
'''

from os import remove, getenv
from os.path import join, dirname, realpath, splitext, expanduser, isfile
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
    parser.add_argument('-g', '--n-gpu', type=int, default=1,
        help='Number of GPUs')
    parser.add_argument('-w', '--n-worker-per-gpu', type=int, default=1,
        help='Number of workers per each GPU')        
    opts = parser.parse_args()

    # need to create the counter files before-hand to prevent race condition
    path_list = ['job_list']
    for p in path_list:
        if opts.__dict__[p]:
            opts.__dict__[p] = expanduser(opts.__dict__[p])
    no_ext = splitext(opts.job_list)[0]
    start_counter = no_ext + '-start.txt'
    finish_counter = no_ext + '-finish.txt'
    
    if opts.reset:
        if isfile(start_counter):
            remove(start_counter)
        if isfile(finish_counter):
            remove(finish_counter)
        print('Counters have been reset for "%s"' % opts.job_list)
        return

    if not isfile(start_counter):
         with open(start_counter, 'w') as f:
             f.write('0\n')
    if not isfile(finish_counter):
         with open(finish_counter, 'w') as f:
             f.write('0\n')

    # get CUDA_VISIBLE_DEVICES if set
    CVD = getenv('CUDA_VISIBLE_DEVICES')
    if CVD:
        gpu_list = CVD.split(',')
        if opts.n_gpu > len(gpu_list):
            raise ValueError(f'The number of requested GPUs '
            f'({opts.n_gpu}) is more than the number of available GPUs '
            f'set by CUDA_VISIBLE_DEVICES ("{CVD}")')
        gpu_list = [int(x) for x in gpu_list]
    else:
        gpu_list = list(range(opts.n_gpu))
    
    workers = []
    for i in range(opts.n_gpu):
        workers += opts.n_worker_per_gpu*[[opts, gpu_list[i]]]
    pool = Pool(len(workers))
    list(pool.imap_unordered(worker_func, workers))

if __name__ == "__main__":
    main()
