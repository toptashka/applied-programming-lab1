from models import (
    Person, Manager, Coach, Athlete, Location, Event,
    TrainingSession, Tournament, TrainingGroup, Sport,
    Achievement, MedicalCertificate, Equipment
)
import services
import storage
import exceptions

# Глобальное хранилище состояния приложения
db = storage.create_empty_db()


# Вспомогательные функции выбора объектов из списков с поддержкой возврата [0]
def select_location(locations: list[Location]) -> Location | None:
    if not locations:
        print("No locations available")
        return None

    print("\nSelect location:")
    for idx, loc in enumerate(locations, start=1):
        print(f"[{idx}] {loc.name_location} (Capacity: {loc.capacity})")
    print("[0] Back")

    while True:
        raw = input("Enter choice: ").strip()
        if raw == "0" or raw == "":
            return None
        try:
            choice = int(raw)
            if 1 <= choice <= len(locations):
                return locations[choice - 1]
            print(f"Invalid index. Please enter a number between 1 and {len(locations)}, or 0 to go back.")
        except ValueError:
            print("Invalid input: please enter a valid number or 0 to go back.")


def select_group(groups: list[TrainingGroup]) -> TrainingGroup | None:
    if not groups:
        print("No groups available")
        return None

    print("\nSelect group:")
    for idx, grp in enumerate(groups, start=1):
        print(f"[{idx}] {grp.group_name} (Coach: {grp.coach.name})")
    print("[0] Back")

    while True:
        raw = input("Enter choice: ").strip()
        if raw == "0" or raw == "":
            return None
        try:
            choice = int(raw)
            if 1 <= choice <= len(groups):
                return groups[choice - 1]
            print(f"Invalid index. Please enter a number between 1 and {len(groups)}, or 0 to go back.")
        except ValueError:
            print("Invalid input: please enter a valid number or 0 to go back.")


def select_sport(sports: list[Sport]) -> Sport | None:
    if not sports:
        print("No sports available")
        return None

    print("\nSelect sport:")
    for idx, sp in enumerate(sports, start=1):
        print(f"[{idx}] {sp.name} ({sp.category})")
    print("[0] Back")

    while True:
        raw = input("Enter choice: ").strip()
        if raw == "0" or raw == "":
            return None
        try:
            choice = int(raw)
            if 1 <= choice <= len(sports):
                return sports[choice - 1]
            print(f"Invalid index. Please enter a number between 1 and {len(sports)}, or 0 to go back.")
        except ValueError:
            print("Invalid input: please enter a valid number or 0 to go back.")


def select_athlete(athletes: list[Athlete]) -> Athlete | None:
    if not athletes:
        print("No athletes available")
        return None

    print("\nSelect athlete:")
    for idx, ath in enumerate(athletes, start=1):
        print(f"[{idx}] {ath.name}")
    print("[0] Back")

    while True:
        raw = input("Enter choice: ").strip()
        if raw == "0" or raw == "":
            return None
        try:
            choice = int(raw)
            if 1 <= choice <= len(athletes):
                return athletes[choice - 1]
            print(f"Invalid index. Please enter a number between 1 and {len(athletes)}, or 0 to go back.")
        except ValueError:
            print("Invalid input: please enter a valid number or 0 to go back.")


def select_tournament(tournaments: list[Tournament]) -> Tournament | None:
    if not tournaments:
        print("No tournaments available")
        return None

    print("\nSelect tournament:")
    for idx, trn in enumerate(tournaments, start=1):
        print(f"[{idx}] {trn.title} ({trn.date_time})")
    print("[0] Back")

    while True:
        raw = input("Enter choice: ").strip()
        if raw == "0" or raw == "":
            return None
        try:
            choice = int(raw)
            if 1 <= choice <= len(tournaments):
                return tournaments[choice - 1]
            print(f"Invalid index. Please enter a number between 1 and {len(tournaments)}, or 0 to go back.")
        except ValueError:
            print("Invalid input: please enter a valid number or 0 to go back.")


def select_session(sessions: list[TrainingSession]) -> TrainingSession | None:
    if not sessions:
        print("No training sessions available")
        return None

    print("\nSelect session:")
    for idx, session in enumerate(sessions, start=1):
        print(f"[{idx}] {session.group.group_name} with {session.coach.name} at {session.date_time}")
    print("[0] Back")

    while True:
        raw = input("Enter choice: ").strip()
        if raw == "0" or raw == "":
            return None
        try:
            choice = int(raw)
            if 1 <= choice <= len(sessions):
                return sessions[choice - 1]
            print(f"Invalid index. Please enter a number between 1 and {len(sessions)}, or 0 to go back.")
        except ValueError:
            print("Invalid input: please enter a valid number or 0 to go back.")


