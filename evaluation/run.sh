source /home/vagsart/src/novasplat/venv_novasplat/bin/activate
export PYTHONPATH=bop_toolkit 
export BOP_PATH=$(pwd)/data/bop_h3

for result_file in results/*.csv; do
    if [ ! -e "$result_file" ]; then
        continue
    fi
    filename=$(basename "$result_file")
    name_no_ext="${filename%.*}"
    
    targets_file="test_targets_classic.json"
    if [[ "$filename" == *"extended"* ]]; then
        targets_file="test_targets_extended.json"
    fi
    
    echo "=========================================================="
    echo "Evaluating: $filename with $targets_file"
    echo "=========================================================="
    # run only for vagpose_isclassic_test.csv and vagdope_isclassic_test.csv
    python3 bop_toolkit/scripts/eval_bop19_pose.py \
      --results_path ./results \
      --eval_path ./eval \
      --result_filenames "$filename" \
      --targets_filename "$targets_file"

    python3 calc_per_object_ar.py "./eval/$name_no_ext"
done