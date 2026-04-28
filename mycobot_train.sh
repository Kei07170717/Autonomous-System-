#!/bin/bash
#SBATCH -p GPU
#SBATCH -N 1
#SBATCH -t 0-36:00
#SBATCH -o slurm.%N.%j.out
#SBATCH -e slurm.%N.%j.err
#SBATCH --gres=gpu:2

if [ -f "/usr/local/anaconda3/etc/profile.d/conda.sh" ]; then
    . "/usr/local/anaconda3/etc/profile.d/conda.sh"
else
    export PATH="/usr/local/anaconda3/bin:$PATH"
fi

DATASET_PATH="$1"

if [ -z "$DATASET_PATH" ]; then
    echo "Usage: $0 <path_to_dataset_root>"
    exit 1
fi

conda activate torchgpu
cd "/home/u818797/Project_git/openvla-oft" || exit 1
export PYTHONPATH="/home/u818797/Project_git/openvla-oft:$PYTHONPATH"

mkdir -p /home/u818797/my_cobot_280_VLA/runs_huge_dataset_v3

torchrun --standalone --nnodes 1 --nproc-per-node 2 vla-scripts/finetune.py \
  --data_root_dir "$DATASET_PATH" \
  --dataset_name my_cobot_280_pi \
  --run_root_dir /home/u818797/my_cobot_280_VLA/runs_huge_dataset_v3 \
  --use_l1_regression True \
  --use_diffusion False \
  --use_film False \
  --num_images_in_input 2 \
  --use_proprio True \
  --batch_size 2 \
  --learning_rate 5e-4 \
  --num_steps_before_decay 8000 \
  --grad_accumulation_steps 4 \
  --max_steps 10000 \
  --use_val_set True \
  --val_freq 250 \
  --save_freq 1000 \
  --save_latest_checkpoint_only False \
  --image_aug True \
  --use_lora True \
  --lora_rank 32 \
  --wandb_entity "ishikurakei0717-tilburg-university" \
  --wandb_project "mycobot_openvla"
