from models.address import Address
from daos.address_dao import AddressDao

def test_create_and_read_address():
    """Vérifie qu'un cours créé peut ensuite être relu avec les mêmes valeurs"""
    address_dao = AddressDao()

    new_address = Address("Rue de Sofia", "Nice", 6000)

    id_created = address_dao.create(new_address)
    assert id_created > 0  # un id valide a bien été renvoyé

    fetched_address = address_dao.read(id_created)
    assert fetched_address is not None
    assert fetched_address.city == "Nice"

    # nettoyage : on supprime le cours de test pour ne pas polluer la base
    address_dao.delete(fetched_address)


def test_update_address():
    """Vérifie qu'un cours mis à jour reflète bien le changement en base"""
    address_dao = AddressDao()

    address = Address("Rue de Sofia", "Nice", 6000)
    address_dao.create(address)

    address.city = "Toulouse"
    success = address_dao.update(address)
    assert success is True

    reloaded = address_dao.read(address.id)
    assert reloaded.city == "Toulouse"

    address_dao.delete(address)  # nettoyage


def test_delete_address():
    address_dao = AddressDao()

    address = Address("Rue à supprimer", "Nice", 6000)
    address_dao.create(address)

    success = address_dao.delete(address)
    assert success is True

    reloaded = address_dao.read(address.id)
    assert reloaded is None


def test_read_nonexistent_address():
    address_dao = AddressDao()
    result = address_dao.read(999999)
    assert result is None