import re
import exceptions
from datetime import datetime

class Person:
    def __init__(self, person_id: int, name: str, phone: str) -> None:
        self._person_id: int = self._validate_id(person_id)
        self.name: str = name
        self.phone: str = phone

    def _validate_id(self, person_id: int) -> int:
        if person_id < 0:
            raise exceptions.InvalidIdValueError("The ID cannot be negative")
        return person_id
    
    @property
    def person_id(self) -> int:
        return self._person_id

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
        self.certificate: bool = None
        self.achievements: list = []

    @property
    def birth_date(self) -> str:
        return self._birth_date

    @birth_date.setter
    def birth_date(self, value: str) -> None:
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', value):
            raise exceptions.InvalidBirthDateFormatError("Invalid birth date format. Expected: DD.MM.YYYY")
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise exceptions.InvalidBirthDateError("An invalid date has been specified")
        if parsed_date > datetime.now():
            raise exceptions.InvalidBirthDateError("The date of birth cannot be in the future")
        
        self._birth_date = value

    def get_info(self) -> str:
        base_info = super().get_info()
        
        return (f"{base_info}\n"
                f"Birth Date: {self.birth_date}\n"
                f"Achievements: {len(self.achievements)}\n"
                f"Certificate: {'Yes' if self.certificate else 'No'}")

class Coach(Person):
    def __init__(self, person_id: int, name: str, phone: str, experience_years: int, specialization: str) -> None:
        super().__init__(person_id, name, phone)
        self.experience_years: int = experience_years
        self.specialization: str = specialization

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