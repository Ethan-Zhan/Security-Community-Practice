<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()
{
confirm("完成的不错！");
 window.location.href="level2.php?keyword=test";
}
</script>
<title>欢迎来到level1 (安全加固版)</title>
</head>
<body>
<h1 align=center>欢迎来到level1 (安全加固版)</h1>
<?php
/**
 * Level 1 安全加固版
 * 修复内容：使用 htmlspecialchars() 对用户输入进行转义
 * 原漏洞：$_GET["name"] 直接拼接到 HTML，可被注入任意脚本
 */
require_once __DIR__ . '/../includes/security.php';
set_security_headers();
ini_set("display_errors", 0);
$str = isset($_GET["name"]) ? $_GET["name"] : '';

if (!validate_input_length($str)) {
    echo '<h2 align=center>输入过长，最大允许' . MAX_INPUT_LENGTH . '字符</h2>';
} else {
    echo '<h2 align=center>欢迎用户' . safe_output($str) . '</h2>';
}
?>
<center><img src=level1.png></center>
<?php
echo '<h3 align=center>payload的长度:' . strlen($str) . '</h3>';
?>
</body>
</html>
