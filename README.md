# Parscript: Parallel or distributed execution of jobs

Simple concept: write your jobs (shell, python, batch or anything!) in a txt file, one job one line!
```
python train.py --name=exp1 --param=1
python train.py --name=exp2 --param=2
python train.py --name=exp3 --param=3
```

And use `python -m parscript.worker job-list.txt` to run the jobs sequentially, or `python -m parscript.dispatcher job-list.txt` to run them in parallel or distributed fashion.

Usage:
- Specify the number of GPUs through `-g` (default 1)
- Specify the number of workers (per GPU) through `-w` (default 1)
- Reset the job counter through `-r`
- Directly edit `job-list.txt` after launched to add more jobs to it
- If one job fails, it will not affect other jobs and failed jobs will be recorded and reported at the end.
- Use `-s` to shutdown the machine after all jobs are finished (useful for running jobs on AWS).

For example:
`python -m parscript.dispatcher job-list.txt -g 4 -w 2` means running 8 jobs at a time from the job list using 4 GPUs with 2 jobs on each GPU.

Hint: for complicated jobs, you might want to write a job/script generator.


## Installation
```
pip install parscript
```
[![PyPI version](https://badge.fury.io/py/parscript.svg)](https://badge.fury.io/py/parscript)

Useful bash aliases (add them to `~/.bash_aliases`):
```
alias parworker='python -m parscript.worker'
alias pardispatch='python -m parscript.dispatcher'
```

