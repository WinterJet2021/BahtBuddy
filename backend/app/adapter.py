# app/services/os_adapter.py
import os, datetime

def save_report(content, name="report.txt"):
    instance_dir = os.path.join(os.getcwd(), "backend", "instance")
    os.makedirs(instance_dir, exist_ok=True)
    path = os.path.join(instance_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def get_system_time():
    return datetime.datetime.now().isoformat()
