# Базовые и специализированные исключения для валидации формата данных
class InvalidFormatError(Exception):
    pass


class InvalidNameFormatError(InvalidFormatError):
    pass


class InvalidPhoneFormatError(InvalidFormatError):
    pass


class InvalidDateFormatError(InvalidFormatError):
    pass


class InvalidSpecializationFormatError(InvalidFormatError):
    pass


# Исключения для проверки допустимых диапазонов и значений
class InvalidValueError(Exception):
    pass


class InvalidIdValueError(InvalidValueError):
    pass


class InvalidDateError(InvalidValueError):
    pass


class InvalidExperienceYearsError(InvalidValueError):
    pass


class InvalidQuantityError(InvalidValueError):
    pass


class InvalidDurationError(InvalidValueError):
    pass


class InvalidAccessLevelError(InvalidValueError):
    pass


# Исключения бизнес-логики и разграничения прав доступа
class BusinessLogicError(Exception):
    pass


class AccessDeniedError(BusinessLogicError):
    pass


class ScheduleConflictError(BusinessLogicError):
    pass