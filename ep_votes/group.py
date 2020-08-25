from enum import Enum, auto

GROUP_NAMES = {
    "Group of the European People's Party (Christian Democrats)": "EPP",
    "Non-attached Members": "NI",
    "Identity and Democracy Group": "ID",
    "Group of the Progressive Alliance of Socialists and Democrats in the European Parliament": "SD",  # noqa: E501
    "European Conservatives and Reformists Group": "ECR",
    "Group of the Greens/European Free Alliance": "GREENS",
    "Renew Europe Group": "RENEW",
    "Group of the European United Left - Nordic Green Left": "GUE",
}


class Group(Enum):
    EPP = auto()
    SD = auto()
    GREENS = auto()
    RENEW = auto()
    GUE = auto()
    ECR = auto()
    ID = auto()
    NI = auto()

    @staticmethod
    def from_str(name):
        return Group[GROUP_NAMES[name]]
