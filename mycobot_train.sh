#!/bin/bash
#SBATCH -p GPU
#SBATCH -N 1
#SBATCH -t 0-36:00
#SBATCH -o slurm.%N.%j.out
#SBATCH -e slurm.%N.%j.err
#SBATCH --gres=gpu:1

if [ -f "/usr/local/anaconda3/etc/profile.d/conda.sh" ]; then
    . "/usr/local/anaconda3/etc/profile.d/conda.sh"
else
    export PATH="/usr/local/anaconda3/bin:$PATH"
fi

source activate torchgpu
cd /path/to/openvla-oft

torchrun --standalone --nnodes 1 --nproc-per-node 1 vla-scripts/finetune.py \
  --data_root_dir /home/u818797/my_cobot_280_VLA/openvla-oft/prismatic/vla/datasets/rlds \
  --dataset_name MyCobot280_pi_training_dataset \
  --run_root_dir /home/u818797/my_cobot_280_VLA/runs \
  --batch_size 1 \
  --learning_rate 5e-4 \
  --max_steps 50000 \
  --use_lora True \
  --lora_rank 32