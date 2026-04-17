#!/bin/bash
set -e

cd "$(dirname "$0")/openvla-oft" || exit 1
export PYTHONPATH="$(pwd):$PYTHONPATH"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate torchgpu || exit 1

python vla-scripts/deploy.py \
  --pretrained_checkpoint ../my_cobot_280_VLA/runs/openvla-7b+my_cobot_280_pi+b1+lr-0.0005+lora-r32+dropout-0.0--image_aug--2000_chkpt \
  --unnorm_key my_cobot_280_pi \
  --num_images_in_input 1 \
  --use_l1_regression True \
  --use_diffusion False \
  --use_film False \
  --use_proprio True \
  --lora_rank 32 \
  --center_crop True