import json
import glob
import os
import argparse
import numpy as np

def calculate_per_object_ar(eval_dir):
    """
    Calculates the per-object Average Recall (AR) following the BOP19 protocol.
    BOP19 AR is the mean of the AR of VSD, MSSD, and MSPD.
    """
    metrics = ['vsd', 'mssd', 'mspd', 'add']
    
    # First pass to find all unique object IDs in the dataset
    obj_ids = set()
    for metric in metrics:
        score_files = glob.glob(os.path.join(eval_dir, f"error={metric}*", "scores_*.json"))
        for f in score_files:
            with open(f, 'r') as fh:
                data = json.load(fh)
                if 'obj_recalls' in data:
                    obj_ids.update(data['obj_recalls'].keys())
                elif 'scores' in data:
                    obj_ids.update(data['scores'].keys())
    
    obj_ids = sorted(list(obj_ids), key=int)
    if not obj_ids:
        print(f"No score files found in {eval_dir}")
        return

    print(f"Found {len(obj_ids)} objects: {obj_ids}")
    results = {}

    # Step 1: Calculate the Metric AR for each error function
    for metric in metrics:
        score_files = glob.glob(os.path.join(eval_dir, f"error={metric}*", "scores_*.json"))
        if not score_files:
            continue
            
        # Dictionary to store all recalls across all thresholds for each object
        metric_obj_recalls = {obj_id: [] for obj_id in obj_ids}
        
        for f in score_files:
            with open(f, 'r') as fh:
                data = json.load(fh)
                score_dict = data.get('obj_recalls') or data.get('scores', {})
                for obj_id in obj_ids:
                    # Append the recall at this specific threshold
                    if obj_id in score_dict:
                        metric_obj_recalls[obj_id].append(score_dict[obj_id])
        
        # The Average Recall (AR) for this metric is the mean across all thresholds
        results[metric] = {
            obj_id: np.mean(metric_obj_recalls[obj_id]) if metric_obj_recalls[obj_id] else 0.0
            for obj_id in obj_ids
        }

    # Step 2: Calculate the final BOP24 AR (Mean of evaluated metrics)
    print("\n" + "="*50)
    print(f"Per-Object Average Recall for:\n{os.path.basename(eval_dir)}")
    print("="*50)
    
    ar_per_obj = {}
    for obj_id in obj_ids:
        ar_sum = 0
        count = 0
        for metric in metrics:
            if metric in results:
                val = results[metric][obj_id]
                ar_sum += val
                count += 1
                
        if count > 0:
            avg_ar = ar_sum / count
            ar_per_obj[obj_id] = avg_ar
            print(f"Object {obj_id}: {avg_ar:.4f}")
            if 'vsd' in results:
                print(f"  ├─ AR_VSD:  {results['vsd'][obj_id]:.4f}")
            if 'mssd' in results:
                print(f"  ├─ AR_MSSD: {results['mssd'][obj_id]:.4f}")
            if 'mspd' in results:
                print(f"  ├─ AR_MSPD: {results['mspd'][obj_id]:.4f}")
            if 'add' in results:
                print(f"  └─ AR_ADD:  {results['add'][obj_id]:.4f}")
            print("-" * 30)
            
    # For LaTeX formatting
    latex_row = " & ".join([f"{ar_per_obj[obj_id]:.2f}" for obj_id in obj_ids if obj_id in ar_per_obj])
    print("\nLaTeX row format:")
    print(latex_row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate per-object BOP19 Average Recall")
    parser.add_argument("eval_dir", type=str, help="Path to the specific evaluation directory (e.g., output/eval/industryshapes_IS_Extended-test)")
    args = parser.parse_args()
    
    calculate_per_object_ar(args.eval_dir)
