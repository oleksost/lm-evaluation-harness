import evaluate as hf_evaluate
import re


try:
    pass_at_k = hf_evaluate.load("code_eval")

    # run simple test to check code execution is enabled before model generation
    test_cases = ["assert add(2, 3)==5"]
    candidates = [["def add(a,b): return a*b"]]
    results = pass_at_k.compute(references=test_cases, predictions=candidates, k=[1])
except Exception as e:
    raise e


def extract_code(text):
    """
    Extract code from various formats, including nested code blocks within special tags.
    
    Args:
        text (str): The input text containing code in one of several formats
        
    Returns:
        str: The extracted code or the original text if no pattern matches
    """
    code_blocks = []
    
    python_matches = re.finditer(r'```python(.*?)(?:```|$)', text, re.DOTALL)
    for match in python_matches:
        code_blocks.append(match.group(1).strip())
    
    if not code_blocks:
        code_matches = re.finditer(r'```(?!python)(.*?)(?:```|$)', text, re.DOTALL)
        for match in code_matches:
            code_blocks.append(match.group(1).strip())
    
    if code_blocks:
        return "\n\n".join(code_blocks)
    
    
    # Check for [BEGIN FINAL RESPONSE]...[END FINAL RESPONSE]
    begin_end_match = re.search(r'\[BEGIN FINAL RESPONSE\](.*?)(?:\[END FINAL RESPONSE\]|$)', text, re.DOTALL)
    if begin_end_match:
        content = begin_end_match.group(1).strip()
        nested_python = re.finditer(r'```python(.*?)(?:```|$)', content, re.DOTALL)
        nested_code_blocks = [match.group(1).strip() for match in nested_python]
        
        if not nested_code_blocks:
            nested_code = re.finditer(r'```(?!python)(.*?)(?:```|$)', content, re.DOTALL)
            nested_code_blocks = [match.group(1).strip() for match in nested_code]
        
        if nested_code_blocks:
            return "\n\n".join(nested_code_blocks)
        return content
    
    # Check for <|begin_of_solution|>...<|end_of_solution|>
    solution_match = re.search(r'<\|begin_of_solution\|>(.*?)(?:<\|end_of_solution\|>|$)', text, re.DOTALL)
    if solution_match:
        content = solution_match.group(1).strip()
        # Look for code blocks within this content
        nested_python = re.finditer(r'```python(.*?)(?:```|$)', content, re.DOTALL)
        nested_code_blocks = [match.group(1).strip() for match in nested_python]
        
        if not nested_code_blocks:
            nested_code = re.finditer(r'```(?!python)(.*?)(?:```|$)', content, re.DOTALL)
            nested_code_blocks = [match.group(1).strip() for match in nested_code]
        
        if nested_code_blocks:
            return "\n\n".join(nested_code_blocks)
        return content
    
    # Check for content after </think> tags
    think_match = re.search(r'</think>(.*?)$', text, re.DOTALL)
    if think_match:
        content = think_match.group(1).strip()
        nested_python = re.finditer(r'```python(.*?)(?:```|$)', content, re.DOTALL)
        nested_code_blocks = [match.group(1).strip() for match in nested_python]
        
        if not nested_code_blocks:
            nested_code = re.finditer(r'```(?!python)(.*?)(?:```|$)', content, re.DOTALL)
            nested_code_blocks = [match.group(1).strip() for match in nested_code]
        
        if nested_code_blocks:
            return "\n\n".join(nested_code_blocks)
        return content
    
    # Check for content after </reasoning> tags (new addition)
    reasoning_match = re.search(r'</reasoning>(.*?)$', text, re.DOTALL)
    if reasoning_match:
        content = reasoning_match.group(1).strip()
        # Look for code blocks within this content
        nested_python = re.finditer(r'```python(.*?)(?:```|$)', content, re.DOTALL)
        nested_code_blocks = [match.group(1).strip() for match in nested_python]
        
        if not nested_code_blocks:
            nested_code = re.finditer(r'```(?!python)(.*?)(?:```|$)', content, re.DOTALL)
            nested_code_blocks = [match.group(1).strip() for match in nested_code]
        
        if nested_code_blocks:
            return "\n\n".join(nested_code_blocks)
        return content
    
    # No pattern matched, return original text
    return text
import re



def process_reka(text):
    if " <sep> human:" in text:
        text = text.replace(" <sep> human:", "").strip()
        return text
    return text

def pass_at_1(references, predictions):
    # predictions = [extract_code(pred) for pred in predictions]
    # print("Predictions, ", predictions)
    predictions = [extract_code(pred) for pred in predictions]
    predictions = [process_reka(pred) for pred in predictions]
    return pass_at_k.compute(
        references=references,
        predictions=[predictions],
        k=[1],
    )[0]["pass@1"]


def list_fewshot_samples():
    return [
        {
            "task_id": 2,
            "text": "Write a function to find the similar elements from the given two tuple lists.",
            "code": "def similar_elements(test_tup1, test_tup2):\r\n  res = tuple(set(test_tup1) & set(test_tup2))\r\n  return (res) ",
            "test_list": [
                "assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)",
                "assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4)",
                "assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14)",
            ],
            "is_fewshot": True,
        },
        {
            "task_id": 3,
            "text": "Write a python function to identify non-prime numbers.",
            "code": "import math\r\ndef is_not_prime(n):\r\n    result = False\r\n    for i in range(2,int(math.sqrt(n)) + 1):\r\n        if n % i == 0:\r\n            result = True\r\n    return result",
            "test_list": [
                "assert is_not_prime(2) == False",
                "assert is_not_prime(10) == True",
                "assert is_not_prime(35) == True",
            ],
            "is_fewshot": True,
        },
        {
            "task_id": 4,
            "text": "Write a function to find the largest integers from a given list of numbers using heap queue algorithm.",
            "code": "import heapq as hq\r\ndef heap_queue_largest(nums,n):\r\n  largest_nums = hq.nlargest(n, nums)\r\n  return largest_nums",
            "test_list": [
                "assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] ",
                "assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] ",
                "assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35]",
            ],
            "is_fewshot": True,
        },
    ]
