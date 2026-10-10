from datetime import datetime
from decimal import Decimal, InvalidOperation

MAX_MONTO = Decimal("99999999.99")
CENTAVO = Decimal("0.01")


def validar_fecha(fecha: datetime | str, campo: str) -> datetime:
    if isinstance(fecha, str):
        try:
            fecha = datetime.fromisoformat(fecha)
        except ValueError as error:
            raise ValueError(f"La fecha {campo} no tiene un formato válido") from error

    if not isinstance(fecha, datetime):
        raise ValueError(f"La fecha {campo} no es válida")

    return fecha


def validar_monto(monto: Decimal | int | float | str, campo: str = "monto") -> Decimal:
    if isinstance(monto, bool):
        raise ValueError(f"El campo {campo} debe ser un monto mayor que cero con máximo dos decimales")

    try:
        valor = Decimal(str(monto))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"El campo {campo} debe ser un monto válido") from error

    if (
        not valor.is_finite()
        or valor <= 0
        or valor > MAX_MONTO
        or valor.quantize(CENTAVO) != valor
    ):
        raise ValueError(f"El campo {campo} debe ser un monto mayor que cero con máximo dos decimales")

    return valor


def validar_programacion(
    fecha_inicio: datetime | str,
    fecha_fin: datetime | str,
    precio_inicial: Decimal | int | float | str,
) -> tuple[datetime, datetime, Decimal]:
    inicio = validar_fecha(fecha_inicio, "fecha_inicio")
    fin = validar_fecha(fecha_fin, "fecha_fin")

    if inicio.tzinfo != fin.tzinfo:
        raise ValueError("Las fechas de inicio y fin deben usar la misma zona horaria")
    if inicio >= fin:
        raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")

    precio = validar_monto(precio_inicial, "precio_inicial")
    return inicio, fin, precio


def validar_fecha_inicio_no_pasada(fecha_inicio: datetime, ahora: datetime) -> None:
    if fecha_inicio.tzinfo != ahora.tzinfo:
        raise ValueError("La fecha de inicio y la hora actual deben usar la misma zona horaria")

    inicio_por_hora = fecha_inicio.replace(minute=0, second=0, microsecond=0)
    ahora_por_hora = ahora.replace(minute=0, second=0, microsecond=0)

    if inicio_por_hora < ahora_por_hora:
        raise ValueError("La fecha y hora de inicio no pueden ser anteriores a la hora actual")


def comparar_montos(monto_a: Decimal | int | float | str, monto_b: Decimal | int | float | str) -> int:
    valor_a = validar_monto(monto_a, "monto")
    valor_b = validar_monto(monto_b, "precio_inicial")
    return (valor_a > valor_b) - (valor_a < valor_b)
