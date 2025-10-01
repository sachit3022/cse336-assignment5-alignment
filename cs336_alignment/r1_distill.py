from openai import OpenAI
import os
import json
from tqdm import tqdm
from drgrpo_grader import r1_zero_reward_fn

if __name__ == "__main__":

    client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY") 
    with open("cs336_alignment/prompts/r1_zero.prompt", "r") as f:
        prompt_template = f.read()
    
    
    
    if os.path.exists("outputs/r1_distill_accuracy_results.jsonl"):
        os.remove("outputs/r1_distill_accuracy_results.jsonl")
    
    os.makedirs("outputs/", exist_ok=True)

    accuracy_list = []
    for topic in os.listdir("data/MATH/train/"):
        pbar = tqdm(total=len(os.listdir(f"data/MATH/train/{topic}/")), desc=f"Processing {topic}")
        for prob in os.listdir(f"data/MATH/train/{topic}/"):
            with open(f"data/MATH/train/{topic}/{prob}", "r") as f:
                problem_dict = json.load(f)
                prompt =  prompt_template.format(question=problem_dict['problem'])
                true_response = problem_dict['solution']
                resp = client.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
                    prompt=prompt,
                    max_tokens=4096,
                    stop=["</answer>"],
                )
    
                if resp.choices[0].finish_reason == "stop":
                    generated_response = prompt + resp.choices[0].text + "</answer>"
                reward_resp = r1_zero_reward_fn(generated_response,true_response,False)
                accuracy_list.append(
                    {
                        **reward_resp,
                        **problem_dict,
                        "prob": prob,
                        "topic": topic,
                        "true_output": true_response,
                        "generated_response": generated_response,
                        "reponse": resp.choices[0].model_dump()   
                    }
                )
                pbar.set_postfix({"accuracy": sum([x['answer_reward'] for x in accuracy_list])/len(accuracy_list)})
                with open("outputs/r1_distill_accuracy_results.jsonl", "a") as f:
                    f.write(json.dumps(accuracy_list[-1]) + "\n")
                pbar.update(1)