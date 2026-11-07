#Ошибки синтаксиса и формата
class InvalidFormatError(Exception): pass

class InvalidNameFormatError(InvalidFormatError): pass
class InvalidPhoneFormatError(InvalidFormatError): pass
class InvalidDateFormatError(InvalidFormatError): pass
class InvalidSpecializationFormatError(InvalidFormatError): pass

# Ошибки логики и недопустимых значений
class InvalidValueError(Exception): pass

class InvalidIdValueError(InvalidValueError): pass
class InvalidDateError(InvalidValueError): pass
class InvalidExperienceYearsError(InvalidValueError): pass
class InvalidQuantityError(InvalidValueError): pass
class InvalidDurationError(InvalidValueError): pass
class InvalidAccessLevelError(InvalidValueError): pass