import json
from utils import pred_extractor, append_try_list
import datasets
import copy
import re

# Load dataset
dataset = datasets.load_dataset("meituan-longcat/AMO-Bench")['test']
info_map = {item['question_id']: append_try_list(item) for item in dataset}
print(f"Loaded {len(info_map)} problems from AMO-Bench\n")

# Load results
RESULTS_FILE = 'grok_4_1_results.json'
print(f"Loading results from: {RESULTS_FILE}")

with open(RESULTS_FILE, 'r') as f:
    results = json.load(f)

print(f"Loaded {len(results)} test results\n")


def clean_gold_answer(gold):
    """Remove \boxed{} wrapper from gold answer"""
    if "\\boxed{" in gold:
        gold = gold.replace("\\boxed{", "").replace("}", "").strip()
    return gold.strip()


def simple_compare(pred, gold, answer_type):
    """Simple, reliable comparison"""
    
    # Clean gold answer
    gold_clean = clean_gold_answer(gold)
    pred_clean = pred.strip()
    
    # For numbers: numeric comparison
    if answer_type == "number":
        try:
            pred_num = float(pred_clean)
            gold_num = float(gold_clean)
            return abs(pred_num - gold_num) < 1e-6
        except:
            # Fallback to string
            return pred_clean == gold_clean
    
    # For sets: order-independent comparison
    elif answer_type == "set":
        pred_set = re.sub(r'\s+', '', pred_clean).replace('{', '').replace('}', '').replace('\\', '')
        gold_set = re.sub(r'\s+', '', gold_clean).replace('{', '').replace('}', '').replace('\\', '')
        return pred_set == gold_set
    
    # For everything else: string match
    return pred_clean == gold_clean


# Grade each result
print("GRADING RESULTS")

for idx, r in enumerate(results, 1):
    # Skip errors
    if r.get('error', False):
        r['correct'] = 0.0
        r['grading_status'] = 'skipped_api_error'
        print(f"\n[{idx}/{len(results)}] Q{r['question_id']} - SKIPPED (error in generation)")
        continue
    
    info = copy.deepcopy(info_map[r['question_id']])
    answer_type = info['answer_type']
    
    try:
        # Extract predicted answer
        pred_extract = pred_extractor(r['response'], answer_type)
        
        print(f"\n[{idx}/{len(results)}] Q{r['question_id']} ({r['prompt_type']}, {r['reasoning_mode']}, {answer_type})")
        print(f"  Pred: '{pred_extract[:50]}...'" if len(pred_extract) > 50 else f"  Pred: '{pred_extract}'")
        print(f"  Gold: '{info['answer'][:50]}...'" if len(info['answer']) > 50 else f"  Gold: '{info['answer']}'")
        
        # Use simple comparison 
        result = simple_compare(pred_extract, info['answer'], answer_type)
        
        r['correct'] = 1.0 if result else 0.0
        r['grading_status'] = 'success'
        r['extracted_answer'] = pred_extract
        
        print(f"  {'CORRECT' if r['correct'] else 'INCORRECT'}")
    
    except Exception as e:
        print(f"\n[{idx}/{len(results)}] Q{r['question_id']} - ERROR: {e}")
        r['correct'] = 0.0
        r['grading_status'] = f'grading_error: {str(e)}'
        r['extracted_answer'] = None

# Save graded results
GRADED_FILE = 'graded_grok_4.1.json'
with open(GRADED_FILE, 'w') as f:
    json.dump(results, f, indent=2)