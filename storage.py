import json
import xml.etree.ElementTree as ET
from models import (
    Manager, Coach, Athlete, MedicalCertificate, Achievement,
    Sport, Equipment, TrainingGroup, Event, TrainingSession, Tournament, Location
)
import exceptions


# Инициализация пустой структуры данных в памяти
def create_empty_db() -> dict[str, list]:
    return {
        "sports": [],
        "managers": [],
        "coaches": [],
        "athletes": [],
        "locations": [],
        "equipment": [],
        "groups": [],
        "training_sessions": [],
        "tournaments": []
    }


# Десериализация: восстановление графа объектов и связей из словаря сырых данных
def _build_objects(raw_data: dict) -> dict[str, list]:
    db = create_empty_db()
    # Вспомогательные словари-индексы для быстрого связывания объектов по ID и именам
    sport_map: dict[str, Sport] = {}
    coach_map: dict[int, Coach] = {}
    athlete_map: dict[int, Athlete] = {}
    location_map: dict[str, Location] = {}
    group_map: dict[str, TrainingGroup] = {}

    for s in raw_data.get("sports", []):
        try:
            sport = Sport(name=s["name"], category=s["category"])
            db["sports"].append(sport)
            sport_map[sport.name] = sport
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError) as e:
            print(f"Error loading sport: {e}")

    for m in raw_data.get("managers", []):
        try:
            manager = Manager(
                access_level=int(m["access_level"]),
                person_id=int(m["person_id"]),
                name=m["name"],
                phone=m["phone"]
            )
            db["managers"].append(manager)
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError, ValueError) as e:
            print(f"Error loading manager: {e}")

    for c in raw_data.get("coaches", []):
        try:
            coach = Coach(
                person_id=int(c["person_id"]),
                name=c["name"],
                phone=c["phone"],
                experience_years=int(c["experience_years"]),
                specialization=c["specialization"]
            )
            db["coaches"].append(coach)
            coach_map[coach.person_id] = coach
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError, ValueError) as e:
            print(f"Error loading coach: {e}")

    for a in raw_data.get("athletes", []):
        try:
            athlete = Athlete(
                person_id=int(a["person_id"]),
                name=a["name"],
                phone=a["phone"],
                birth_date=a["birth_date"]
            )
            cert_data = a.get("certificate")
            if cert_data:
                is_val = cert_data["is_valid"]
                if isinstance(is_val, str):
                    is_val = is_val.lower() == "true"
                cert = MedicalCertificate(issue_date=cert_data["issue_date"], is_valid=is_val)
                athlete.add_medical_certificate(cert)

            for ach in a.get("achievements", []):
                sp = sport_map.get(ach["sport"])
                if sp:
                    achievement = Achievement(title=ach["title"], date_awarded=ach["date_awarded"], sport=sp)
                    athlete.add_achievement(achievement)

            db["athletes"].append(athlete)
            athlete_map[athlete.person_id] = athlete
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError, ValueError, TypeError) as e:
            print(f"Error loading athlete: {e}")

    for l in raw_data.get("locations", []):
        try:
            loc = Location(name_location=l["name_location"], capacity=int(l["capacity"]))
            for ev in l.get("schedule", []):
                event = Event(
                    date_time=ev["date_time"],
                    duration_mins=int(ev["duration_mins"]),
                    location=loc
                )
                loc.schedule.append(event)
            db["locations"].append(loc)
            location_map[loc.name_location] = loc
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError, ValueError) as e:
            print(f"Error loading location: {e}")

    for eq in raw_data.get("equipment", []):
        try:
            sp = sport_map.get(eq["sport"])
            if sp:
                item = Equipment(item_name=eq["item_name"], quantity=int(eq["quantity"]), sport=sp)
                db["equipment"].append(item)
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError, ValueError) as e:
            print(f"Error loading equipment: {e}")

    for g in raw_data.get("groups", []):
        try:
            sp = sport_map.get(g["sport"])
            coach = coach_map.get(int(g["coach_id"]))
            if sp and coach:
                group = TrainingGroup(group_name=g["group_name"], sport=sp, coach=coach)
                coach.assign_to_group(group)
                for ath_id in g.get("athlete_ids", []):
                    ath = athlete_map.get(int(ath_id))
                    if ath:
                        group.add_athlete(ath)
                db["groups"].append(group)
                group_map[group.group_name] = group
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError, ValueError) as e:
            print(f"Error loading group: {e}")

    for ts in raw_data.get("training_sessions", []):
        try:
            loc = location_map.get(ts["location"])
            group = group_map.get(ts["group_name"])
            coach = coach_map.get(int(ts["coach_id"]))
            if loc and group and coach:
                session = TrainingSession(
                    date_time=ts["date_time"],
                    duration_mins=int(ts["duration_mins"]),
                    location=loc,
                    group=group,
                    coach=coach
                )
                for a_id in ts.get("attendance_ids", []):
                    ath = athlete_map.get(int(a_id))
                    if ath:
                        session.mark_attendance(ath)
                loc.schedule.append(session)
                db["training_sessions"].append(session)
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError, ValueError) as e:
            print(f"Error loading training session: {e}")

    for t in raw_data.get("tournaments", []):
        try:
            loc = location_map.get(t["location"])
            sp = sport_map.get(t["sport"])
            if loc and sp:
                trn = Tournament(
                    date_time=t["date_time"],
                    duration_mins=int(t["duration_mins"]),
                    location=loc,
                    title=t["title"],
                    sport=sp
                )
                for p_id in t.get("participant_ids", []):
                    ath = athlete_map.get(int(p_id))
                    if ath:
                        trn.add_participant(ath)
                loc.schedule.append(trn)
                db["tournaments"].append(trn)
        except (exceptions.InvalidFormatError, exceptions.InvalidValueError, KeyError, ValueError) as e:
            print(f"Error loading tournament: {e}")

    return db


