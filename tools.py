import os
import subprocess
import webbrowser
import psutil # type: ignore
import json
from duckduckgo_search import DDGS
from PIL import ImageGrab

def run_powershell_command(command: str) -> str:
    """Executes a PowerShell or shell command on the local Windows system and returns the output."""
    try:
        process = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30
        )
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        if stderr:
            return f"Output:\n{stdout}\nErrors:\n{stderr}" if stdout else f"Error: {stderr}"
        return stdout if stdout else "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Execution error: {str(e)}"

def open_application(app_name: str) -> str:
    """Opens a desktop application or URL (e.g. 'chrome', 'notepad', 'calc', 'spotify', 'https://google.com')."""
    try:
        app_name_lower = app_name.lower().strip()
        if app_name_lower.startswith("http://") or app_name_lower.startswith("https://"):
            webbrowser.open(app_name)
            return f"Opened website: {app_name}"
        
        app_map = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "cmd": "cmd.exe",
            "terminal": "wt.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "spotify": "spotify.exe",
            "code": "code.cmd",
            "vscode": "code.cmd",
            "explorer": "explorer.exe",
            "paint": "mspaint.exe",
            "taskmanager": "taskmgr.exe"
        }
        
        target = app_map.get(app_name_lower, app_name)
        subprocess.Popen(target, shell=True)
        return f"Successfully launched {app_name}."
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

def web_search(query: str, max_results: int = 5) -> str:
    """Performs a real-time web search and returns relevant search results with titles, snippets, and URLs."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "No search results found."
            formatted = []
            for idx, r in enumerate(results, 1):
                formatted.append(f"{idx}. {r.get('title')}\n   Snippet: {r.get('body')}\n   URL: {r.get('href')}")
            return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search failed: {str(e)}"

def read_file(filepath: str) -> str:
    """Reads the contents of a local file."""
    try:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Creates or overwrites a local file with the specified text content."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File successfully written to '{filepath}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_directory(directory_path: str = ".") -> str:
    """Lists files and folders inside a given directory."""
    try:
        items = os.listdir(directory_path)
        if not items:
            return f"Directory '{directory_path}' is empty."
        result = []
        for item in items:
            full_path = os.path.join(directory_path, item)
            item_type = "Folder" if os.path.isdir(full_path) else "File"
            size = f"({os.path.getsize(full_path)} bytes)" if item_type == "File" else ""
            result.append(f"[{item_type}] {item} {size}")
        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def execute_python_code(code: str) -> str:
    """Executes arbitrary Python code in a safe subprocess and returns stdout/stderr."""
    try:
        process = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=20
        )
        out = process.stdout.strip()
        err = process.stderr.strip()
        if err:
            return f"Stdout:\n{out}\nStderr:\n{err}" if out else f"Error:\n{err}"
        return out if out else "Python script executed successfully with no output."
    except Exception as e:
        return f"Python execution error: {str(e)}"

def get_system_diagnostics() -> str:
    """Returns real-time system performance metrics including CPU, Memory, Disk, and Battery stats."""
    try:
        cpu_pct = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        battery = psutil.sensors_battery()
        
        info = [
            f"CPU Usage: {cpu_pct}% ({psutil.cpu_count(logical=True)} logical cores)",
            f"Memory: {mem.percent}% used ({round(mem.used/(1024**3), 2)} GB / {round(mem.total/(1024**3), 2)} GB)",
            f"Disk Usage: {disk.percent}% used ({round(disk.used/(1024**3), 2)} GB / {round(disk.total/(1024**3), 2)} GB)"
        ]
        if battery:
            plugged = "Plugged In" if battery.power_plugged else "On Battery"
            info.append(f"Battery: {battery.percent}% ({plugged})")
            
        return "\n".join(info)
    except Exception as e:
        return f"Failed to retrieve system diagnostics: {str(e)}"

def take_screenshot(save_path: str = "screenshot.png") -> str:
    """Captures the current screen and saves it as an image file."""
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(save_path)
        return f"Screenshot saved successfully to {os.path.abspath(save_path)}"
    except Exception as e:
        return f"Failed to capture screenshot: {str(e)}"

TOOL_FUNCTIONS = {
    "run_powershell_command": run_powershell_command,
    "open_application": open_application,
    "web_search": web_search,
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "execute_python_code": execute_python_code,
    "get_system_diagnostics": get_system_diagnostics,
    "take_screenshot": take_screenshot
}

TOOL_DECLARATIONS = [
    run_powershell_command,
    open_application,
    web_search,
    read_file,
    write_file,
    list_directory,
    execute_python_code,
    get_system_diagnostics,
    take_screenshot
]