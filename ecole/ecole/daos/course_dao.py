# -*- coding: utf-8 -*-

#Classe Dao[Course]
#on ouvre le curseur → on écrit une requête sécurisée avec des %s
#on l'exécute avec les vraies valeurs → on valide (commit)
#on récupère l'id auto-généré → on le renvoie.

from models.course import Course
from daos.dao import Dao
from dataclasses import dataclass
from typing import Optional
from daos.teacher_dao import TeacherDao


@dataclass
class CourseDao(Dao[Course]):

    """"""
    def create(self, course: Course) -> int:
        """Crée en BD l'entité Course correspondant au cours course

        :param course: à créer sous forme d'entité Course en BD
        :return: l'id de l'entité insérée en BD (0 si la création a échoué)
        """
        with Dao.connection.cursor() as cursor:
            #Un curseur, c'est l'objet qui permet d'envoyer des commandes SQL
            #au serveur MySQL et d'en récupérer les résultats. Pensez-y comme
            #un "stylo" qui écrit/lit dans la base à travers la connexion déjà
            #ouverte (Dao.connection)
            #Le with garantit que le curseur se ferme automatiquement à la fin du bloc, même en cas d'erreur"""

            sql = "INSERT INTO course (name, start_date, end_date, id_teacher) " \
                  "VALUES (%s, %s, %s, %s)"
            #requête INSERT classique. Vous préparez votre phrase à l'avance, avec des trous →
            #"INSERT INTO course (...) VALUES (%s, %s, %s, %s)". Les %s sont des trous, comme dans
            #un texte à trous : "Je m'appelle ___ et j'ai ___ ans."
            #Vous donnez les mots à mettre dans les trous → (course.name, course.start_date, ...). Le premier mot va dans le premier trou, le deuxième mot dans le deuxième trou, etc."""
            cursor.execute(sql, (course.name, course.start_date,
                                 course.end_date, course.teacher.id))
            Dao.connection.commit()
            #sans commit(), l'insertion reste "en attente" côté serveur et ne sera jamais réellement enregistrée. C'est une sécurité de MySQL (le principe de transaction) : on peut faire plusieurs opérations liées, puis les valider (ou les annuler) toutes ensemble.
            #Vous écrivez vraiment → cursor.execute(...). Le stylo touche le papier

            course.id = cursor.lastrowid

            #Le carnet vous donne un numéro de ticket → chaque nouvelle ligne reçoit automatiquement un numéro (1, 2, 3...). Ce numéro, c'est cursor.lastrowid. On le garde précieusement
            #car c'est comme ça qu'on retrouvera cette ligne plus tard.
            #On le stocke dans course.id pour que l'objet Python sache désormais quel est son identifiant en base (utile ensuite pour faire un update ou delete sur ce même cours)

        return course.id
    #Conformément à ce que demande la documentation de la méthode (:return: l'id de l'entité insérée en BD)"""

    def read(self, id_course: int) -> Optional[Course]:
        """Renvoit le cours correspondant à l'entité dont l'id est id_course
           (ou None s'il n'a pu être trouvé)"""
        course: Optional[Course]
        
        with Dao.connection.cursor() as cursor:
            #ouvre un curseur pour exécuter du SQL sur la connexion partagée"""
            sql = "SELECT * FROM course WHERE id_course=%s"
            #%s : c'est un paramètre préparé — jamais on n'insère une valeur directement dans le texte SQL
           #On passe la valeur à part, dans un tuple (id_course,)"""
            cursor.execute(sql, (id_course,))
            record = cursor.fetchone()
            #cursor.fetchone() : récupère une ligne sous forme de dictionnaire
            #(record['name'], etc.) grâce à DictCursor configuré dans dao.py"""
        if record is not None:
            course = Course(record['name'], record['start_date'], record['end_date'])
            course.id = record['id_course']

            # on fabrique une instance de TeacherDao
            teacher_dao = TeacherDao()
            # Comme le * sélectionne toutes les colonnes de la table course, id_teacher y est forcément présent — c'est juste un numéro (par exemple 2), pas un objet.
            # teacher_dao.read(...) : on appelle la méthode read() en lui donnant ce numéro.
            # Cette méthode va, en coulisses : Faire une requête SQL avec un JOIN entre teacher et perso et reconstruire un objet Teacher complet
            teacher = teacher_dao.read(record['id_teacher'])
            # teacher = ... : on range ce résultat dans une variable temporaire teacher — un objet Python complet et utilisable, pas juste un numéro
            course.set_teacher(teacher)
        # Cette méthode ne fait pas que remplir course.teacher — elle fait aussi le lien dans l'autre sens : elle ajoute ce cours à la liste teacher.courses_teached (les cours que cet enseignant donne). C'est ce qu'on appelle une relation bidirectionnelle

        else:
            course = None
            #Si rien trouvé → None. Sinon → on reconstruit un objet Python Course"""

        return course

    def update(self, course: Course) -> bool:
        """Met à jour en BD l'entité Course correspondant à course, pour y correspondre
        La méthode reçoit un objet Course déjà modifié en Python (par exemple,
        on a changé course.name en mémoire), et renvoie True/False selon
        que la mise à jour a réussi.

        :param course: cours déjà mis à jour en mémoire
        !!Le rôle de update() n'est pas de modifier l'objet, mais de
        répercuter ces changements dans la base de données, qui elle
        contient encore les anciennes valeurs!!
        :return: True si la mise à jour a pu être réalisée
        """
        with Dao.connection.cursor() as cursor:
            #Comme toujours, on ouvre le curseur"""
            sql = "UPDATE course SET name=%s, start_date=%s, end_date=%s, id_teacher=%s " \
                  "WHERE id_course=%s"

            #C'est une requête UPDATE, avec deux parties bien distinctes :
            #SET ... : quelles colonnes on remplace, et par quoi (4 %s)
            #WHERE id_course=%s : sur quelle ligne précise on applique ce changement (1 %s de plus)

            cursor.execute(sql, (course.name, course.start_date, course.end_date,
                                 course.teacher.id, course.id))

            #On fournit 5 valeurs pour les 5 %s, dans l'ordre exact où ils apparaissent
            #dans le texte SQL. Les 4 premières sont les nouvelles valeurs à
            #écrire, la 5ème (course.id) sert uniquement à identifier quelle ligne
            #modifier (celle du WHERE)

            Dao.connection.commit()
            #On valide définitivement le changement — sans ça, la modification
            #resterait invisible en base"""
            success = cursor.rowcount > 0

            #cursor.rowcount dit combien de lignes ont réellement été touchées par
           # le UPDATE. Si course.id correspondait à un cours qui existe vraiment
            #en base, ce sera 1 → success = True. Si course.id ne correspond à
            #aucune ligne (id inexistant, ou déjà supprimé), ce sera 0 → success = False.

        return success
        #On renvoie ce booléen à qui a appelé la méthode"""


    def delete(self, course: Course) -> bool:
        """Supprime en BD l'entité Course correspondant à course
        La méthode reçoit l'objet Course à supprimer,
        et renvoie True/False selon que la suppression a réussi.

        :param course: cours dont l'entité Course correspondante est à supprimer
        On ne se sert en réalité que d'une seule information de cet objet : son id
        """
        with Dao.connection.cursor() as cursor:
            sql = "DELETE FROM course WHERE id_course=%s"

            #C'est une requête DELETE, avec un seul %s : celui du WHERE.
            #Il n'y a pas de SET comme pour update(), puisqu'on ne
            #modifie aucune valeur — on supprime la ligne entière

            cursor.execute(sql, (course.id,))

            #On fournit une seule valeur : course.id. Remarquez la virgule après
            #course.id : (course.id,) est un tuple à un seul élément. Sans cette
            #virgule, (course.id) serait juste... course.id entre parenthèses,
            #pas un tuple — Python exige cette virgule pour bien indiquer "c'est
            #un tuple, même s'il n'a qu'un élément"

            Dao.connection.commit()
            #On valide la suppression"""
            success = cursor.rowcount > 0
            #Combien de lignes ont été supprimées ? Si course.id correspondait
            #à un cours existant → 1 ligne supprimée → True. Si course.id ne
            #correspond à rien (déjà supprimé, ou n'a jamais existé) → 0 → False."""
        return success

