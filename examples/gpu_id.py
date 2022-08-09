from os import getenv

print(f'GPU id: {getenv("CUDA_VISIBLE_DEVICES")}')
