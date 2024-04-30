
from typing import List
import datetime
import json

from pydantic import BaseModel


class vname(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    honorifics: str


class tel(BaseModel):
    type: str  # work, home, cell, etc.
    num: str


class adr(BaseModel):
    type: str  # work, home, etc.
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class VCard2_1(BaseModel):
    formatted_name: str

    name: vname = vname(
        first_name="",
        middle_name="",
        last_name="",
        honorifics=""
    )

    org: str = ""
    title: str = ""
    role: str = ""
    logo: str = ""  # ignored by iphone

    photo: str = ""  # ignored by iphone

    tels: List[tel] = []
    adrs: List[adr] = []

    rev: str = ""
    email: str = ""
    note: str = ""

    # more esoteric fields
    bday: str = ""
    categories: str = ""
    geo: str = ""
    sound: str = ""
    key: str = ""
    tz: str = ""

    def update_rev(self):
        self.rev = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

    def __str__(self):
        return self.str()

    def str(self, iphone_compat=True):

        vcard_key_names = {
            "formatted_name": "FN",
            "org": "ORG",
            "title": "TITLE",
            "role": "ROLE",
            "logo": "LOGO",
            "photo": "PHOTO",
            "email": "EMAIL",
            "rev": "REV",
            "note": "NOTE",
            "bday": "BDAY",
            "categories": "CATEGORIES",
            "geo": "GEO",
            "sound": "SOUND",
            "key": "KEY",
            "tz": "TZ"
        }

        vc_str = f"BEGIN:VCARD\n  VERSION:2.1"
        for k, v in self.pruned_dump().items():
            if k == "adrs":
                for adr_v in v:
                    vc_str += f"""
        ADR;{adr_v['type']}:;;{adr_v['street']};{adr_v['city']};{adr_v['state']};{adr_v['zip_code']};{adr_v['country']}
        LABEL;{adr_v['type']};ENCODING#QUOTED-PRINTABLE;CHARSET#UTF-8:{adr_v['street']}#0D#
            #0A{adr_v['city']}\, {adr_v['state']} {adr_v['zip_code']}#0D#0A{adr_v['country']}"""
            elif k == "name":
                vc_str += f"\nN:{v['last_name']};{v['first_name']};{v['middle_name']};{v['honorifics']}"
            elif k == "tels":
                for tel_v in v:
                    vc_str += f"\nTEL;{tel_v['type'].upper()};VOICE:{tel_v['num']}"
            elif k == "photo":
                if v and not iphone_compat:
                    vc_str += f"\nPHOTO;JPEG:{v}"
            elif k in vcard_key_names:
                if v:
                    vc_str += f"\n{vcard_key_names[k]}:{v}"
            else:
                if v:
                    vc_str += f"\n{k}:{v}"
        vc_str += "\nEND:VCARD"
        return vc_str

    def pruned_dump(self):
        raw = self.model_dump()

        # order the dict keys
        order = [
            "formatted_name",
            "name",
            "org",
            "title",
            "email",
            "tels",
            "adrs",
            "role",
            "logo",
            "photo",
            "bday",
            "categories",
            "geo",
            "sound",
            "key",
            "rev",
            "tz",
            "note",
        ]
        ordered = {k: raw[k] for k in order if k in raw}
        pruned = {k: v for k, v in ordered.items() if v}
        return pruned


if __name__ == "__main__":

    # write the schema to file
    with open("vcard2.1_minimal_schema.json", "w") as f:
        json.dump(VCard2_1.model_json_schema(), f, indent=4)
