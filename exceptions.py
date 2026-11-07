class InvalidFormatError(Exception): pass

class InvalidIdFormatError(InvalidFormatError): pass
class InvalidNameFormatError(InvalidFormatError): pass
class InvalidPhoneFormatError(InvalidFormatError): pass
class InvalidDateFormatError(InvalidFormatError): pass
class InvalidSpecializationFormatError(InvalidFormatError): pass

class InvalidValueError(Exception): pass

class InvalidIdValueError(InvalidValueError): pass
class InvalidDateError(InvalidValueError): pass
class InvalidExperienceYearsError(InvalidValueError): pass