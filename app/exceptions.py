"""Exceções de domínio da aplicação."""


class DoubleBookingError(Exception):
    """Lançada quando um médico ou paciente já tem um atendimento no horário."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(Exception):
    """Lançada quando uma entidade não é encontrada no banco de dados."""

    def __init__(self, entity: str, entity_id: int):
        self.entity = entity
        self.entity_id = entity_id
        self.message = f"{entity} com id {entity_id} não encontrado"
        super().__init__(self.message)
