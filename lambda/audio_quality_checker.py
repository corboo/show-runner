"""
Audio Quality Checker Lambda
Checks audio for silence gaps and fact-checks scripts.

Deploy to AWS Lambda and call from Make.com before Spreaker posting.

Returns:
{
    "passed": true/false,
    "audio_issues": ["list of issues"],
    "fact_check_issues": ["list of issues"],
    "should_post": true/false
}
"""

import json
import boto3
import os
import tempfile
import subprocess
from urllib.request import urlretrieve

def analyze_audio_for_gaps(audio_url, min_gap_seconds=5):
    """
    Download audio and use ffmpeg to detect silence gaps.
    Returns list of gaps >= min_gap_seconds.
    """
    issues = []
    
    try:
        # Download audio to temp file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_path = f.name
            urlretrieve(audio_url, temp_path)
        
        # Use ffmpeg silencedetect filter
        cmd = [
            'ffmpeg', '-i', temp_path,
            '-af', f'silencedetect=noise=-50dB:d={min_gap_seconds}',
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        stderr = result.stderr
        
        # Parse silence detection output
        import re
        silence_starts = re.findall(r'silence_start: ([\d.]+)', stderr)
        silence_ends = re.findall(r'silence_end: ([\d.]+)', stderr)
        
        for i, (start, end) in enumerate(zip(silence_starts, silence_ends)):
            duration = float(end) - float(start)
            if duration >= min_gap_seconds:
                issues.append(f"Silence gap of {duration:.1f}s at {float(start):.1f}s")
        
        # Cleanup
        os.unlink(temp_path)
        
    except Exception as e:
        issues.append(f"Audio analysis error: {str(e)}")
    
    return issues

def fact_check_script(script_text, perplexity_api_key):
    """
    Use Perplexity AI to fact-check the script.
    Returns list of factual issues found.
    """
    issues = []
    
    try:
        import requests
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {perplexity_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Fact-check this biography script. Look for:
1. Incorrect dates or years
2. Wrong facts about the person
3. Misattributed quotes or achievements
4. Historical inaccuracies

If you find errors, list each one clearly.
If everything is accurate, respond with just: VERIFIED

Script:
{script_text[:8000]}"""
                    }
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            if 'VERIFIED' not in content.upper():
                # Found issues
                issues.append(content)
        else:
            issues.append(f"Fact-check API error: {response.status_code}")
            
    except Exception as e:
        issues.append(f"Fact-check error: {str(e)}")
    
    return issues

def handler(event, context):
    """
    Lambda handler - receives audio URL and script text from Make.com
    
    Expected event:
    {
        "audio_url": "https://s3.amazonaws.com/...",
        "script_text": "Biography content...",
        "perplexity_api_key": "pplx-..." (optional, can use env var)
    }
    """
    
    audio_url = event.get('audio_url')
    script_text = event.get('script_text', '')
    perplexity_key = event.get('perplexity_api_key') or os.environ.get('PERPLEXITY_API_KEY')
    
    results = {
        "passed": True,
        "audio_issues": [],
        "fact_check_issues": [],
        "should_post": True,
        "message": ""
    }
    
    # Check audio for gaps
    if audio_url:
        audio_issues = analyze_audio_for_gaps(audio_url, min_gap_seconds=5)
        results["audio_issues"] = audio_issues
        if audio_issues:
            results["passed"] = False
            results["should_post"] = False
    
    # Fact-check script
    if script_text and perplexity_key:
        fact_issues = fact_check_script(script_text, perplexity_key)
        results["fact_check_issues"] = fact_issues
        if fact_issues and "VERIFIED" not in str(fact_issues).upper():
            results["passed"] = False
            # Still allow posting but flag for review
            results["message"] = "Fact-check flagged potential issues - review recommended"
    
    # Summary message
    if not results["passed"]:
        if results["audio_issues"]:
            results["message"] = f"BLOCKED: Audio has {len(results['audio_issues'])} silence gap(s) of 5+ seconds"
        elif results["fact_check_issues"]:
            results["message"] = "WARNING: Fact-check found potential issues"
    else:
        results["message"] = "All checks passed"
    
    return results

# For local testing
if __name__ == "__main__":
    test_event = {
        "audio_url": "https://example.com/test.mp3",
        "script_text": "Test biography content about someone born in 1985...",
    }
    print(json.dumps(handler(test_event, None), indent=2))
