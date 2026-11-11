from datetime import datetime, timedelta
from models import (
    Manager, Coach, Athlete, Event, Location,
    Tournament, TrainingSession, TrainingGroup, Achievement, Equipment, Sport
)
import exceptions


# Планирование мероприятия с проверкой уровня доступа и пересечения интервалов времени
def schedule_event(manager: Manager, event: Event, location: Location) -> None:
    if manager.access_level < 2:
        raise exceptions.AccessDeniedError("Access denied: insufficient permissions to schedule events")

    new_start = datetime.strptime(event.date_time, "%d.%m.%Y %H:%M")
    new_end = new_start + timedelta(minutes=event.duration_mins)

    # Проверка накладок в расписании выбранного зала
    for existing_event in location.schedule:
        exist_start = datetime.strptime(existing_event.date_time, "%d.%m.%Y %H:%M")
        exist_end = exist_start + timedelta(minutes=existing_event.duration_mins)

        if new_start < exist_end and exist_start < new_end:
            raise exceptions.ScheduleConflictError("The location is already booked for this time")

    location.schedule.append(event)


# Отмена запланированного мероприятия (доступно только менеджерам 3-го уровня)
def cancel_event(manager: Manager, event: Event, location: Location) -> None:
    if manager.access_level < 3:
        raise exceptions.AccessDeniedError("Access denied: only level 3 managers can cancel events")

    if event in location.schedule:
        location.schedule.remove(event)
    else:
        raise exceptions.BusinessLogicError("Event not found in this location schedule")


# Регистрация спортсмена на турнир с обязательной проверкой медицинской справки
def register_for_tournament(manager: Manager, athlete: Athlete, tournament: Tournament) -> None:
    if manager.access_level < 1:
        raise exceptions.AccessDeniedError("Access denied: insufficient permissions")

    if not athlete.certificate:
        raise exceptions.BusinessLogicError(f"Athlete {athlete.name} has no medical certificate")

    if not athlete.certificate.is_valid:
        raise exceptions.BusinessLogicError(f"Medical certificate for {athlete.name} is expired or invalid")

    if athlete in tournament.participants:
        raise exceptions.BusinessLogicError(f"Athlete {athlete.name} is already registered")

    tournament.add_participant(athlete)


# Массовая выдача сертификатов участникам по завершении турнира
def award_tournament_participants(manager: Manager, tournament: Tournament) -> None:
    if manager.access_level < 2:
        raise exceptions.AccessDeniedError("Access denied: insufficient permissions to issue tournament awards")

    if not tournament.participants:
        raise exceptions.BusinessLogicError("No participants registered for this tournament")

    award_date = datetime.now().strftime("%d.%m.%Y")
    for athlete in tournament.participants:
        certificate_ach = Achievement(
            title=f"Participant of {tournament.title}",
            date_awarded=award_date,
            sport=tournament.sport
        )
        athlete.add_achievement(certificate_ach)


# Индивидуальное награждение спортсмена тренером своей группы
def award_athlete(coach: Coach, athlete: Athlete, achievement: Achievement, group: TrainingGroup) -> None:
    if group not in coach.groups:
        raise exceptions.AccessDeniedError("Coach can only award athletes in their own groups")

    if athlete not in group.athletes:
        raise exceptions.BusinessLogicError("Athlete is not a member of this training group")

    athlete.add_achievement(achievement)


# Отметка посещаемости тренировки тренером
def mark_session_attendance(coach: Coach, athlete: Athlete, session: TrainingSession) -> None:
    if session.coach != coach and session.group not in coach.groups:
        raise exceptions.AccessDeniedError("Coach can only mark attendance for their own training sessions")

    if athlete not in session.group.athletes:
        raise exceptions.BusinessLogicError("Athlete is not a member of this training group")

    if athlete in session.attendance:
        raise exceptions.BusinessLogicError(f"Athlete {athlete.name} is already marked as present")

    session.mark_attendance(athlete)


# Управление спортивным инвентарем и справочниками
def add_equipment(manager: Manager, equipment: Equipment, equipment_list: list[Equipment]) -> None:
    if manager.access_level < 2:
        raise exceptions.AccessDeniedError("Access denied: insufficient permissions to manage equipment")
    equipment_list.append(equipment)


def remove_equipment(manager: Manager, equipment: Equipment, equipment_list: list[Equipment]) -> None:
    if manager.access_level < 2:
        raise exceptions.AccessDeniedError("Access denied: insufficient permissions to manage equipment")
    if equipment in equipment_list:
        equipment_list.remove(equipment)
    else:
        raise exceptions.BusinessLogicError("Equipment not found")


def add_sport(manager: Manager, sport: Sport, sports_list: list[Sport]) -> None:
    if manager.access_level < 2:
        raise exceptions.AccessDeniedError("Access denied: insufficient permissions to manage sports")
    for existing in sports_list:
        if existing.name.lower() == sport.name.lower():
            raise exceptions.BusinessLogicError("This sport already exists")
    sports_list.append(sport)


# Управление тренировочными группами тренером
def create_training_group(coach: Coach, group: TrainingGroup, db_groups: list[TrainingGroup]) -> None:
    coach.assign_to_group(group)
    db_groups.append(group)


def add_athlete_to_group(coach: Coach, athlete: Athlete, group: TrainingGroup) -> None:
    if group not in coach.groups:
        raise exceptions.AccessDeniedError("Access denied: you can only manage your own groups")
    if athlete in group.athletes:
        raise exceptions.BusinessLogicError(f"Athlete {athlete.name} is already in the group")
    group.add_athlete(athlete)


def remove_athlete_from_group(coach: Coach, athlete: Athlete, group: TrainingGroup) -> None:
    if group not in coach.groups:
        raise exceptions.AccessDeniedError("Access denied: you can only manage your own groups")
    if athlete not in group.athletes:
        raise exceptions.BusinessLogicError(f"Athlete {athlete.name} is not in the group")
    group.remove_athlete(athlete)