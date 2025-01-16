from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import subprocess
# from accelerate import infer_auto_device_map, init_empty_weights

# max_memory = {
#             0: "0GB",
#             1: "0GB",
#             2: "10GB",
#             3: "0GB",
#             4: "0GB",
#             5: "0GB",
#             6: "0GB",
#             7: "25GB",
#         }
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
checkpoint = os.path.join(BASE_DIR, 'static/Qwen2.5-Coder-7B-Instruct')
# with init_empty_weights():
#     empty_model = AutoModelForCausalLM.from_pretrained(checkpoint, trust_remote_code=True)
#     device_map = infer_auto_device_map(empty_model, max_memory=max_memory)

# 加载模型和分词器
# device = "cuda:0" # the device to load the model onto
device = 'cpu'

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device).eval()

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

# Create your views here.
def home(request):
    return redirect('index')

def textgen(request):
    if not request.user.is_authenticated:
        # 用户未登录，重定向到登录页面
        return redirect('login')  # Replace 'login' with your login URL name
    username = 'huangjinpeng'
    params = { 'username': username}
    return render(request, 'text_generation/textgen.html', params)

def rag(request):
    data = request.GET
    code = data.get('code')
    language = data.get('language')


    if language == 'python':
        rag_answer = """python实现的归并排序算法：
def merge_sort(data, l, r):
    if l >= r:
        return
    mid = (l + r) // 2
    merge_sort(data, l, mid)
    merge_sort(data, mid + 1, r)
    tmp = []
    i = l
    j = mid + 1
    while (i <= mid) and (j <= r):
        if data[i] <= data[j]:
            tmp.append(data[i])
            i += 1
        else:
            tmp.append(data[j])
            j += 1
    tmp += data[i:mid + 1]
    tmp += data[j:r + 1]
    data[l:r + 1] = tmp"""
    elif language == 'cpp':
        rag_answer = """c++实现的高精度乘法算法：
#include <iostream>
#include <vector>

using namespace std;

vector<int> mul(vector<int> &A, int b)
{
    vector<int> C;
    int t = 0;

    for (int i = 0; i < A.size() || t; i ++ )
    {
        if (i < A.size()) t += A[i] * b;
        C.push_back(t % 10);
        t /= 10;
    }

    while (C.size() > 1 && C.back() == 0) C.pop_back();

    return C;
}

int main()
{
    string a;
    int b;

    cin >> a >> b;

    vector<int> A;
    for (int i = a.size() - 1; i >= 0; i -- ) A.push_back(a[i] - '0');

    auto C = mul(A, b);

    for (int i = C.size() - 1; i >= 0; i -- ) cout << C[i];
    cout << endl;

    return 0;
}"""
    elif language == 'java':
        rag_answer = """java实现的一维数组前缀和算法：
import java.util.Scanner;
public class Main{
    public static void main(String[] args){
        Scanner scan  = new Scanner(System.in);
        int n = scan.nextInt();
        int m = scan.nextInt();
        int[] a = new int[n+1];
        int[] s = new int[n+1];
        for(int i = 1 ; i <= n ; i ++ ){
            a[i] = scan.nextInt();
        }
        for(int i = 1 ; i <= n ; i ++){
                s[i] = s[i-1] + a[i];
        }
        while(m-- > 0){
            int l = scan.nextInt();
            int r = scan.nextInt();
            System.out.println(s[r] - s[l-1]);
        }
    }
}"""

    return JsonResponse({'result': 'success', 'answer': rag_answer})

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
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=2048,  # 可以增加输出长度
        do_sample=True,  # 如果希望生成的内容更随机，可以使用这个选项
        return_dict_in_generate=True,  # 确保可以逐步生成
        output_scores=True  # 获取输出分数以便处理
    )
    # generated_ids = [
    #     output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    # ]
    # answer = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # return JsonResponse({'result': 'success', 'answer': answer})

    generated_text = ""
    for output_ids in generated_ids.sequences:
        generated_text += tokenizer.decode(output_ids[len(model_inputs.input_ids[0]):], skip_special_tokens=True)

    return JsonResponse({'result': 'success', 'answer': generated_text})

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

# 注册视图
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # 创建用户
            messages.success(request, '注册成功！')
            return redirect('login')  # 注册成功后跳转到登录页面
        else:
            messages.error(request, '请检查输入的字段')
    else:
        form = CustomUserCreationForm()
    return render(request, 'text_generation/register.html', {'form': form})

# 登录视图
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # 获取用户并登录
            user = form.get_user()
            login(request, user)
            messages.success(request, f'欢迎回来，{user.username}！')
            return redirect('index')  # 登录成功后跳转到主页
        else:
            messages.error(request, '用户名或密码错误')
    else:
        form = AuthenticationForm()
    return render(request, 'text_generation/login.html', {'form': form})

# 登出视图
def logout_view(request):
    # 登出用户
    logout(request)

    # 设置缓存头，防止浏览器缓存
    response = redirect('login')  # 重定向到登录页面
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response