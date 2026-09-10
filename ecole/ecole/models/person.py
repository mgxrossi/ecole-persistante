# -*- coding: utf-8 -*-

"""
Classe abstraite Person, mère de Student et Teacher
"""

from abc import ABC
from dataclasses import dataclass, field

from .address import Address


@dataclass
class Person(ABC):
    """Personne liée à l'école : enseignant ou élève."""
    first_name: str
    last_name: str
    age: int
    address: Address | None = field(default=None, init=False)
    """init=False veut dire : cet attribut n'est PAS un paramètre du constructeur
    C'est un attribut qu'on doit remplir après coup, manuellement
    Pour que student.address (ou teacher.address) soit vraiment rempli avec un objet Address complet, il faudrait dans read() :
    Récupérer aussi id_address dans la requête SQL
    Si non NULL, appeler AddressDao().read(id_address) pour obtenir l'objet Address complet
    Assigner : student.address = cet_objet_address
    """

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.age} ans)" + \
               (f", {self.address}" if self.address is not None else '')
