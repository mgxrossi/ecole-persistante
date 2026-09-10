# -*- coding: utf-8 -*-

"""
Ça garantit une cohérence : n'importe qui lisant votre code sait,
rien qu'en voyant class CourseDao(Dao[Course]):, que cette classe aura
forcément les 4 méthodes create, read, update, delete, avec les bonnes
signatures. C'est un peu comme une checklist imposée — impossible
d'oublier une méthode par mégarde, Python vous le signalerait
immédiatement à l'exécution
Classe abstraite générique Dao[T], dont hérite les classes de DAO de chaque entité
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
#servent à créer une classe qu'on ne peut jamais utiliser directement, mais qui sert uniquement de modèle pour d'autres classes
from typing import ClassVar, Optional
import pymysql.cursors


@dataclass
class Dao[T](ABC):

    #la connexion partagée vers MySQL, ouverte une seule fois, utilisée par tous les DAO
    connection: ClassVar[pymysql.Connection] = \
        pymysql.connect(host='localhost',
                        user='ecole',
                        password='FqDEuKWd9TxLERZg6ooh',
                        database='ecole',
                        cursorclass=pymysql.cursors.DictCursor)

    @abstractmethod
    #@abstractmethod : ça déclare que toute classe qui hérite de Dao doit obligatoirement écrire sa propre version de create()

    def create(self, obj: T) -> int:
        """Crée l'entité en BD correspondant à l'objet obj

        :param obj: à créer sous forme d'entité en BD
        :return: l'id de l'entité insérée en BD (0 si la création a échoué)
        """
        ...
    # Dao ne sait pas comment créer un Course ou un Teacher, chaque sous-classe (CourseDao, TeacherDao...) doit fournir sa propre implémentation concrète

    @abstractmethod
    def read(self, id_entity: int) -> Optional[T]:
        """Renvoit l'objet correspondant à l'entité dont l'id est id_entity
           (ou None s'il n'a pu être trouvé)"""
        ...

    @abstractmethod
    def update(self, obj: T) -> bool:
        """Met à jour en BD l'entité correspondant à obj, pour y correspondre

        :param obj: objet déjà mis à jour en mémoire
        :return: True si la mise à jour a pu être réalisée
        """
        ...

    @abstractmethod
    def delete(self, obj: T) -> bool:
        """Supprime en BD l'entité correspondant à obj

        :param obj: objet dont l'entité correspondante est à supprimer
        :return: True si la suppression a pu être réalisée
        """
        ...
