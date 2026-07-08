from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", contact_info="jordan@example.com", preferences={"available_time_minutes": 60})

    mochi = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    rex = Pet(name="Rex", species="cat", breed="Tabby")
    owner.add_pet(mochi)
    owner.add_pet(rex)

    mochi.add_task(
        Task(title="Morning walk", category="walk", duration_minutes=30, priority="high", preferred_time=time(8, 0))
    )
    mochi.add_task(
        Task(title="Brushing", category="grooming", duration_minutes=15, priority="low", preferred_time=time(18, 0))
    )
    rex.add_task(
        Task(title="Feeding", category="feeding", duration_minutes=10, priority="high", preferred_time=time(9, 0))
    )
    # Same preferred time as Mochi's "Morning walk", on a different pet — should trigger a conflict warning.
    rex.add_task(
        Task(title="Litter box cleaning", category="other", duration_minutes=5, priority="medium", preferred_time=time(8, 0))
    )

    scheduler = Scheduler(available_time_minutes=60)

    conflicts = scheduler.detect_time_conflicts(owner)
    if conflicts:
        print("Scheduling Conflicts")
        for warning in conflicts:
            print(f"  {warning}")
        print()

    plan = scheduler.generate_daily_plan(owner)

    print("Today's Schedule")
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