# Сериализация: преобразование живых объектов в примитивные структуры для сохранения
def _serialize_objects(db: dict) -> dict:
    return {
        "sports": [
            {"name": s.name, "category": s.category}
            for s in db["sports"]
        ],
        "managers": [
            {
                "access_level": m.access_level,
                "person_id": m.person_id,
                "name": m.name,
                "phone": m.phone
            }
            for m in db["managers"]
        ],
        "coaches": [
            {
                "person_id": c.person_id,
                "name": c.name,
                "phone": c.phone,
                "experience_years": c.experience_years,
                "specialization": c.specialization
            }
            for c in db["coaches"]
        ],
        "athletes": [
            {
                "person_id": a.person_id,
                "name": a.name,
                "phone": a.phone,
                "birth_date": a.birth_date,
                "certificate": {
                    "issue_date": a.certificate.issue_date,
                    "is_valid": a.certificate.is_valid
                } if a.certificate else None,
                "achievements": [
                    {
                        "title": ach.title,
                        "date_awarded": ach.date_awarded,
                        "sport": ach.sport.name
                    }
                    for ach in a.achievements
                ]
            }
            for a in db["athletes"]
        ],
        "locations": [
            {
                "name_location": l.name_location,
                "capacity": l.capacity,
                # Тренировки и турниры сохраняются в отдельных списках, чтобы избежать дублирования
                "schedule": [
                    {
                        "date_time": ev.date_time,
                        "duration_mins": ev.duration_mins
                    }
                    for ev in l.schedule if not isinstance(ev, (Tournament, TrainingSession))
                ]
            }
            for l in db["locations"]
        ],
        "equipment": [
            {
                "item_name": eq.item_name,
                "quantity": eq.quantity,
                "sport": eq.sport.name
            }
            for eq in db["equipment"]
        ],
        "groups": [
            {
                "group_name": g.group_name,
                "sport": g.sport.name,
                "coach_id": g.coach.person_id,
                "athlete_ids": [a.person_id for a in g.athletes]
            }
            for g in db["groups"]
        ],
        "training_sessions": [
            {
                "date_time": ts.date_time,
                "duration_mins": ts.duration_mins,
                "location": ts.location.name_location,
                "group_name": ts.group.group_name,
                "coach_id": ts.coach.person_id,
                "attendance_ids": [a.person_id for a in ts.attendance]
            }
            for ts in db["training_sessions"]
        ],
        "tournaments": [
            {
                "date_time": t.date_time,
                "duration_mins": t.duration_mins,
                "location": t.location.name_location,
                "title": t.title,
                "sport": t.sport.name,
                "participant_ids": [p.person_id for p in t.participants]
            }
            for t in db["tournaments"]
        ]
    }


