from __future__ import annotations
import re
import exceptions
from datetime import datetime

class Person:
    def __init__(self, person_id: int, name: str, phone: str) -> None:
        self._person_id: int = self._validate_id(person_id)
        self.name: str = name
        self.phone: str = phone

    @property
    def person_id(self) -> int:
        return self._person_id   

    def _validate_id(self, person_id: int) -> int:
        if person_id < 0:
            raise exceptions.InvalidIdValueError("The ID cannot be negative")
        return person_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if value.strip() == "":
            raise exceptions.InvalidNameFormatError("The name cannot be empty")
        self._name = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        if not re.match(r'^(8|\+7)\d{10}$', value):
            raise exceptions.InvalidPhoneFormatError(f"Invalid phone format: {value}")
        self._phone = value

    def get_info(self) -> str:
        return (f"ID: {self.person_id}\n"
                f"Name: {self.name}\n"
                f"Phone: {self.phone}")

class Athlete(Person):
    def __init__(self, person_id: int, name: str, phone: str, birth_date: str) -> None:
        super().__init__(person_id, name, phone)
        self.birth_date: str = birth_date
        self.certificate: MedicalCertificate | None = None
        self._achievements: list[Achievement] = []

    @property
    def birth_date(self) -> str:
        return self._birth_date

    @birth_date.setter
    def birth_date(self, value: str) -> None:
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', value):
            raise exceptions.InvalidDateFormatError("Invalid date format. Expected: DD.MM.YYYY")
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise exceptions.InvalidDateError("An invalid date has been specified")
        if parsed_date > datetime.now():
            raise exceptions.InvalidDateError("The date of birth cannot be in the future")
        self._birth_date = value

    def get_info(self) -> str:
        base_info = super().get_info()
        
        return (f"{base_info}\n"
                f"Birth Date: {self.birth_date}\n"
                f"Achievements: {len(self._achievements)}\n"
                f"Certificate: {'Yes' if self.certificate else 'No'}")
        
    def add_achievement(self, achievement: Achievement) -> None:
        self._achievements.append(achievement)
        print(f"{achievement.title} successfully added")

    def add_medical_certificate(self, certificate: MedicalCertificate) -> None:
        self.certificate = certificate

class MedicalCertificate:
    def __init__(self, issue_date: str, is_valid: bool) -> None:
        self.issue_date: str = issue_date
        self.is_valid: bool = is_valid

    @property
    def issue_date(self) -> str:
        return self._issue_date
        
    @issue_date.setter
    def issue_date(self, value: str) -> None:
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', value):
            raise exceptions.InvalidDateFormatError("Invalid date format. Expected: DD.MM.YYYY")
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise exceptions.InvalidDateError("An invalid date has been specified")
        if parsed_date > datetime.now():
            raise exceptions.InvalidDateError("The issue date cannot be in the future")
        self._issue_date = value

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value: bool):
        if not isinstance(value, bool):
            raise exceptions.InvalidValueError("Invalid data type")
        self._is_valid = value
    
class Coach(Person):
    def __init__(self, person_id: int, name: str, phone: str, experience_years: int, specialization: str) -> None:
        super().__init__(person_id, name, phone)
        self.experience_years: int = experience_years
        self.specialization: str = specialization
        self._groups: list[TrainingGroup] = []

    @property
    def experience_years(self) -> int:
        return self._experience_years

    @experience_years.setter
    def experience_years(self, value: int) -> None:
        if value < 3:
            raise exceptions.InvalidExperienceYearsError("Length of service does not meet the requirements")
        self._experience_years = value

    @property
    def specialization(self) -> str:
        return self._specialization

    @specialization.setter
    def specialization(self, value: str) -> None:
        if value.strip() == "":
            raise exceptions.InvalidSpecializationFormatError("Specialization cannot be empty")
        self._specialization = value

    def get_info(self) -> str:
        base_info = super().get_info()
        
        return (f"{base_info}\n"
                f"Experience years: {self.experience_years}\n"
                f"Specialization: {self.specialization}\n"
                f"Number of groups: {len(self._groups)}")

    def assign_to_group(self, group: TrainingGroup) -> None:
        self._groups.append(group)
        print(f"Coach {self.name} has been successfully assigned to the group: {group.group_name}")

class Event:
    def __init__(self, date_time: str, duration_mins: int, location: Location) -> None:
        self._date_time: str = self._validate_date_time(date_time)
        self._duration_mins: int = self._validate_duration_mins(duration_mins)
        self.location: Location = location

    @property
    def date_time(self) -> str:
        return self._date_time

    def _validate_date_time(self, date_time: str) -> str:
        if not re.match(r'^\d{2}\.\d{2}\.\d{4} \d{2}\:\d{2}', date_time):
            raise exceptions.InvalidDateFormatError("Invalid date format. Expected: DD.MM.YYYY HH:MM")
        try:
            datetime.strptime(date_time, "%d.%m.%Y %H:%M")
        except ValueError:
            raise exceptions.InvalidDateError("An invalid date time has been specified")
        return date_time                    

    @property 
    def duration_mins(self) -> int:
        return self._duration_mins

    def _validate_duration_mins(self, duration_mins: int) -> int:
        if duration_mins <= 0:
            raise exceptions.InvalidIdValueError("The duration in minutes must be positive")
        return duration_mins