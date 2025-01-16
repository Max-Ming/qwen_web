$common_button = $('#commonBtn');
$rag_button = $('#ragBtn');
$generate_button = $('#generateBtn');
$complex_button = $('#complexBtn');
$code_input = $('#codeInput');
$rag_output = $('#ragOutput');
$question_input = $('#questionInput');
$output = $('#codeOutput');
$markdown_output = $('#markdownOutput');
$languageInput = $('#languageInput');

$common_button.on('click', function() {
    console.log(111)
    let code = $code_input.val();
    $question_input.val(`我的问题为：\n${code}\n请回答我的问题：`)
})

$rag_button.on('click', function() {
    let code = $code_input.val();
    let language = $languageInput.val();
    $.ajax({
        url: "/text_generation/rag",
        type: "GET",
        data: {
            code: code,
            language: language,
        },
        success: function(resp) {
            if (resp.result === 'success') {
                $rag_output.val(resp.answer);
                // $question_input.val(1);
                $question_input.val(`我的问题为：\n${code}\n下面是具体的例子\n${resp.answer}\n请参考上面的例子做出回答：`)
            }
        }
    })
})

// 提交问题
// $generate_button.on('click', function() {
//     let question = $input.val();
//     $.ajax({
//         url: "/text_generation/generate_text",
//         type: "GET",
//         data: {
//             question: question,
//         },
//         success: function(resp) {
//             if (resp.result === 'success') {
//                 $output.val(resp.answer);
//                 $markdown_output.html(marked.parse(resp.answer));
//             }
//         }
//     })
// });
$generate_button.on('click', function() {
    let question = $question_input.val();
    $.ajax({
        url: "/text_generation/generate_text",
        type: "GET",
        data: {
            question: question,
        },
        success: function(resp) {
            if (resp.result === 'success') {
                // 清空之前的输出
                $output.val('');
                $markdown_output.html('');

                // 调用打字机效果的函数
                typeWriter(resp.answer, 0);
            }
        }
    });
});

$complex_button.on('click', function() {
    let question = $question_input.val();
    // 替换最后一行
    if (question.trim() !== "") { // 确保问题不为空
        let lines = question.split('\n'); // 按换行符分割成数组
        lines[lines.length - 1] = "在写出代码之前，请详细写出分析步骤。"; // 替换最后一行
        question = lines.join('\n'); // 重新组合为字符串
    }
    console.log(question);
    $.ajax({
        url: "/text_generation/generate_text",
        type: "GET",
        data: {
            question: question,
        },
        success: function(resp) {
            if (resp.result === 'success') {
                // 清空之前的输出
                $output.val('');
                $markdown_output.html('');

                // 调用打字机效果的函数
                typeWriter(resp.answer, 0);
            }
        }
    });
})

function typeWriter(text, i) {
    if (i < text.length) {
        $output.val($output.val() + text.charAt(i));
        $markdown_output.html(marked.parse($output.val()));
        i++;
        setTimeout(function() {
            typeWriter(text, i);
        }, 10);
    }
}

// 渲染markdown
let $markdownBtn = $('#markdownBtn');
$markdownBtn.on('click', function() {
    let text = $output.val();
    $markdown_output.html(marked.parse(text));
    $markdown_output.addClass('markdown-body');
});

// 切换tab
let tabs = $('.tab');
let tabContents = $('.tab-content');
tabs.on('click', function() {
    tabs.removeClass('active');
    tabContents.removeClass('active');

    $(this).addClass('active');
    const target = $(this).data('target');
    $('#' + target).addClass('active');
});

// 提取代码
let $onlyCode = $('#onlyCode');
let $codeBtn = $('#codeBtn');
$codeBtn.on('click', function() {
    let text = $output.val();
    const codeRegex = /```([\s\S]*?)```/;

    const match = codeRegex.exec(text);

    if (match) {
        const extractedCode = `\`\`\`${match[1].trim()}\n\`\`\``;

        $onlyCode.html(marked.parse(extractedCode));
        $onlyCode.addClass('markdown-body');
    } else {
        $onlyCode.html(marked.parse('### 未找到代码块'));
        $onlyCode.addClass('markdown-body');
    }
});

// 运行代码
$runTestBtn = $('#runTestBtn');
$languageSelect = $('#languageSelect');
$testInput = $('#testInput');
$testOutput = $('#testOutput');
$runTestBtn.on('click', function() {
    let code = $onlyCode.text();
    $.ajax({
        url: "/text_generation/runtest",
        type: "GET",
        data: {
            language: $languageSelect.val(),
            code: code,
            input: $testInput.val(),
        },
        success: function(resp) {
            if (resp.result === 'success') {
                $testOutput.val(resp.output);
            } else {
                $testOutput.val('测试失败');
            }
        }
    });
});

$.ajax({
    url: "/static/question/python.text",
    method: 'GET',
    dataType: 'text',
    success: function(data) {
        $code_input.val(data);
    },
    error: function(err) {
        console.error('无法加载文件:', err); // 错误处理
    }
});


$languageInput.on('change', function() {
    let language = $languageInput.val();
    if (language === 'python') {
        url = "/static/question/python.text";
    } else if (language === 'cpp') {
        url = "/static/question/c++.text";
    } else if (language === 'java') {
        url = "/static/question/java.text";
    }
    $.ajax({
        url: url,
        method: 'GET',
        dataType: 'text',
        success: function(data) {
            $code_input.val(data);
        },
        error: function(err) {
            console.error('无法加载文件:', err); // 错误处理
        }
    });
});

$(document).ready(function() {
    // 登录表单提交
    $('#loginForm').on('submit', function(e) {
        e.preventDefault(); // 阻止默认的表单提交行为

        // 获取表单数据
        var email = $('#loginEmail').val();
        var password = $('#loginPassword').val();

        // 使用 AJAX 提交数据
        $.ajax({
            url: '/login/', // 后端登录处理 URL
            type: 'POST',
            data: {
                email: email,
                password: password,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() // 添加 CSRF Token
            },
            success: function(response) {
                // 登录成功后，显示提示并关闭模态框
                alert('登录成功！');
                $('#loginModal').modal('hide');
            },
            error: function(xhr, status, error) {
                // 登录失败时，显示错误消息
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.error : '登录失败！';
                alert(errorMessage);
            }
        });
    });

    // 注册表单提交
    $('#registerForm').on('submit', function(e) {
        e.preventDefault(); // 阻止默认的表单提交行为

        // 获取表单数据
        var email = $('#registerEmail').val();
        var password = $('#registerPassword').val();

        // 使用 AJAX 提交数据
        $.ajax({
            url: '/register/', // 后端注册处理 URL
            type: 'POST',
            data: {
                email: email,
                password: password,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() // 添加 CSRF Token
            },
            success: function(response) {
                // 注册成功后，显示提示并关闭模态框
                alert('注册成功！');
                $('#registerModal').modal('hide');
            },
            error: function(xhr, status, error) {
                // 注册失败时，显示错误消息
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.error : '注册失败！';
                alert(errorMessage);
            }
        });
    });
});