# -*- coding: utf-8 -*-

"""
Tests de CourseDao
On teste sur une vraie base : ici, chaque test crée ses propres données, puis les supprime à la
fin (course_dao.delete(...)). C'est essentiel pour ne pas polluer votre base ecole avec des
faux cours à chaque exécution.
assert : c'est le cœur de tout test. assert condition ne fait rien si c'est vrai, et fait
échouer le test si c'est faux.
Un test par comportement : un test vérifie une seule chose à la fois (test_create_and_read_course,
test_update_course...), pas tout en même temps — ça facilite le diagnostic quand un test échoue.
teacher_dao.read(1) suppose qu'un enseignant avec l'id 1 existe déjà dans votre base (regardez
votre ecole.sql : oui, id_teacher=1 existe). Adaptez si besoin.
"""

from datetime import date
from models.course import Course
from models.teacher import Teacher
from daos.course_dao import CourseDao
from daos.teacher_dao import TeacherDao


def test_create_and_read_course():
    """Vérifie qu'un cours créé peut ensuite être relu avec les mêmes valeurs"""
    course_dao = CourseDao()

    # on récupère un enseignant déjà existant en base pour l'associer au cours
    teacher_dao = TeacherDao()
    teacher = teacher_dao.read(1)  # suppose qu'un enseignant d'id 1 existe

    new_course = Course("Test Pytest", date(2026, 1, 1), date(2026, 2, 1))
    new_course.set_teacher(teacher)

    id_created = course_dao.create(new_course)
    assert id_created > 0  # un id valide a bien été renvoyé

    fetched_course = course_dao.read(id_created)
    assert fetched_course is not None
    assert fetched_course.name == "Test Pytest"

    # nettoyage : on supprime le cours de test pour ne pas polluer la base
    course_dao.delete(fetched_course)


def test_update_course():
    """Vérifie qu'un cours mis à jour reflète bien le changement en base"""
    course_dao = CourseDao()
    teacher_dao = TeacherDao()
    teacher = teacher_dao.read(1)

    course = Course("Avant modif", date(2026, 1, 1), date(2026, 2, 1))
    course.set_teacher(teacher)
    course_dao.create(course)

    course.name = "Après modif"
    success = course_dao.update(course)
    assert success is True

    reloaded = course_dao.read(course.id)
    assert reloaded.name == "Après modif"

    course_dao.delete(course)  # nettoyage


def test_delete_course():
    """Vérifie qu'un cours supprimé n'est plus lisible ensuite"""
    course_dao = CourseDao()
    teacher_dao = TeacherDao()
    teacher = teacher_dao.read(1)

    course = Course("À supprimer", date(2026, 1, 1), date(2026, 2, 1))
    course.set_teacher(teacher)
    course_dao.create(course)

    success = course_dao.delete(course)
    assert success is True

    reloaded = course_dao.read(course.id)
    assert reloaded is None


def test_read_nonexistent_course():
    """Vérifie qu'un id inexistant renvoie bien None"""
    course_dao = CourseDao()
    result = course_dao.read(999999)
    assert result is None