# Чтение и запись данных в формате JSON
def load_json(filepath: str) -> dict[str, list]:
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
        print(f"Data successfully imported from {filepath}")
        return _build_objects(raw_data)
    except FileNotFoundError:
        print(f"File {filepath} not found")
        return create_empty_db()
    except json.JSONDecodeError:
        print(f"Invalid JSON format in {filepath}")
        return create_empty_db()
    except OSError as e:
        print(f"File error: {e}")
        return create_empty_db()


def save_json(filepath: str, db: dict) -> None:
    try:
        data = _serialize_objects(db)
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data successfully exported to {filepath}")
    except OSError as e:
        print(f"Failed to export JSON: {e}")


# Запись и чтение данных в формате XML (с использованием дерева элементов ElementTree)
def save_xml(filepath: str, db: dict) -> None:
    try:
        data = _serialize_objects(db)
        root = ET.Element("club_data")

        sports_el = ET.SubElement(root, "sports")
        for s in data["sports"]:
            ET.SubElement(sports_el, "sport", {"name": s["name"], "category": s["category"]})

        managers_el = ET.SubElement(root, "managers")
        for m in data["managers"]:
            ET.SubElement(managers_el, "manager", {
                "access_level": str(m["access_level"]),
                "person_id": str(m["person_id"]),
                "name": m["name"],
                "phone": m["phone"]
            })

        coaches_el = ET.SubElement(root, "coaches")
        for c in data["coaches"]:
            ET.SubElement(coaches_el, "coach", {
                "person_id": str(c["person_id"]),
                "name": c["name"],
                "phone": c["phone"],
                "experience_years": str(c["experience_years"]),
                "specialization": c["specialization"]
            })

        athletes_el = ET.SubElement(root, "athletes")
        for a in data["athletes"]:
            ath_el = ET.SubElement(athletes_el, "athlete", {
                "person_id": str(a["person_id"]),
                "name": a["name"],
                "phone": a["phone"],
                "birth_date": a["birth_date"]
            })
            if a["certificate"]:
                ET.SubElement(ath_el, "certificate", {
                    "issue_date": a["certificate"]["issue_date"],
                    "is_valid": str(a["certificate"]["is_valid"])
                })
            achs_el = ET.SubElement(ath_el, "achievements")
            for ach in a["achievements"]:
                ET.SubElement(achs_el, "achievement", {
                    "title": ach["title"],
                    "date_awarded": ach["date_awarded"],
                    "sport": ach["sport"]
                })

        locations_el = ET.SubElement(root, "locations")
        for l in data["locations"]:
            loc_el = ET.SubElement(locations_el, "location", {
                "name_location": l["name_location"],
                "capacity": str(l["capacity"])
            })
            sched_el = ET.SubElement(loc_el, "schedule")
            for ev in l["schedule"]:
                ET.SubElement(sched_el, "event", {
                    "date_time": ev["date_time"],
                    "duration_mins": str(ev["duration_mins"])
                })

        equipment_el = ET.SubElement(root, "equipment")
        for eq in data["equipment"]:
            ET.SubElement(equipment_el, "item", {
                "item_name": eq["item_name"],
                "quantity": str(eq["quantity"]),
                "sport": eq["sport"]
            })

        groups_el = ET.SubElement(root, "groups")
        for g in data["groups"]:
            g_el = ET.SubElement(groups_el, "group", {
                "group_name": g["group_name"],
                "sport": g["sport"],
                "coach_id": str(g["coach_id"])
            })
            for ath_id in g["athlete_ids"]:
                ET.SubElement(g_el, "athlete_id", {"id": str(ath_id)})

        sessions_el = ET.SubElement(root, "training_sessions")
        for ts in data["training_sessions"]:
            ts_el = ET.SubElement(sessions_el, "training_session", {
                "date_time": ts["date_time"],
                "duration_mins": str(ts["duration_mins"]),
                "location": ts["location"],
                "group_name": ts["group_name"],
                "coach_id": str(ts["coach_id"])
            })
            for a_id in ts["attendance_ids"]:
                ET.SubElement(ts_el, "attendance_id", {"id": str(a_id)})

        tournaments_el = ET.SubElement(root, "tournaments")
        for t in data["tournaments"]:
            t_el = ET.SubElement(tournaments_el, "tournament", {
                "date_time": t["date_time"],
                "duration_mins": str(t["duration_mins"]),
                "location": t["location"],
                "title": t["title"],
                "sport": t["sport"]
            })
            for p_id in t["participant_ids"]:
                ET.SubElement(t_el, "participant_id", {"id": str(p_id)})

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ")
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
        print(f"Data successfully exported to {filepath}")
    except OSError as e:
        print(f"Failed to export XML: {e}")


