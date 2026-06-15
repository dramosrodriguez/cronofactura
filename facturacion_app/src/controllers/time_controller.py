from datetime import datetime
from src.models.time_log import TimeLog
from src.models.client import Client

class TimeController:
    """Controlador encargado de la lógica de negocio y validación de los Registros de Tiempo."""

    @staticmethod
    def create_log(client_id: int, date_str: str, hours: float, description: str, notes: str = None) -> TimeLog:
        """Registra un nuevo bloque de horas trabajadas para un cliente."""
        description = description.strip()
        notes = notes.strip() if notes else None

        if not client_id:
            raise ValueError("Debe seleccionar un cliente.")

        # Validar si el cliente realmente existe
        client = Client.get_by_id(client_id)
        if not client:
            raise ValueError("El cliente seleccionado no existe.")

        # Validar la fecha
        try:
            # Comprobar formato YYYY-MM-DD
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("El formato de fecha debe ser YYYY-MM-DD (Ej. 2026-06-14).")

        # Validar horas
        if hours <= 0:
            raise ValueError("El número de horas trabajadas debe ser mayor que 0.")

        if not description:
            raise ValueError("Debe proporcionar una descripción del trabajo realizado.")

        new_log = TimeLog(client_id=client_id, date=date_str, hours=hours, description=description, notes=notes)
        new_log.save()
        return new_log

    @staticmethod
    def delete_log(log_id: int) -> bool:
        """Elimina un registro de tiempo determinado."""
        log = TimeLog.get_all() # o directamente recuperar por id, pero como no añadimos get_by_id en TimeLog, podemos crear una instancia con el ID y llamarle delete
        # Creamos una instancia básica con el ID
        log_instance = TimeLog(client_id=0, date="", hours=1.0, description="", id=log_id)
        return log_instance.delete()

    @staticmethod
    def list_logs() -> list[dict]:
        """Obtiene una lista extendida de todos los registros de tiempo con datos del cliente."""
        return TimeLog.get_extended_logs()

    @staticmethod
    def get_unbilled_logs(client_id: int, start_date_str: str, end_date_str: str) -> list[TimeLog]:
        """Recupera los registros de tiempo pendientes de facturación de un cliente en un rango de fechas."""
        if not client_id:
            raise ValueError("Debe especificar un cliente.")

        # Validar fechas
        try:
            datetime.strptime(start_date_str, "%Y-%m-%d")
            datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("El formato de fecha debe ser YYYY-MM-DD.")

        if start_date_str > end_date_str:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

        return TimeLog.get_unbilled(client_id, start_date_str, end_date_str)
