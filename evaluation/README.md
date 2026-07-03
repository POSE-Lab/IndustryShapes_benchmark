# Evaluating Pose Estimation on IndustryShapes

This guide explains how to set up the BOP Toolkit to properly evaluate prediction CSV files on the **IndustryShapes** (Classic and Extended) datasets. It includes necessary modifications to calculate the legacy `ADD` metric and per-object Average Recalls (AR) following the BOP19 protocol.

## 1. Setup and Clone BOP Toolkit

First, clone the official BOP Toolkit and set up your environment:

```bash
# Initialize the BOP Toolkit submodule
git submodule update --init --recursive

# Apply the IndustryShapes compatibility patch
cd bop_toolkit
git apply ../diff.patch
cd ..

# Install requirements
pip install -r bop_toolkit/requirements.txt
```

## 2. Download and Setup Dataset 

The BOP Toolkit has a very strict parser and expects dataset names to be entirely alphanumeric (lowercase without dashes).

Run the provided script to automatically download the official test datasets and 3D models from HuggingFace, extract them into a local `data/bop_h3` directory, and correctly rename the folders (`isclassic` and `isextended`) to satisfy the toolkit's strict naming conventions:

```bash
./download_dataset.sh
```

## 3. Running the Evaluation

Ensure your prediction CSV files strictly follow the BOP naming convention: `[method]_[dataset]-[split].csv` (e.g., `fpmb_isclassic-test.csv`). The single underscore and hyphen are mandatory for the parser.

You can simply run the automated script that evaluates all CSV files in the `results` directory:

```bash
./run.sh
```

Alternatively, you can run the evaluation manually:

### Run BOP19 Evaluation (Overall Metrics)
Execute the main script from your project root. This will compute VSD, MSSD, MSPD, and ADD:

```bash
export PYTHONPATH=bop_toolkit
export BOP_PATH=/path/to/bop_datasets

python3 bop_toolkit/scripts/eval_bop19_pose.py \
  --results_path output/results \
  --eval_path output/eval \
  --result_filenames fpmb_IS_Classic-test.csv \
  --targets_filename test_targets_bop24.json
```
*Note: Depending on your exact dataset layout, your targets filename might be `test_targets_bop19.json` or `test_targets_bop24.json`.*

### Run Per-Object AR Calculation
Once the evaluation script finishes, it will generate a folder inside `output/eval/` matching your CSV name. Pass this directory to your per-object script:

```bash
python3 thirdparty/bop_toolkit/scripts/calc_per_obj_ar.py output/eval/fpmb_IS_Classic-test
```

This will print the exact tree of `AR_VSD`, `AR_MSSD`, `AR_MSPD`, and `AR_ADD` for each individual object, along with a LaTeX-formatted string ready to be dropped into your paper!

## 3. Evaluating a Single Object (Filtering Predictions and Targets)

If you need to evaluate the Average Recall (AR) for a single object in isolation (for example, Object 1) to verify isolated behavior, you can manually filter both the ground-truth targets and the predictions CSV. This is useful for reproducing the exact per-object evaluation metrics.

### 3.1 Filter the Ground Truth Targets
Use `jq` to extract only the targets for your target object and save it inside the dataset directory so the toolkit can find it.
```bash
jq '[.[] | select(.obj_id == 1)]' data/bop_h3/isclassic/test_targets_bop24.json > data/bop_h3/isclassic/test_targets_obj1.json
```

### 3.2 Filter the Predictions CSV
Use `awk` to keep the CSV header row and any predictions where the object ID is `1`. Ensure the filename matches the BOP convention exactly!
```bash
awk -F',' 'NR==1 || $3=="1"' results/fpmb_isclassic-test.csv > results/fpmbobj1_isclassic-test.csv
```

### 3.3 Run the BOP Toolkit Evaluation
Evaluate the filtered CSV against the filtered targets JSON, outputting to a clean directory.
```bash
python3 bop_toolkit/scripts/eval_bop19_pose.py \
  --results_path ./results \
  --eval_path ./eval_obj1 \
  --result_filenames fpmbobj1_isclassic-test.csv \
  --targets_filename test_targets_obj1.json
```

### 3.4 Show the Final Performance
Display the true Average Recall for the isolated object using the standard BOP performance script.
```bash
python3 bop_toolkit/scripts/show_performance_bop19.py \
  --eval_path ./eval_obj1 \
  --result_filenames fpmbobj1_isclassic-test.csv
```
*(You can replace `"1"` and `obj1` with any other object ID in the commands above to evaluate other objects.)*
