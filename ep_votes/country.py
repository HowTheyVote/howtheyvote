from enum import Enum, auto

COUNTRY_NAMES = {
    'Austria': 'AT',
    'Belgium': 'BE',
    'Bulgaria': 'BG',
    'Cyprus': 'CY',
    'Czech Republic': 'CZ',
    'Germany': 'DE',
    'Denmark': 'DK',
    'Estonia': 'EE',
    'Spain': 'ES',
    'Finland': 'FI',
    'France': 'FR',
    'United Kingdom': 'GB',
    'Greece': 'GR',
    'Croatia': 'CR',
    'Hungary': 'HU',
    'Ireland': 'IE',
    'Italy': 'IT',
    'Lithuania': 'LT',
    'Luxembourg': 'LU',
    'Latvia': 'LV',
    'Malta': 'MT',
    'Netherlands': 'NL',
    'Poland': 'PL',
    'Portugal': 'PT',
    'Romania': 'RO',
    'Sweden': 'SE',
    'Slovenia': 'SI',
    'Slovakia': 'SK',
}

class Country(Enum):
    AT = auto()
    BE = auto()
    BG = auto()
    CY = auto()
    CZ = auto()
    DE = auto()
    DK = auto()
    EE = auto()
    ES = auto()
    FI = auto()
    FR = auto()
    GB = auto()
    GR = auto()
    HR = auto()
    HU = auto()
    IE = auto()
    IT = auto()
    LT = auto()
    LU = auto()
    LV = auto()
    MT = auto()
    NL = auto()
    PL = auto()
    PT = auto()
    RO = auto()
    SE = auto()
    SI = auto()
    SK = auto()

    @staticmethod
    def from_str(name):
        return Country[COUNTRY_NAMES[name]]