def select_equipment(equipment_list: list[Equipment]) -> Equipment | None:
    if not equipment_list:
        print("No equipment available")
        return None

    print("\nSelect equipment:")
    for idx, eq in enumerate(equipment_list, start=1):
        print(f"[{idx}] {eq.item_name} (Qty: {eq.quantity}, Sport: {eq.sport.name})")
    print("[0] Back")

    while True:
        raw = input("Enter choice: ").strip()
        if raw == "0" or raw == "":
            return None
        try:
            choice = int(raw)
            if 1 <= choice <= len(equipment_list):
                return equipment_list[choice - 1]
            print(f"Invalid index. Please enter a number between 1 and {len(equipment_list)}, or 0 to go back.")
        except ValueError:
            print("Invalid input: please enter a valid number or 0 to go back.")


# Обработчики пользовательских действий для роли Менеджера
def action_view_schedule() -> None:
    loc = select_location(db["locations"])
    if not loc:
        return
    print(f"\nSchedule for {loc.name_location}:")
    if not loc.schedule:
        print("No events scheduled")
        return
    for i, ev in enumerate(loc.schedule, start=1):
        if isinstance(ev, Tournament):
            ev_desc = f"Tournament: {ev.title} (Participants: {len(ev.participants)})"
        elif isinstance(ev, TrainingSession):
            ev_desc = f"Training: {ev.group.group_name} with {ev.coach.name} (Present: {len(ev.attendance)})"
        else:
            ev_desc = "General Event"
        print(f"[{i}] {ev_desc} at {ev.date_time} ({ev.duration_mins} mins)")


def action_schedule_training(manager: Manager) -> None:
    loc = select_location(db["locations"])
    if not loc:
        return
    group = select_group(db["groups"])
    if not group:
        return
    date_time = input("Enter date and time (DD.MM.YYYY HH:MM): ")
    try:
        duration = int(input("Enter duration in minutes: "))
        new_session = TrainingSession(
            date_time=date_time,
            duration_mins=duration,
            location=loc,
            group=group,
            coach=group.coach
        )
        services.schedule_event(manager=manager, event=new_session, location=loc)
        db["training_sessions"].append(new_session)
        print("Training session successfully scheduled")
    except (exceptions.InvalidFormatError, exceptions.InvalidValueError) as e:
        print(f"Validation error: {e}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")
    except ValueError:
        print("Duration must be a number")


def action_schedule_tournament(manager: Manager) -> None:
    loc = select_location(db["locations"])
    if not loc:
        return
    sport = select_sport(db["sports"])
    if not sport:
        return
    title = input("Enter tournament title: ")
    date_time = input("Enter date and time (DD.MM.YYYY HH:MM): ")
    try:
        duration = int(input("Enter duration in minutes: "))
        new_trn = Tournament(
            date_time=date_time,
            duration_mins=duration,
            location=loc,
            title=title,
            sport=sport
        )
        services.schedule_event(manager=manager, event=new_trn, location=loc)
        db["tournaments"].append(new_trn)
        print("Tournament successfully scheduled")
    except (exceptions.InvalidFormatError, exceptions.InvalidValueError) as e:
        print(f"Validation error: {e}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")
    except ValueError:
        print("Duration must be a number")


def action_cancel_event(manager: Manager) -> None:
    loc = select_location(db["locations"])
    if not loc:
        return
    if not loc.schedule:
        print("No events available to cancel in this location")
        return

    print(f"\nScheduled events for {loc.name_location}:")
    for i, ev in enumerate(loc.schedule, start=1):
        print(f"[{i}] {ev.date_time}")
    print("[0] Cancel")

    while True:
        raw = input("Select event index to cancel: ").strip()
        if raw == "0" or raw == "":
            return
        try:
            choice = int(raw)
            if 1 <= choice <= len(loc.schedule):
                event_to_cancel = loc.schedule[choice - 1]
                break
            print(f"Invalid index. Please enter a number between 1 and {len(loc.schedule)}, or 0 to cancel.")
        except ValueError:
            print("Invalid input: please enter a valid number or 0 to cancel.")

    try:
        services.cancel_event(manager=manager, event=event_to_cancel, location=loc)
        if isinstance(event_to_cancel, Tournament) and event_to_cancel in db["tournaments"]:
            db["tournaments"].remove(event_to_cancel)
        elif isinstance(event_to_cancel, TrainingSession) and event_to_cancel in db["training_sessions"]:
            db["training_sessions"].remove(event_to_cancel)
        print("Event successfully cancelled")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


