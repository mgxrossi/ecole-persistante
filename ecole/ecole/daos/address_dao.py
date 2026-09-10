# -*- coding: utf-8 -*-

"""
Classe Dao[Address]
"""

from models.address import Address
from daos.dao import Dao
from dataclasses import dataclass
from typing import Optional


@dataclass
class AddressDao(Dao[Address]):


    def create(self, address : Address) -> int:
        #Crée en BD l'entité Address

        with Dao.connection.cursor() as cursor:
            #curseur c'est l'objet qui permet d'envoyer des commandes SQL
            #au serveur MySQL et d'en récupérer les résultats. Pensez-y comme
            #un stylo qui écrit/lit dans la base à travers la connexion déjà
            #ouverte (Dao.connection)
            #Le with garantit que le curseur se ferme automatiquement à la fin du bloc, même en cas d'erreur"""

            sql = "INSERT INTO address (street, city, postal_code) " \
                  "VALUES (%s, %s, %s)"
            #requête INSERT classique. Vous préparez votre phrase à l'avance, avec des trous →
            #"INSERT INTO address (...) VALUES (%s, %s, %s, %s)". Les %s sont des trous, comme dans
            #un texte à trous : "Je m'appelle ___ et j'ai ___ ans."
            #Vous donnez les mots à mettre dans les trous → (address.name, address.start_date, ...). Le premier mot va dans le premier trou, le deuxième mot dans le deuxième trou, etc.

            cursor.execute(sql, (address.street, address.city,
                                 address.postal_code))
            Dao.connection.commit()
            #sans commit(), l'insertion reste "en attente" côté serveur et ne sera jamais réellement enregistrée. C'est une sécurité de MySQL (le principe de transaction) : on peut faire plusieurs opérations liées, puis les valider (ou les annuler) toutes ensemble.
            #Vous écrivez vraiment → cursor.execute(...). Le stylo touche le papier

            address.id = cursor.lastrowid
            #Le carnet vous donne un numéro de ticket → chaque nouvelle ligne reçoit automatiquement un numéro (1, 2, 3...). Ce numéro, c'est cursor.lastrowid. On le garde précieusement
            # car c'est comme ça qu'on retrouvera cette ligne plus tard.
            #On le stocke dans address.id pour que l'objet Python sache désormais quel est son identifiant en base (utile ensuite pour faire un update ou delete sur ce même cours)

        return address.id
    #Conformément à ce que demande la documentation de la méthode (:return: l'id de l'entité insérée en BD)"""

    def read(self, id_address: int) -> Optional[Address]:
        """Renvoit le cours correspondant à l'entité dont l'id est id_address
           (ou None s'il n'a pu être trouvé)"""
        address: Optional[Address]

        with Dao.connection.cursor() as cursor:
            #ouvre un curseur pour exécuter du SQL sur la connexion partagée
            sql = "SELECT * FROM address WHERE id_address=%s"
            #%s : c'est un paramètre préparé — jamais on n'insère une valeur directement dans le texte SQL
           #On passe la valeur à part, dans un tuple (id_address,)

            cursor.execute(sql, (id_address,))
            record = cursor.fetchone()
            #cursor.fetchone() : récupère une ligne sous forme de dictionnaire
            #(record['name'], etc.) grâce à DictCursor configuré dans dao.py"""
        if record is not None:
            address = Address(record['street'], record['city'], record['postal_code'])
            address.id = record['id_address']
        else:
            address = None
            #Si rien trouvé → None. Sinon → on reconstruit un objet Python address"""

        return address

    def update(self, address: Address) -> bool:
        """Met à jour en BD l'entité address correspondant à address, pour y correspondre
        La méthode reçoit un objet address déjà modifié en Python (par exemple,
        on a changé address.name en mémoire), et renvoie True/False selon
        que la mise à jour a réussi.

        :param address: cours déjà mis à jour en mémoire
        !!Le rôle de update() n'est pas de modifier l'objet, mais de
        répercuter ces changements dans la base de données, qui elle
        contient encore les anciennes valeurs!!
        :return: True si la mise à jour a pu être réalisée
        """
        with Dao.connection.cursor() as cursor:
            #Comme toujours, on ouvre le curseur
            sql = "UPDATE address SET street=%s, city=%s, postal_code=%s " \
                  "WHERE id_address=%s"

            #C'est une requête UPDATE, avec deux parties bien distinctes :
            #SET ... : quelles colonnes on remplace, et par quoi (4 %s)
            #WHERE id_address=%s : sur quelle ligne précise on applique ce changement (1 %s de plus)

            cursor.execute(sql, (address.street, address.city,
                                 address.postal_code, address.id))

            #On fournit 5 valeurs pour les 5 %s, dans l'ordre exact où ils apparaissent
            #dans le texte SQL. Les 4 premières sont les nouvelles valeurs à
            #écrire, la 5ème (address.id) sert uniquement à identifier quelle ligne
            #modifier (celle du WHERE)

            Dao.connection.commit()
            #On valide définitivement le changement — sans ça, la modification
            #resterait invisible en base
            success = cursor.rowcount > 0

            #cursor.rowcount dit combien de lignes ont réellement été touchées par
            #le UPDATE. Si address.id correspondait à une addresse qui existe vraiment
            #en base, ce sera 1 → success = True. Sinon (id inexistant, ou déjà supprimé), ce sera 0 → success = False.

        return success
        #On renvoie ce booléen à qui a appelé la méthode

    def delete(self, address: Address) -> bool:
        #Ce qu'on reçoit : un objet Address qui existe déjà en base (il a forcément un id,
        # puisqu'on veut le supprimer). Ce qu'on renvoie : True/False, selon que la
        # suppression a réellement fonctionné

        with Dao.connection.cursor() as cursor:
            #On ouvre le "canal de communication" vers MySQL
            sql = "DELETE FROM address WHERE id_address=%s"
            #"Supprime la ligne de la table address, mais SEULEMENT celle dont id_address correspond exactement à la valeur qu'on va donner."

            cursor.execute(sql, (address.id,))
        #On donne une seule valeur pour l'unique %s : address.id. Remarquez la virgule dans (address.id,) — c'est le tuple à un seul élément
        #Ce qu'on utilise de address : uniquement son id. On se fiche complètement de street, city, postal_code ici — on ne fait que pointer vers la bonne ligne à effacer, pas la décrire

            Dao.connection.commit()
            #On valide la suppression"""

            success = cursor.rowcount > 0
            #Combien de lignes ont été supprimées ? Si address.id correspondait
            #à une addresse existante → 1 ligne supprimée → True. Sinon 0 → False.
        return success
