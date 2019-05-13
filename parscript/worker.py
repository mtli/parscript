'''
A worker is a single processing unit
that fetches job from a list of jobs
unitl all jobs are done

Standalone module, cross-platform
'''

from platform import system
from os import remove
from os.path import join, isfile, expanduser, splitext
from argparse import ArgumentParser
from subprocess import run

import portalocker as ptl

def main():
    parser = ArgumentParser()
    parser.add_argument('job_list', type=str,
        help='List of jobs to execute')
    parser.add_argument('-r', '--reset', action='store_true', default=False,
        help='Reset counters for a given job list')
    parser.add_argument('-s', '--shutdown', action='store_true', default=False,
        help='Power off the machine when all jobs are done')
    opts = parser.parse_args()
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
         with ptl.Lock(start_counter, 'w') as f:
             f.write('0\n')
    if not isfile(finish_counter):
         with ptl.Lock(finish_counter, 'w') as f:
             f.write('0\n')

    error_list = []
    while True:
        # new jobs can be appended while running (but old jobs should not be removed!)
        with open(opts.job_list) as f:
            jobs = f.readlines()
            jobs = [j.strip() for j in jobs]
            jobs = list(filter(None, jobs))
            n_job = len(jobs)
        with ptl.Lock(start_counter, 'r+') as f:
            n_start = int(f.read())
            if n_start >= n_job:
                break
            job = jobs[n_start]
            n_start += 1
            f.seek(0)
            f.write('%d\n' % n_start)
        print('Parscript worker: working on job %d/%d' % (n_start, n_job))
        status = run(job, shell=True)
        if status.returncode:
            # job id is one-based
            error_list.append((n_start, job))
        with ptl.Lock(finish_counter, 'r+') as f:
            n_finish = int(f.read())
            n_finish += 1
            f.seek(0)
            f.write('%d\n' % n_finish)        

    with ptl.Lock(finish_counter, 'r+') as f:
        # for unknown reasons, flag 'r' throws error sometimes, thus using 'r+' instead
        n_finish = int(f.read())
    is_all_done = n_finish >= n_job
    status_str = 'finished all jobs' if is_all_done else 'no unallocated jobs'
    print('Parscript worker: %s in "%s"' % (status_str, opts.job_list))
    if error_list:
        print('Parscript worker: following jobs contain error:')
        print(error_list)
    if is_all_done and opts.shutdown:
        # shut down in 1 minute
        if system() == 'Windows':
            # Windows
            run('shutdown /s /t 60')
        elif system() == 'Darwin':
            # MacOS
            run('sudo shutdown -h +1')
        else:
            # Linux
			# for unknown reasons, `run` will yield 'FileNotFoundError' under python 3.6
            from subprocess import call
            call(['sudo', 'shutdown', '-f', '-h', '-t', '1'])

if __name__ == '__main__':
    main()