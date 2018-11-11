'''
A worker is a single processing unit
that fetches job from a list of jobs
unitl all jobs are done

Standalone module, cross-platform
'''

from os.path import join, dirname, isfile, expanduser
from argparse import ArgumentParser
from subprocess import run

import portalocker as ptl

def main():
    parser = ArgumentParser()
    parser.add_argument('job_list', type=str,
        help='List of jobs to execute')
    parser.add_argument('--counter-path', type=str, default=None,
        help='Path for shared counter (default to "job-counter.txt" in the job list folder)')
    # parser.add_argument('--work-dir', type=str,
    #     help='Working directory')
    opts = parser.parse_args()
    path_list = ['job_list', 'counter_path']
    for p in path_list:
        if opts.__dict__[p]:
            opts.__dict__[p] = expanduser(opts.__dict__[p])
    if opts.counter_path is None:
        opts.counter_path = join(dirname(opts.job_list), 'job-counter.txt')
    if not isfile(opts.counter_path):
         with ptl.Lock(opts.counter_path, 'w') as f:
             f.write('0\n')

    error_list = []
    while True:
        # new jobs can be appended while running (but old jobs should not be removed!)
        with open(opts.job_list) as f:
            jobs = f.readlines()
            jobs = [j.strip() for j in jobs]
            jobs = list(filter(None, jobs))
            n_job = len(jobs)
        with ptl.Lock(opts.counter_path, 'r+') as f:
            cnt = int(f.read())
            if cnt >= n_job:
                break
            job = jobs[cnt]
            cnt += 1
            f.seek(0)
            f.write('%d\n' % cnt)
        print('Parscript worker: working on job %d/%d' % (cnt, n_job))
        status = run(job)
        if status.returncode:
            # job id is one-based
            error_list.append((cnt, job))
    
    if error_list:
        print('Parscript worker: finished all jobs in "%s"' % opts.job_list)
        print('Parscript worker: following jobs contain error:')
        print(error_list)
    else:
        print('Parscript worker: finished all jobs in "%s" without error' % opts.job_list)

if __name__ == '__main__':
    main()