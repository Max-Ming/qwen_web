from django.shortcuts import render
from django.http import JsonResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import subprocess

device = "cuda:0" # the device to load the model onto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tokenizer = AutoTokenizer.from_pretrained(os.path.join(BASE_DIR, 'static/Qwen2.5-Coder-7B-Instruct'))
model = AutoModelForCausalLM.from_pretrained(os.path.join(BASE_DIR, 'static/Qwen2.5-Coder-7B-Instruct')).to(device).eval()

# Create your views here.
def index(request):
    username = 'huangjinpeng'
    params = { 'username': username}
    return render(request, 'text_generation/index.html', params)

def generate_text(request):
    data = request.GET
    question = data.get('question')
   
    prompt = question
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=2048 # can increase the output length
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    answer = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(answer)

    return JsonResponse({'result': 'success', 'answer': answer})

def runtest(request):
    data = request.GET
    language = data.get('language')
    code = data.get('code')
    input = data.get('input')
    output = '运行失败'
    if language == 'python':
        try:
            result = subprocess.run(
                ['python3', '-c', code], 
                input=input,
                capture_output=True, 
                text=True, 
                timeout=10
            )
            output = result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            output = '运行超时'
        except Exception as e:
            output = str(e)
    elif language == 'cpp':
        try:
            with open('test.cpp', 'w') as f:
                f.write(code)

            compile_result = subprocess.run(['g++', 'test.cpp', '-o', 'test'], capture_output=True, text=True)
            
            if compile_result.returncode == 0:
                result = subprocess.run(
                    ['./test'], 
                    input=input, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                output = result.stdout if result.returncode == 0 else result.stderr
            else:
                output = compile_result.stderr
        except subprocess.TimeoutExpired:
            output = '运行超时'
        except Exception as e:
            output = str(e)
        finally:
            # 清理生成的文件
            if os.path.exists('test.cpp'):
                os.remove('test.cpp')
            if os.path.exists('test'):
                os.remove('test')
    elif language == 'java':
        try:
            with open('Main.java', 'w') as f:
                f.write(code)

            compile_result = subprocess.run(['javac', 'Main.java'], capture_output=True, text=True)

            if compile_result.returncode == 0:
                result = subprocess.run(
                    ['java', 'Main'],
                    input=input, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                output = result.stdout if result.returncode == 0 else result.stderr
            else:
                output = compile_result.stderr
        except subprocess.TimeoutExpired:
            output = '运行超时'
        except Exception as e:
            output = str(e)
        finally:
            # 清理生成的文件
            if os.path.exists('Main.java'):
                os.remove('Main.java')
            if os.path.exists('Main.class'):
                os.remove('Main.class')
    return JsonResponse({'result': 'success', 'output': output})