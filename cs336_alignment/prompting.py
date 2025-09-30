from vllm import LLM, SamplingParams
import os
import json
from drgrpo_grader import grade
from tqdm import tqdm

def save_accruracy_list(accuracy_list):
    with open("outputs/accuracy_results.json", "w") as f:
        json.dump(accuracy_list, f, indent=4)

if __name__ == "__main__":
    # Create a sampling params object, stopping generation on newline.
    sampling_params = SamplingParams(
        temperature=1.0, top_p=1.0, max_tokens=5000, stop= ["</answer>"], include_stop_str_in_output=True
    )
    # Create an Qwen 2.5 Math 1.5B Base
    llm = LLM(model="Qwen/Qwen2.5-Math-1.5B")
    accuracy_list = []
    #load the math dataset from ../data/MATH/test/{topic}/{i}.json
    with open("cs336_alignment/prompts/r1_zero.prompt", "r") as f:
        prompt_template = f.read()
    
    prompts = [ ]
    true_outputs = []
    
    for topic in os.listdir("data/MATH/test/"):
        pbar = tqdm(total=len(os.listdir(f"data/MATH/test/{topic}/")), desc=f"Processing {topic}")
        for prob in os.listdir(f"data/MATH/test/{topic}/"):
            with open(f"data/MATH/test/{topic}/{prob}", "r") as f:
                problem_dict = json.load(f)
                prompts.append( prompt_template.format(question=problem_dict['problem']))
                true_outputs.append(problem_dict['solution'])
            if len(prompts) >= 200:
                outputs = llm.generate(prompts, sampling_params)
                for i in range(len(outputs)):
                    model_output= outputs[i].prompt + outputs[i].outputs[0].text
                    true_output = true_outputs[i]
                    accuracy = grade(model_output,true_output)
                    accuracy_list.append((accuracy, topic, prob, model_output, true_output))
                
                save_accruracy_list(accuracy_list)
                prompts = []
                true_outputs = []
                pbar.set_postfix({"accuracy": sum([x[0] for x in accuracy_list])/len(accuracy_list)})
                pbar.update(200)
    
    # process remaining prompts
    if prompts:
        outputs = llm.generate(prompts, sampling_params)
        for i in range(len(outputs)):
            model_output= outputs[i].prompt + outputs[i].outputs[0].text
            true_output = true_outputs[i]
            accuracy = grade(model_output,true_output)
            accuracy_list.append((accuracy, topic, prob, model_output, true_output))
        save_accruracy_list(accuracy_list)

    
            