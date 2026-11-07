class InvalidFormatError(Exception): pass

class InvalidIdFormatError(InvalidFormatError): pass
class InvalidNameFormatError(InvalidFormatError): pass
class InvalidPhoneFormatError(InvalidFormatError): pass
class InvalidBirthDateFormatError(InvalidFormatError): pass

class InvalidValueError(Exception): pass

class InvalidIdValueError(InvalidValueError): pass
class InvalidBirthDateError(InvalidValueError): pass