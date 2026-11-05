import re
import exceptions
from datetime import datetime

class Person:
    def __init__(self, person_id: int, name: str, phone: str) -> None:
        self.person_id: int = self._validate_id(person_id)
        self.name: str = self._validate_name(name)
        self.phone: str = self._validate_phone(phone)

    def _validate_id(self, person_id: int) -> int:
        if person_id < 0:
            raise exceptions.InvalidIdFormatError("The ID cannot be negative")
        return person_id
    
    def _validate_name(self, name: str) -> str:
        if name.strip() == "":
            raise exceptions.InvalidNameFormatError("The name cannot be empty")
        return name

    def _validate_phone(self, phone: str) -> str:
        if not re.match(r'^(8|\+7)\d{10}$', phone):
            raise exceptions.InvalidPhoneFormatError(f"Invalid phone format: {phone}")
        return phone

    def get_info(self) -> str:
        return f"id: {self.person_id}\nname: {self.name}\nphone: {self.phone}"

class Athlete(Person):
    def __init__(self, person_id: int, name: str, phone: str, birth_date: str) -> None:
        super().__init__(person_id, name, phone)
        self.birth_date: str = self._validate_birth_date(birth_date)
        self.certificate = None
        self.achievement: list = []

    def _validate_birth_date(self, birth_date) -> str:
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birth_date):
            raise exceptions.InvalidBirthDateFormatError("Invalid birth date format. Expected: DD.MM.YYYY")

        try:
            parsed_date = datetime.strptime(birth_date, "%d.%m.%Y")
        except ValueError:
            raise exceptions.InvalidBirthDateError("An invalid date has been specified")

        if parsed_date > datetime.now():
            raise exceptions.InvalidBirthDateError("The date of birth cannot be in the future")
        
        return birth_date