def load_xml(filepath: str) -> dict[str, list]:
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"File {filepath} not found")
        return create_empty_db()
    except ET.ParseError:
        print(f"Invalid XML format in {filepath}")
        return create_empty_db()
    except OSError as e:
        print(f"File error: {e}")
        return create_empty_db()

    raw_data = create_empty_db()

    for s in root.findall("./sports/sport"):
        raw_data["sports"].append(dict(s.attrib))

    for m in root.findall("./managers/manager"):
        raw_data["managers"].append(dict(m.attrib))

    for c in root.findall("./coaches/coach"):
        raw_data["coaches"].append(dict(c.attrib))

    for a in root.findall("./athletes/athlete"):
        ath_dict = dict(a.attrib)
        cert_el = a.find("certificate")
        ath_dict["certificate"] = dict(cert_el.attrib) if cert_el is not None else None
        ath_dict["achievements"] = [dict(ach.attrib) for ach in a.findall("./achievements/achievement")]
        raw_data["athletes"].append(ath_dict)

    for l in root.findall("./locations/location"):
        loc_dict = dict(l.attrib)
        loc_dict["schedule"] = [dict(ev.attrib) for ev in l.findall("./schedule/event")]
        raw_data["locations"].append(loc_dict)

    for eq in root.findall("./equipment/item"):
        raw_data["equipment"].append(dict(eq.attrib))

    for g in root.findall("./groups/group"):
        g_dict = dict(g.attrib)
        g_dict["athlete_ids"] = [int(el.attrib["id"]) for el in g.findall("athlete_id")]
        raw_data["groups"].append(g_dict)

    for ts in root.findall("./training_sessions/training_session"):
        ts_dict = dict(ts.attrib)
        ts_dict["attendance_ids"] = [int(el.attrib["id"]) for el in ts.findall("attendance_id")]
        raw_data["training_sessions"].append(ts_dict)

    for t in root.findall("./tournaments/tournament"):
        t_dict = dict(t.attrib)
        t_dict["participant_ids"] = [int(el.attrib["id"]) for el in t.findall("participant_id")]
        raw_data["tournaments"].append(t_dict)

    print(f"Data successfully imported from {filepath}")
    return _build_objects(raw_data)