from src.models.client import Client

class ClientController:
    """Controlador encargado de la lógica de negocio y validación para los Clientes."""

    @staticmethod
    def create_client(name: str, nif: str, hourly_rate: float, email: str, address: str) -> Client:
        """Crea y registra un nuevo cliente después de validar los campos."""
        # Limpieza básica
        name = name.strip()
        nif = nif.strip().upper()
        email = email.strip()
        address = address.strip()

        if not name:
            raise ValueError("El nombre del cliente es obligatorio.")

        if not nif:
            import time
            nif = f"PENDIENTE-{int(time.time() * 1000)}"

        if hourly_rate < 0:
            raise ValueError("La tarifa horaria no puede ser negativa.")

        # Validar si el NIF ya está en uso
        if Client.nif_exists(nif):
            raise ValueError(f"Ya existe un cliente registrado con el NIF/DNI {nif}.")

        new_client = Client(name=name, nif=nif, hourly_rate=hourly_rate, email=email, address=address)
        new_client.save()
        return new_client

    @staticmethod
    def update_client(client_id: int, name: str, nif: str, hourly_rate: float, email: str, address: str) -> bool:
        """Actualiza la información de un cliente existente."""
        name = name.strip()
        nif = nif.strip().upper()
        email = email.strip()
        address = address.strip()

        if not client_id:
            raise ValueError("ID de cliente no especificado.")

        if not name:
            raise ValueError("El nombre del cliente es obligatorio.")

        if not nif:
            client_prev = Client.get_by_id(client_id)
            if client_prev and client_prev.nif.startswith("PENDIENTE-"):
                nif = client_prev.nif
            else:
                import time
                nif = f"PENDIENTE-{int(time.time() * 1000)}"

        if hourly_rate < 0:
            raise ValueError("La tarifa horaria no puede ser negativa.")

        # Verificar si el NIF está duplicado con otro cliente
        if Client.nif_exists(nif, exclude_id=client_id):
            raise ValueError(f"El NIF/DNI {nif} ya está siendo utilizado por otro cliente.")

        client = Client.get_by_id(client_id)
        if not client:
            raise ValueError("Cliente no encontrado para actualizar.")

        client.name = name
        client.nif = nif
        client.hourly_rate = hourly_rate
        client.email = email
        client.address = address

        return client.update()

    @staticmethod
    def delete_client(client_id: int) -> bool:
        """Elimina un cliente de la base de datos."""
        client = Client.get_by_id(client_id)
        if not client:
            raise ValueError("Cliente no encontrado para eliminar.")
        
        # El método delete() lanzará un error si falla la integridad (por ejemplo, si tiene facturas asociadas)
        return client.delete()

    @staticmethod
    def get_client(client_id: int) -> Client:
        """Busca y retorna un cliente por su ID."""
        return Client.get_by_id(client_id)

    @staticmethod
    def list_clients() -> list[Client]:
        """Retorna todos los clientes registrados."""
        return Client.get_all()
