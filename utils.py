# utils.py - SIMPLE WORKING VERSION

import copy
import re

answer_prefix_list = [
    "### the final answer is:", "### the final answer:", "### final answer is:", "### final answer:",
    "### the final answer is", "### the final answer", "### final answer is", "### final answer",
]
answer_prefix_list_wo_hashtag = [p[4:] for p in answer_prefix_list]

think_postfix_list = [
    "</think>",
    "</longcat_think>",
]

remove_list = [
    "\\bigl", "\\bigr", 
    "\\Bigl", "\\Bigr",
    "\\biggl", "\\biggr",
    "\\Biggl", "\\Biggr",
    "\\bigg", "\\Bigg", "\\big", "\\Big",
    "\\left", "\\right",
]

replace_list = [
    ["'", "'"],
    ["'", "'"],
    [""", '"'],
    [""", '"'],
    ["（", "("],
    ["）", ")"],
    ["，", ", "],
    ["：", ": "],
    ["；", "; "],
    ["。", ". "],
    ["！", "! "],
    ["？", "? "],
    ["…", "..."],
    ["–", "-"],
    ["−", "-"],
]


def pred_extractor(pred, answer_type):
    """Extract predicted answer from model response"""
    pred_extract = pred.replace('：', ': ')

    # Remove thinking tags
    for think_postfix in think_postfix_list:
        pred_extract = pred_extract.split(think_postfix)[-1].strip()

    # Find answer prefix
    for prefix in answer_prefix_list + answer_prefix_list_wo_hashtag:
        if prefix in pred_extract.lower():
            pred_extract_lower = pred_extract.lower().split(prefix)[-1]
            pred_extract = pred_extract[-len(pred_extract_lower):]
            pred_extract = pred_extract.strip()
            break
    
    # Clean up LaTeX commands
    if answer_type != "description":
        for pat in remove_list:
            pred_extract = pred_extract.replace(pat, "")
    
    # Replace special characters
    for pat, new_pat in replace_list:
        pred_extract = pred_extract.replace(pat, new_pat)

    # Clean up spaces
    while " }" in pred_extract:
        pred_extract = pred_extract.replace(" }", "}")
    while ".}" in pred_extract:
        pred_extract = pred_extract.replace(".}", "}")
    
    # Type-specific cleaning
    if answer_type in ["number", "variable", "set"]:
        pred_extract = pred_extract.replace("\\,", "")
        pred_extract = pred_extract.replace("\\;", "")
        pred_extract = pred_extract.replace(r"\,", "")
        pred_extract = pred_extract.replace(r"\;", "")
        pred_extract = pred_extract.replace("\n", " ")
    
    if answer_type in ["number", "variable"]:
        pred_extract = pred_extract.replace(",", "")
        pred_extract = pred_extract.replace("\\{", "(").replace("\\}", ")")
        pred_extract = pred_extract.replace("\\[", "(").replace("\\]", ")")
        
    # Extract from \boxed{...}
    if "\\boxed{" in pred_extract:
        start = pred_extract.find("\\boxed{") + 7
        end = pred_extract.find("}", start)
        if end != -1:
            pred_extract = pred_extract[start:end]
        else:
            pred_extract = pred_extract.replace("\\boxed{", "")
    elif "$\\boxed{" in pred_extract:
        start = pred_extract.find("$\\boxed{") + 8
        end = pred_extract.find("}$", start)
        if end != -1:
            pred_extract = pred_extract[start:end]
        else:
            pred_extract = pred_extract.replace("$\\boxed{", "").replace("}$", "")

    return pred_extract.strip()


def append_try_list(ori_info):
    """Add test cases for variable answer verification"""
    info = copy.deepcopy(ori_info)
    assert "question_id" in info
    question_id = info["question_id"]
    
    if question_id == 5:
        assert info["answer_type"] == "variable"
        try_list = ["n=1", "n=2", "n=3", "n=4", "n=5", "n=6", "n=7", "n=8", "n=9", "n=10",
                    "n=11", "n=12", "n=13", "n=14", "n=15", "n=16", "n=17", "n=18", "n=19", "n=20"]
        info["try_list"] = try_list
    elif question_id == 37:
        assert info["answer_type"] == "variable"
        try_list = ["a=2,b=3,c=4", "a=3,b=4,c=5", "a=4,b=5,c=6", "a=5,b=6,c=7", "a=6,b=7,c=8",
                    "a=7,b=8,c=9", "a=8,b=9,c=10", "a=9,b=10,c=11", "a=10,b=11,c=12",
                    "a=11,b=12,c=13", "a=12,b=13,c=14", "a=13,b=14,c=15", "a=14,b=15,c=16",
                    "a=15,b=16,c=17", "a=16,b=17,c=18", "a=17,b=18,c=19", "a=18,b=19,c=20"]
        info["try_list"] = try_list
    
    return info