#definit une nouvelle methode
#read_all : le nom qu'on choisit pour cette méthode
#self désigne "l'instance actuelle de CourseDao" — c'est une convention obligatoire en Python pour toute méthode d'une classe. Pas de paramètre supplémentaire ici puisqu'on ne cible rien de précis, on veut tout
#ceci annonce le type de retour — ici, "une liste d'objets Course". C'est différent de read() qui renvoyait Optional[Course] (un seul objet, ou rien). Ici, c'est toujours une liste, potentiellement vide, jamais un seul objet isolé.
    def read_all(self) -> list[Course]:

 #On crée une liste vide, notre "panier"
        courses = []

 #on ouvre le curseur pour pouvoir envoyer des commandes SQL. Le with garantit sa fermeture automatique, même en cas d'erreur
        with Dao.connection.cursor() as cursor:

            #sélectionne toutes les colonnes" (id_course, name, start_date, end_date, id_teacher) — le * est un joker qui veut dire "tout"
            #FROM course : "dans la table course"
            sql = "SELECT * FROM course"

            #On exécute la requête. Un seul argument ici (sql), sans tuple de valeurs derrière, car il n'y a aucun %s à remplir dans le texte
            cursor.execute(sql)

            #"récupère tout") renvoie une liste de dictionnaires, un par ligne trouvée. Si la table course contient 8 cours, records sera une liste de 8 dictionnaires
            records = cursor.fetchall()

     #Pourquoi record au singulier ici, alors que records était au pluriel juste avant ? Parce qu'à l'intérieur de la boucle, on ne regarde qu'un seul élément à la fois
        for record in records:

            #On fabrique un véritable objet Python Course, en piochant les valeurs dans le dictionnaire record de cette ligne précise
            #On respecte scrupuleusement : le nom exact des clés ('name', 'start_date', 'end_date') — ce sont les vrais noms de colonnes SQL
            #et l'ordre exact du constructeur de Course, vu dans models/course.py
            course = Course(record['name'], record['start_date'], record['end_date'])
            course.id = record['id_course']
            #id a init=False dans models/course.py donc on ne peut pas le donner au constrcteur,
            #on doit l'assigner manuellement, juste après, pour que l'objet Python sache "quel numéro il porte" en base

            teacher_dao = TeacherDao()
            teacher = teacher_dao.read(record['id_teacher'])
            course.set_teacher(teacher)

            courses.append(course)
         #append ca veut dire ajoute a la fin l'objet course fraîchement construit dans notre "panier" courses
        #À la fin de la boucle, courses contiendra autant d'objets Course qu'il y avait de lignes dans records

        return courses
    #Une fois tous les tours de boucle terminés on renvoie le panier complet
    #liste prête à être utilisée ailleurs dans le programme (typiquement, dans School.init_from_db(), l'étape suivante)