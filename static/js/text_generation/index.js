$generate_button = $('#generateBtn');
$input = $('#codeInput');
$output = $('#codeOutput');
$markdown_output = $('#markdownOutput');

// 提交问题
$generate_button.on('click', function() {
    let question = $input.val();
    $.ajax({
        url: "/text_generation/generate_text",
        type: "GET",
        data: {
            question: question,
        },
        success: function(resp) {
            if (resp.result === 'success') {
                $output.text(resp.answer);
                $markdown_output.html(marked.parse(resp.answer));
            }
        }
    })
});

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
tabs.on('click', function () {
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
                $testOutput.text(resp.output);
            } else {
                $testOutput.text('测试失败');
            }
        }
    });
});

$languageInput = $('#languageInput');
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
            $input.text(data);
        },
        error: function(err) {
            console.error('无法加载文件:', err);  // 错误处理
        }
    });
});

$.ajax({
    url: "/static/question/python.text",
    method: 'GET',
    dataType: 'text',
    success: function(data) {
        $input.text(data);
    },
    error: function(err) {
        console.error('无法加载文件:', err);  // 错误处理
    }
});