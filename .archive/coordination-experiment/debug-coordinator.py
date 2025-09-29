#!/usr/bin/env python3
"""Debug script for the agent coordinator"""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from agent_coordinator import AgentCoordinator

def main():
    repo_root = Path.cwd()
    coordinator = AgentCoordinator(repo_root)
    
    print("=== Parsing tasks ===")
    tasks = coordinator.parse_tasks()
    
    for task in tasks:
        status = "✓" if task.completed else "○"
        deps_status = f" (deps: {len(task.dependencies)})" if task.dependencies else ""
        print(f"{status} {task.id} @{task.agent}: {task.description[:50]}...{deps_status}")
    
    print("\n=== Ready tasks ===")
    ready_tasks = coordinator.get_ready_tasks(tasks)
    
    if not ready_tasks:
        print("No tasks ready for execution")
        
        # Debug dependency issues
        pending_tasks = [t for t in tasks if not t.completed]
        print(f"\nDebugging {len(pending_tasks)} pending tasks:")
        
        completed_task_ids = {t.id for t in tasks if t.completed}
        print(f"Completed task IDs: {completed_task_ids}")
        
        for task in pending_tasks[:5]:  # Show first 5
            missing_deps = [dep for dep in task.dependencies if dep not in completed_task_ids]
            print(f"  {task.id}: needs {missing_deps}")
    else:
        for task in ready_tasks:
            print(f"  {task.id} @{task.agent}: {task.description[:50]}...")

if __name__ == "__main__":
    main()