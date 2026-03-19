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
  --use_l1_regression True \
  --use_diffusion False \
  --use_film False \
  --num_images_in_input 1 \
  --use_proprio True \ 
  --batch_size 1 \
  --learning_rate 5e-4 \
  --num_steps_before_decay 25000 \
  --max_steps 50000 \
  --use_val_set True \ 
  --val_freq 5000 \
  --save_freq 5000 \
  --save_latest_checkpoint_only False \
  --image_aug True \
  --use_lora True \
  --lora_rank 32 \
  --wandb_entity "ishikurakei0717-tilburg-university" \
  --wandb_project "mycobot_openvla" \