def action_register_tournament(manager: Manager) -> None:
    athlete = select_athlete(db["athletes"])
    if not athlete:
        return
    tournament = select_tournament(db["tournaments"])
    if not tournament:
        return
    try:
        services.register_for_tournament(manager=manager, athlete=athlete, tournament=tournament)
        print(f"Athlete {athlete.name} successfully registered for {tournament.title}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


def action_award_tournament(manager: Manager) -> None:
    tournament = select_tournament(db["tournaments"])
    if not tournament:
        return
    try:
        services.award_tournament_participants(manager=manager, tournament=tournament)
        print("All tournament participants have been awarded certificates")
    except (exceptions.InvalidFormatError, exceptions.InvalidValueError) as e:
        print(f"Validation error: {e}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


def action_add_equipment(manager: Manager) -> None:
    sport = select_sport(db["sports"])
    if not sport:
        return
    item_name = input("Enter equipment name: ")
    try:
        quantity = int(input("Enter quantity: "))
        new_eq = Equipment(item_name=item_name, quantity=quantity, sport=sport)
        services.add_equipment(manager=manager, equipment=new_eq, equipment_list=db["equipment"])
        print("Equipment successfully added")
    except (exceptions.InvalidFormatError, exceptions.InvalidValueError) as e:
        print(f"Validation error: {e}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")
    except ValueError:
        print("Quantity must be a number")


def action_remove_equipment(manager: Manager) -> None:
    eq = select_equipment(db["equipment"])
    if not eq:
        return
    try:
        services.remove_equipment(manager=manager, equipment=eq, equipment_list=db["equipment"])
        print("Equipment successfully removed")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


def action_add_sport(manager: Manager) -> None:
    name = input("Enter sport name: ")
    category = input("Enter sport category: ")
    try:
        new_sport = Sport(name=name, category=category)
        services.add_sport(manager=manager, sport=new_sport, sports_list=db["sports"])
        print("Sport successfully added")
    except (exceptions.InvalidFormatError, exceptions.InvalidValueError) as e:
        print(f"Validation error: {e}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


# Обработчики пользовательских действий для роли Тренера
def action_create_group(coach: Coach) -> None:
    sport = select_sport(db["sports"])
    if not sport:
        return
    group_name = input("Enter group name: ")
    try:
        new_group = TrainingGroup(group_name=group_name, sport=sport, coach=coach)
        services.create_training_group(coach=coach, group=new_group, db_groups=db["groups"])
        print("Training group successfully created")
    except (exceptions.InvalidFormatError, exceptions.InvalidValueError) as e:
        print(f"Validation error: {e}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


def action_add_athlete_to_group(coach: Coach) -> None:
    group = select_group(coach.groups)
    if not group:
        return
    athlete = select_athlete(db["athletes"])
    if not athlete:
        return
    try:
        services.add_athlete_to_group(coach=coach, athlete=athlete, group=group)
        print("Athlete successfully added to the group")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


def action_remove_athlete_from_group(coach: Coach) -> None:
    group = select_group(coach.groups)
    if not group:
        return
    athlete = select_athlete(group.athletes)
    if not athlete:
        return
    try:
        services.remove_athlete_from_group(coach=coach, athlete=athlete, group=group)
        print("Athlete successfully removed from the group")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


def action_mark_attendance(coach: Coach) -> None:
    coach_sessions = [ts for ts in db["training_sessions"] if ts.coach == coach or ts.group in coach.groups]
    session = select_session(coach_sessions)
    if not session:
        return

    if not session.group.athletes:
        print("No athletes in this group")
        return

    athlete = select_athlete(session.group.athletes)
    if not athlete:
        return

    try:
        services.mark_session_attendance(coach=coach, athlete=athlete, session=session)
        print(f"Attendance marked for {athlete.name}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


def action_award_athlete(coach: Coach) -> None:
    group = select_group(coach.groups)
    if not group:
        return
    if not group.athletes:
        print("No athletes in this group")
        return

    athlete = select_athlete(group.athletes)
    if not athlete:
        return

    title = input("Enter achievement title: ")
    date_awarded = input("Enter date awarded (DD.MM.YYYY): ")
    try:
        achievement = Achievement(title=title, date_awarded=date_awarded, sport=group.sport)
        services.award_athlete(coach=coach, athlete=athlete, achievement=achievement, group=group)
        print(f"Achievement added for {athlete.name}")
    except (exceptions.InvalidFormatError, exceptions.InvalidValueError) as e:
        print(f"Validation error: {e}")
    except exceptions.BusinessLogicError as e:
        print(f"Business logic error: {e}")


# Обработчики пользовательских действий для роли Спортсмена
def action_view_athlete_profile(athlete: Athlete) -> None:
    print("\n--- My Profile ---")
    print(athlete.get_info())
    if athlete.achievements:
        print("\nMy Achievements:")
        for ach in athlete.achievements:
            print(f"- {ach.title} ({ach.sport.name}, {ach.date_awarded})")


def action_view_athlete_schedule(athlete: Athlete) -> None:
    print("\n--- My Schedule ---")
    my_sessions = [ts for ts in db["training_sessions"] if athlete in ts.group.athletes]
    my_tournaments = [trn for trn in db["tournaments"] if athlete in trn.participants]

    if not my_sessions and not my_tournaments:
        print("No events scheduled")
        return

    for ts in my_sessions:
        print(f"Training: {ts.group.group_name} at {ts.date_time} ({ts.location.name_location})")
    for trn in my_tournaments:
        print(f"Tournament: {trn.title} at {trn.date_time} ({trn.location.name_location})")


def action_update_medical_certificate(athlete: Athlete) -> None:
    issue_date = input("Enter issue date (DD.MM.YYYY): ")
    is_valid_str = input("Is the certificate valid? (y/n): ").strip().lower()
    is_valid = (is_valid_str == "y")
    try:
        cert = MedicalCertificate(issue_date=issue_date, is_valid=is_valid)
        athlete.add_medical_certificate(cert)
        print("Medical certificate successfully updated")
    except (exceptions.InvalidFormatError, exceptions.InvalidValueError, TypeError) as e:
        print(f"Validation error: {e}")


# Регистрация нового пользователя в системе
def action_register_user() -> None:
    print("\nRegister as:")
    print("[1] Manager")
    print("[2] Coach")
    print("[3] Athlete")
    print("[0] Cancel")

    choice = input("Select role: ").strip()
    if choice == "0" or choice == "":
        return
    if choice not in ("1", "2", "3"):
        print("Invalid choice")
        return

    try:
        person_id = int(input("Enter new ID: "))
        # Проверка уникальности ID среди всех категорий пользователей
        existing_ids = [
            p.person_id for p in (db["managers"] + db["coaches"] + db["athletes"])
        ]
        if person_id in existing_ids:
            print(f"User with ID {person_id} already exists")
            return

        name = input("Enter name: ")
        phone = input("Enter phone (+7XXXXXXXXXX or 8XXXXXXXXXX): ")

        if choice == "1":
            access_level = int(input("Enter access level (1-3): "))
            new_manager = Manager(access_level=access_level, person_id=person_id, name=name, phone=phone)
            db["managers"].append(new_manager)
            print("Manager successfully registered")

        elif choice == "2":
            exp = int(input("Enter experience years: "))
            spec = input("Enter specialization: ")
            new_coach = Coach(person_id=person_id, name=name, phone=phone, experience_years=exp, specialization=spec)
            db["coaches"].append(new_coach)
            print("Coach successfully registered")

        elif choice == "3":
            birth = input("Enter birth date (DD.MM.YYYY): ")
            new_athlete = Athlete(person_id=person_id, name=name, phone=phone, birth_date=birth)
            db["athletes"].append(new_athlete)
            print("Athlete successfully registered")

    except (exceptions.InvalidFormatError, exceptions.InvalidValueError) as e:
        print(f"Validation error: {e}")
    except ValueError:
        print("ID and numeric fields must be valid numbers")


# Меню по ролям пользователей и точка входа в программу
def manager_menu(manager: Manager) -> None:
    while True:
        print(f"\n--- Manager Dashboard (Level {manager.access_level}) ---")
        print("[1] View location schedule")
        print("[2] Schedule a training session")
        print("[3] Schedule a tournament")
        print("[4] Cancel an event")
        print("[5] Register athlete for tournament")
        print("[6] Issue certificates for tournament participants")
        print("[7] Add equipment")
        print("[8] Remove equipment")
        print("[9] Add sport")
        print("[0] Logout")

        choice = input("Select an action: ")
        if choice == "1":
            action_view_schedule()
        elif choice == "2":
            action_schedule_training(manager)
        elif choice == "3":
            action_schedule_tournament(manager)
        elif choice == "4":
            action_cancel_event(manager)
        elif choice == "5":
            action_register_tournament(manager)
        elif choice == "6":
            action_award_tournament(manager)
        elif choice == "7":
            action_add_equipment(manager)
        elif choice == "8":
            action_remove_equipment(manager)
        elif choice == "9":
            action_add_sport(manager)
        elif choice == "0":
            break
        else:
            print("Invalid input")


def coach_menu(coach: Coach) -> None:
    while True:
        print("\n--- Coach Dashboard ---")
        print("[1] View my groups")
        print("[2] Mark training attendance")
        print("[3] Award athlete")
        print("[4] Create training group")
        print("[5] Add athlete to group")
        print("[6] Remove athlete from group")
        print("[0] Logout")

        choice = input("Select an action: ")
        if choice == "1":
            if not coach.groups:
                print("No groups assigned")
            else:
                for g in coach.groups:
                    print(f"- {g.group_name} ({len(g.athletes)} athletes)")
        elif choice == "2":
            action_mark_attendance(coach)
        elif choice == "3":
            action_award_athlete(coach)
        elif choice == "4":
            action_create_group(coach)
        elif choice == "5":
            action_add_athlete_to_group(coach)
        elif choice == "6":
            action_remove_athlete_from_group(coach)
        elif choice == "0":
            break
        else:
            print("Invalid input")


def athlete_menu(athlete: Athlete) -> None:
    while True:
        print("\n--- Athlete Dashboard ---")
        print("[1] View profile & achievements")
        print("[2] View my training schedule")
        print("[3] Update medical certificate")
        print("[0] Logout")

        choice = input("Select an action: ")
        if choice == "1":
            action_view_athlete_profile(athlete)
        elif choice == "2":
            action_view_athlete_schedule(athlete)
        elif choice == "3":
            action_update_medical_certificate(athlete)
        elif choice == "0":
            break
        else:
            print("Invalid input")


def login() -> Person | None:
    if not db["managers"] and not db["coaches"] and not db["athletes"]:
        print("Database is empty, please import data or register a new user first")
        return None
    try:
        user_id = int(input("Enter your ID: "))
        for m in db["managers"]:
            if m.person_id == user_id:
                return m
        for c in db["coaches"]:
            if c.person_id == user_id:
                return c
        for a in db["athletes"]:
            if a.person_id == user_id:
                return a
        print("User not found")
        return None
    except ValueError:
        print("ID must be a number")
        return None


def main() -> None:
    global db
    while True:
        print("\n=== SPORTS CLUB SYSTEM ===")
        print("[1] Login by ID")
        print("[2] Import from JSON")
        print("[3] Export to JSON")
        print("[4] Import from XML")
        print("[5] Export to XML")
        print("[6] Register new user")
        print("[0] Exit")

        choice = input("Select an action: ")
        if choice == "1":
            user = login()
            if user:
                print(f"\nWelcome, {user.name}")
                if isinstance(user, Manager):
                    manager_menu(user)
                elif isinstance(user, Coach):
                    coach_menu(user)
                elif isinstance(user, Athlete):
                    athlete_menu(user)
        elif choice == "2":
            path = input("Enter JSON filename (default data.json): ").strip() or "data.json"
            db = storage.load_json(path)
        elif choice == "3":
            path = input("Enter JSON filename (default data.json): ").strip() or "data.json"
            storage.save_json(path, db)
        elif choice == "4":
            path = input("Enter XML filename (default data.xml): ").strip() or "data.xml"
            db = storage.load_xml(path)
        elif choice == "5":
            path = input("Enter XML filename (default data.xml): ").strip() or "data.xml"
            storage.save_xml(path, db)
        elif choice == "6":
            action_register_user()
        elif choice == "0":
            break
        else:
            print("Invalid input")


if __name__ == "__main__":
    main()