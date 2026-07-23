from typing import Any
import os
import json
import yaml
from pathlib import Path
from fastapi import APIRouter
from app.core.command_executor import execute_command
from app.services.cockpit_reader import _cockpit_dir

router = APIRouter(prefix="/projects", tags=["projects"])

def get_projects_dir() -> Path:
    return _cockpit_dir() / "workspace" / "projects"

@router.get("")
async def list_projects() -> dict[str, Any]:
    projects_dir = get_projects_dir()
    if not projects_dir.exists():
        return {"projects": []}
    
    projects = []
    for file_path in projects_dir.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        meta = yaml.safe_load(parts[1])
                        meta["id"] = file_path.stem
                        projects.append(meta)
        except Exception:
            pass
    return {"projects": projects}

@router.get("/{slug}")
async def get_project(slug: str) -> dict[str, Any]:
    file_path = get_projects_dir() / f"{slug}.md"
    if not file_path.exists():
        return {"error": "Project not found"}
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    meta = yaml.safe_load(parts[1])
                    meta["id"] = slug
                    meta["content"] = parts[2].strip()
                    return meta
    except Exception:
        pass
    return {"error": "Failed to parse project"}

@router.put("/{slug}")
async def update_project(slug: str, data: dict[str, Any]) -> dict[str, Any]:
    file_path = get_projects_dir() / f"{slug}.md"
    if not file_path.exists():
        return {"error": "Project not found"}
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                meta = yaml.safe_load(parts[1])
                
                if "tags" in data: meta["tags"] = data["tags"]
                if "repositories" in data: meta["repositories"] = data["repositories"]
                if "links" in data: meta["links"] = data["links"]
                if "tasks" in data: meta["tasks"] = data["tasks"]
                
                # Convert datetime objects to RFC3339 strings so Go can parse them
                import datetime
                for k, v in meta.items():
                    if isinstance(v, datetime.datetime):
                        meta[k] = v.isoformat()
                        
                new_yaml = yaml.dump(meta, allow_unicode=True, sort_keys=False)
                new_content = f"---\n{new_yaml}---\n{parts[2]}"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return {"success": True}
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Failed to update project"}

@router.post("")
async def create_project(data: dict[str, Any]) -> dict[str, Any]:
    slug = data.get("slug")
    title = data.get("title", "")
    desc = data.get("description", "")
    args = ["create", slug]
    if title:
        args.extend(["--title", title])
    if desc:
        args.extend(["--description", desc])
    
    result = execute_command("project", args)
    return {"output": result.stdout, "success": result.success}

@router.post("/{slug}/task")
async def add_task(slug: str, data: dict[str, Any]) -> dict[str, Any]:
    title = data.get("title")
    result = execute_command("project", ["task", "add", slug, title])
    return {"output": result.stdout, "success": result.success}

@router.put("/{slug}/task/{task_id}/move")
async def move_task(slug: str, task_id: str, data: dict[str, Any]) -> dict[str, Any]:
    col = data.get("column")
    result = execute_command("project", ["task", "move", slug, task_id, col])
    return {"output": result.stdout, "success": result.success}

@router.put("/{slug}/task/{task_id}/reorder")
async def reorder_task(slug: str, task_id: str, data: dict[str, Any]) -> dict[str, Any]:
    index = data.get("index")
    result = execute_command("project", ["task", "reorder", slug, task_id, str(index)])
    return {"output": result.stdout, "success": result.success}

@router.post("/{slug}/track")
async def add_tracking(slug: str, data: dict[str, Any]) -> dict[str, Any]:
    msg = data.get("message")
    result = execute_command("project", ["track", slug, msg])
    return {"output": result.stdout, "success": result.success}

@router.post("/{slug}/task/{task_id}/sync")
async def sync_github_issue(slug: str, task_id: str) -> dict[str, Any]:
    result = execute_command("project", ["task", "sync", slug, task_id])
    
    if not result.success:
        return {"error": result.stdout or "GitHub Sync failed"}
        
    # Read the updated project to get the task
    file_path = get_projects_dir() / f"{slug}.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        parts = content.split("---", 2)
        meta = yaml.safe_load(parts[1])
        tasks = meta.get("tasks", [])
        task = next((t for t in tasks if t.get("id") == task_id), None)
        
        return {"success": True, "task": task, "output": result.stdout}
    except Exception as e:
        return {"error": f"Failed to read synced task: {str(e)}"}

