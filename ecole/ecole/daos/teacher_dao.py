# -*- coding: utf-8 -*-

"""
Classe Dao[Teacher]
"""

from models.teacher import Teacher
from daos.dao import Dao
from dataclasses import dataclass
from typing import Optional
from daos.address_dao import AddressDao  # nouvel import pour recup l'adresse complete from AdressDao

@dataclass
class TeacherDao(Dao[Teacher]):
    def create(self, teacher: Teacher) -> int:
        """Crée en BD les entités Person et Teacher correspondant à teacher

        :param teacher: à créer sous forme d'entités Person + Teacher en BD
        :return: l'id de l'entité Teacher insérée en BD (0 si la création a échoué)
        """
        with Dao.connection.cursor() as cursor:
            # 1. on insère d'abord dans la table person (colonnes communes)
            sql_person = "INSERT INTO person (first_name, last_name, age) " \
                         "VALUES (%s, %s, %s)"
            cursor.execute(sql_person, (teacher.first_name, teacher.last_name, teacher.age))
            id_person = cursor.lastrowid

            # 2. puis dans teacher, en référençant l'id_person qu'on vient de créer
            sql_teacher = "INSERT INTO teacher (hiring_date, id_person) VALUES (%s, %s)"
            cursor.execute(sql_teacher, (teacher.hiring_date, id_person))
            teacher.id = cursor.lastrowid

            Dao.connection.commit()
        return teacher.id

    def read(self, id_teacher: int) -> Optional[Teacher]:
        """Renvoit l'enseignant correspondant à l'entité dont l'id est id_teacher
           (ou None s'il n'a pu être trouvé)"""
        teacher: Optional[Teacher]

        with Dao.connection.cursor() as cursor:
            sql = "SELECT teacher.id_teacher, teacher.hiring_date, " \
                  "       person.first_name, person.last_name, person.age, " \
                  "       person.id_address " \
                  "FROM teacher " \
                  "JOIN person ON teacher.id_person = person.id_person " \
                  "WHERE teacher.id_teacher = %s"
            cursor.execute(sql, (id_teacher,))
            record = cursor.fetchone()

        if record is not None:
            teacher = Teacher(record['first_name'], record['last_name'],
                               record['age'], record['hiring_date'])
            teacher.id = record['id_teacher']

            # si cette personne a une adresse enregistrée, on va la chercher
            if record['id_address'] is not None:
                """On vérifie d'abord que la personne a bien une adresse"""
                address_dao = AddressDao()
                """On crée une "instance" de AddressDao, l'outil qui sait lire la table address"""
                teacher.address = address_dao.read(record['id_address'])
                """On appelle read() sur AddressDao, avec l'id trouvé. Ça renvoie un véritable objet Address (rue, ville, code postal), qu'on accroche à teacher.address"""
        else:
            teacher = None

        return teacher

    def update(self, teacher: Teacher) -> bool:
        """Met à jour en BD les entités Person et Teacher correspondant à teacher

        :param teacher: enseignant déjà mis à jour en mémoire
        :return: True si la mise à jour a pu être réalisée
        """
        with Dao.connection.cursor() as cursor:
            sql_teacher = "UPDATE teacher SET hiring_date=%s WHERE id_teacher=%s"
            cursor.execute(sql_teacher, (teacher.hiring_date, teacher.id))

            sql_person = "UPDATE person SET first_name=%s, last_name=%s, age=%s " \
                         "WHERE id_person = (SELECT id_person FROM teacher WHERE id_teacher=%s)"
            cursor.execute(sql_person, (teacher.first_name, teacher.last_name,
                                         teacher.age, teacher.id))
            Dao.connection.commit()
            success = cursor.rowcount > 0
        return success

    def delete(self, teacher: Teacher) -> bool:
        """Supprime en BD les entités Teacher et Person correspondant à teacher

        :param teacher: enseignant dont les entités correspondantes sont à supprimer
        :return: True si la suppression a pu être réalisée
        """
        with Dao.connection.cursor() as cursor:
            sql = "SELECT id_person FROM teacher WHERE id_teacher=%s"
            cursor.execute(sql, (teacher.id,))
            record = cursor.fetchone()
            if record is None:
                return False
            id_person = record['id_person']

            cursor.execute("DELETE FROM teacher WHERE id_teacher=%s", (teacher.id,))
            cursor.execute("DELETE FROM person WHERE id_person=%s", (id_person,))
            Dao.connection.commit()
            success = cursor.rowcount > 0
        return success