import asyncio
from supabase import create_client
from app.core.config import get_settings
from app.db.supabase_repo import SupabaseRepository

settings = get_settings()
client = create_client(settings.supabase_url, settings.supabase_service_role_key)
repo = SupabaseRepository(client, settings)

gardens = repo.list_gardens("demo-user")
print(f"Gardens: {len(gardens)}")

for g in gardens:
    plants = repo.list_garden_plants("demo-user", g.id)
    print(f"Garden {g.id} has {len(plants)} plants")
    for p in plants:
        plan = repo.get_plan("demo-user", p.id)
        if plan:
            print(f"Plan for {p.id} has {len(plan.tasks)} tasks")
            for t in plan.tasks:
                print(f"  Task {t.id} completed: {t.completed}")
            
            if plan.tasks:
                task_id = plan.tasks[0].id
                res = repo.complete_task("demo-user", p.id, task_id)
                print(f"Completed task {task_id}: {res}")
        else:
            print(f"No plan for {p.id}")
