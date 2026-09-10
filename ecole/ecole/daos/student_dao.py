# -*- coding: utf-8 -*-

"""
Classe Dao[Student]
"""

from models.student import Student
from daos.dao import Dao
from dataclasses import dataclass
from typing import Optional
from daos.address_dao import AddressDao


@dataclass
class StudentDao(Dao[Student]):
    def create(self, student: Student) -> int:
        """Crée en BD les entités Person et Student correspondant à student

        :param student: à créer sous forme d'entités Person + Student en BD
        :return: le n° étudiant inséré en BD (0 si la création a échoué)
        """
        with Dao.connection.cursor() as cursor:
            sql_person = ("INSERT INTO person (first_name, last_name, age) "
                          "VALUES (%s, %s, %s)")
            """il y a héritage, je dois insérer d'abord dans person (la table "mère")"""
            cursor.execute(sql_person, (student.first_name, student.last_name, student.age))
            """ici j'utilise exactement les noms d'attributs trouvés (first_name, last_name, age) 
            — c'est le lien direct entre le fichier modèle et ce code."""
            id_person = cursor.lastrowid
            """je récupère l'id auto-généré de person, pour pouvoir le réutiliser juste après"""

            sql_student = "INSERT INTO student (student_nbr, id_person) VALUES (%s, %s)"
            """j'insère ensuite dans student, avec student.student_nbr — celui déjà calculé automatiquement par __post_init__ au moment où l'objet Python a été créé"""
            cursor.execute(sql_student, (student.student_nbr, id_person))

            Dao.connection.commit()
            """je valide les 2 insertions ensemble"""
        return student.student_nbr
        """contrairement à Course/Teacher où on retourne un id auto-généré par MySQL, ici je retourne le numéro déjà connu côté Python"""


    def read(self, student_nbr: int) -> Optional[Student]:
        """Renvoit l'élève correspondant à l'entité dont le n° est student_nbr
           (ou None s'il n'a pu être trouvé)"""
        student: Optional[Student]

        with Dao.connection.cursor() as cursor:
            sql = "SELECT student.student_nbr, " \
                  "       person.first_name, person.last_name, person.age " \
                  "       person.id_address " \
                  "FROM student " \
                  "JOIN person ON student.id_person = person.id_person " \
                  "WHERE student.student_nbr = %s"
            """
            avec JOIN on rassemble les colonnes des deux tables en une seule ligne de résultat
            """
            cursor.execute(sql, (student_nbr,))
            record = cursor.fetchone()

        if record is not None:
            student = Student(record['first_name'], record['last_name'], record['age'])
            # je respecte exactement l'ordre du constructeur

            student.student_nbr = record['student_nbr']
            # on écrase le n° attribué automatiquement par __post_init__
            # avec le vrai n° stocké en base

            if record['id_address'] is not None:
                address_dao = AddressDao()
                student.address = address_dao.read(record['id_address'])

        else:
            student = None

        return student

    def update(self, student: Student) -> bool:
        """Met à jour en BD les entités Person et Student correspondant à student

        :param student: élève déjà mis à jour en mémoire
        :return: True si la mise à jour a pu être réalisée
        """
        with Dao.connection.cursor() as cursor:
            sql = "UPDATE person SET first_name=%s, last_name=%s, age=%s " \
                  "WHERE id_person = (SELECT id_person FROM student WHERE student_nbr=%s)"
            cursor.execute(sql, (student.first_name, student.last_name,
                                  student.age, student.student_nbr))
            Dao.connection.commit()
            success = cursor.rowcount > 0
        return success

    # attention toujours supprimer student avant person (jamais l'inverse, sinon erreur de clé étrangère #1451
    def delete(self, student: Student) -> bool:
        """Supprime en BD les entités Student et Person correspondant à student

        :param student: élève dont les entités correspondantes sont à supprimer
        :return: True si la suppression a pu être réalisée
        """
        with Dao.connection.cursor() as cursor:
            sql = "SELECT id_person FROM student WHERE student_nbr=%s"
            cursor.execute(sql, (student.student_nbr,))
            record = cursor.fetchone()
            if record is None:
                return False
            id_person = record['id_person']

            cursor.execute("DELETE FROM student WHERE student_nbr=%s", (student.student_nbr,))
            cursor.execute("DELETE FROM person WHERE id_person=%s", (id_person,))
            Dao.connection.commit()
            success = cursor.rowcount > 0
        return success

    def read_all(self) -> list[Student]:
        students = []
        with Dao.connection.cursor() as cursor:
            sql = "SELECT student.student_nbr, " \
                  "       person.first_name, person.last_name, person.age, " \
                  "       person.id_address " \
                  "FROM student " \
                  "JOIN person ON student.id_person = person.id_person"
            #Pourquoi c'est plus long ? Parce qu'on ne peut plus utiliser SELECT * bêtement
            # — on doit assembler des colonnes venant de deux tables différentes
            #teacher.id_teacher, teacher.hiring_date → viennent de la table teacher
            #person.first_name, person.last_name, person.age, person.id_address → viennent de la table person
            #pour chaque ligne de teacher, va chercher la ligne correspondante dans person (celle dont l'id coïncide), et fusionne les deux en une seule ligne de résultat."

            cursor.execute(sql)
            records = cursor.fetchall()
        for record in records:
            student = Student(record['first_name'], record['last_name'], record['age'])
            student.student_nbr = record['student_nbr']

            #même cascade qu'on avait déjà écrite dans TeacherDao.read()
            #record['id_address'] n'est qu'un numéro pas une adresse,
            #Si on veut que teacher.address contienne un vrai objet Address complet (rue, ville, code postal), il faut aller le chercher séparément, via AddressDao.
            if record['id_address'] is not None:
                #if car certain n ont pas d'addresse et comme ca ca plante pas si cest le cas
                address_dao = AddressDao()
                student.address = address_dao.read(record['id_address'])
            students.append(student)
        return students