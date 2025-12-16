from openai import OpenAI
import datasets
import json
import os

# OpenRouter with Grok 4.1 
client = OpenAI(
    api_key="YOUR_OPENROUTER_API_KEY_HERE",  
    base_url="https://openrouter.ai/api/v1"
)

# Load problems
dataset = datasets.load_dataset("meituan-longcat/AMO-Bench")
all_problems = list(dataset['test'])

# Only parser-based problems (number, set, variable)
problems = [p for p in all_problems if p['answer_type'] in ['number', 'set', 'variable']]


print(f"Testing Grok 4.1 on {len(problems)} parser-based problems\n")

# 2 prompts 
prompts = {
    'zero_shot': "{problem}\n\nProvide your final answer in the format:\n### The final answer is: $\\boxed{{answer}}$",
    
    'chain_of_thought': "Solve this step by step.\n\n{problem}\n\nProvide your final answer in the format:\n### The final answer is: $\\boxed{{answer}}$",
}

# 2 reasoning modes
reasoning_modes = {
    'no_reasoning': False,
    'with_reasoning': True
}

# File for incremental saving
RESULTS_FILE = 'grok_4_1_results.json'
CHECKPOINT_FILE = 'grok_4_1_checkpoint.json'

# Load existing results if any
if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, 'r') as f:
        results = json.load(f)
    print(f"Loaded {len(results)} existing results")
else:
    results = []

# Load checkpoint 
completed_tasks = set()
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, 'r') as f:
        checkpoint = json.load(f)
        completed_tasks = set(tuple(x) for x in checkpoint['completed'])
    print(f"Resuming from checkpoint: {len(completed_tasks)} tasks already done")

# Create list of all tasks (problem × prompt × reasoning_mode)
all_tasks = []
for prob in problems:
    for prompt_name in prompts.keys():
        for reasoning_name in reasoning_modes.keys():
            all_tasks.append((prob['question_id'], prompt_name, reasoning_name))

total_tasks = len(all_tasks)
remaining_tasks = [t for t in all_tasks if t not in completed_tasks]

print(f"Progress: {len(completed_tasks)}/{total_tasks} completed")
print(f"Remaining: {len(remaining_tasks)} tasks")

# Process only remaining tasks
for task_idx, (question_id, prompt_name, reasoning_name) in enumerate(remaining_tasks, 1):
    # Find the problem
    prob = next(p for p in problems if p['question_id'] == question_id)
    prompt_template = prompts[prompt_name]
    reasoning_enabled = reasoning_modes[reasoning_name]
    
    prompt = prompt_template.format(problem=prob['prompt'])
    
    try:
        # API call with reasoning control
        response = client.chat.completions.create(
            model="x-ai/grok-4.1-fast",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=42000,  
            extra_body={"reasoning": {"enabled": reasoning_enabled}}
        )
        
        # Extract response content
        response_content = response.choices[0].message.content
        
        # Check if reasoning was actually used
        reasoning_used = False
        if hasattr(response.choices[0].message, 'reasoning_details'):
            reasoning_used = True
            reasoning_details = response.choices[0].message.reasoning_details
        
        result = {
            'question_id': prob['question_id'],
            'prompt_type': prompt_name,
            'reasoning_mode': reasoning_name,
            'reasoning_enabled': reasoning_enabled,
            'reasoning_used': reasoning_used,
            'response': response_content,
            'gold_answer': prob['answer'],
            'answer_type': prob['answer_type'],
        }
        
        results.append(result)
        completed_tasks.add((question_id, prompt_name, reasoning_name))
        
        # Save incrementally after each result
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Update checkpoint
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'completed': list(completed_tasks),
            }, f, indent=2)
        
        reasoning_status = "WITH reasoning" if reasoning_enabled else "NO reasoning"
        print(f"[{task_idx}/{len(remaining_tasks)}] Q{question_id}, {prompt_name}, {reasoning_status}")
        
    except Exception as e:
        print(f"Error on Q{question_id}, {prompt_name}, {reasoning_name}: {e}")
        # Save error but continue
        results.append({
            'question_id': prob['question_id'],
            'prompt_type': prompt_name,
            'reasoning_mode': reasoning_name,
            'reasoning_enabled': reasoning_enabled,
            'response': f"ERROR: {str(e)}",
            'gold_answer': prob['answer'],
            'answer_type': prob['answer_type'],
            'error': True,
        })
        
        # Still save and checkpoint
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'completed': list(completed_tasks),
            }, f, indent=2)
