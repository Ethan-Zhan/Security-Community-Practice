<?php
/**
 * Security helper library for XSS Challenge Platform
 *
 * Provides centralized security functions for all levels.
 * Each level should require this file before outputting any HTML.
 *
 * @author   李秉卓 (2023211533)
 * @version  1.0.0
 * @package  XSS-Lab
 */

define('MAX_INPUT_LENGTH', 5000);
define('SESSION_TIMEOUT', 3600);

/**
 * Set security-related HTTP response headers
 *
 * Sets CSP, X-Frame-Options, X-Content-Type-Options, and X-XSS-Protection
 * headers on every page load to mitigate common web attacks.
 *
 * @return void
 */
function set_security_headers()
{
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: DENY');
    header('X-XSS-Protection: 1; mode=block');
    header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'");
}

/**
 * Safely encode output for HTML context
 *
 * Wraps htmlspecialchars() with ENT_QUOTES to prevent both double-quote
 * and single-quote attribute injection. Recursively handles arrays.
 *
 * @param  mixed $data  String or array to encode
 * @return mixed        Encoded string or array
 */
function safe_output($data)
{
    if (is_array($data)) {
        return array_map('safe_output', $data);
    }
    return htmlspecialchars((string) $data, ENT_QUOTES, 'UTF-8');
}

/**
 * Log detected XSS payload attempts to file
 *
 * Records timestamp, level number, source IP, and payload summary
 * for analysis and monitoring purposes.
 *
 * @param  int    $level    Level number where XSS was detected
 * @param  string $payload  The potentially malicious input string
 * @return void
 */
function log_xss_attempt($level, $payload)
{
    $log_dir = __DIR__ . '/../logs';
    if (!is_dir($log_dir)) {
        @mkdir($log_dir, 0755, true);
    }

    $log_file = $log_dir . '/xss_attempts.log';
    $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : 'unknown';
    $line = sprintf(
        "[%s] Level %d | IP: %s | Payload: %s\n",
        date('Y-m-d H:i:s'),
        (int) $level,
        $ip,
        substr((string) $payload, 0, 200)
    );

    @file_put_contents($log_file, $line, FILE_APPEND | LOCK_EX);
}

/**
 * Detect common XSS patterns in user input
 *
 * Checks input against a set of known XSS attack patterns.
 * Note: This is a heuristic, not a replacement for proper output encoding.
 *
 * @param  string $input  User-supplied input to check
 * @return bool           True if XSS pattern detected
 */
function detect_xss_payload($input)
{
    $patterns = array(
        '/<script[^>]*>/i',
        '/<img[^>]+onerror\s*=/i',
        '/<svg[^>]+onload\s*=/i',
        '/javascript\s*:/i',
        '/on\w+\s*=/i',
        '/<iframe[^>]*>/i',
        '/data\s*:\s*text\/html/i',
        '/expression\s*\(/i',
        '/vbscript\s*:/i',
    );

    foreach ($patterns as $pattern) {
        if (preg_match($pattern, $input)) {
            return true;
        }
    }
    return false;
}

/**
 * Validate input against expected type/format
 *
 * @param  string $input  Input to validate
 * @param  string $type   Expected type: alphanumeric, email, url, numeric
 * @return bool           True if valid
 */
function validate_input_type($input, $type)
{
    switch ($type) {
        case 'alphanumeric':
            return (bool) preg_match('/^[a-zA-Z0-9_\- ]+$/', $input);
        case 'numeric':
            return is_numeric($input);
        case 'email':
            return (bool) filter_var($input, FILTER_VALIDATE_EMAIL);
        case 'url':
            return (bool) preg_match('#^https?://#i', $input);
        default:
            return true;
    }
}

/**
 * Validate input length does not exceed maximum
 *
 * @param  string $input  Input to check
 * @return bool           True if length is within limit
 */
function validate_input_length($input)
{
    return strlen((string) $input) <= MAX_INPUT_LENGTH;
}
