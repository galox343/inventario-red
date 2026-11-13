from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

app = FastAPI(title="Inventario de red")


class Dispositivo(BaseModel):
    nombre: str
    tipo: str
    ip: str
    activo: bool = True


class DispositivoActualizar(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
    ip: str | None = None
    activo: bool | None = None


inventario = [
    Dispositivo(nombre="R1", tipo="router", ip="10.0.0.1"),
    Dispositivo(nombre="SW1", tipo="switch", ip="10.0.0.10", activo=False),
    Dispositivo(nombre="FW1", tipo="firewall", ip="10.0.0.254"),
]


@app.get("/")
async def estado():
    return {"servicio": "Inventario de red", "total": len(inventario)}


@app.get("/dispositivos")
async def listar(activo: bool | None = None):
    if activo is None:
        return inventario
    return [equipo for equipo in inventario if equipo.activo == activo]


@app.get("/dispositivos/{nombre}")
async def obtener(nombre: str):
    for equipo in inventario:
        if equipo.nombre.upper() == nombre.upper():
            return equipo
    raise HTTPException(status_code=404, detail=f"No existe el equipo {nombre}")


@app.post("/dispositivos", status_code=201)
async def crear(dispositivo: Dispositivo):
    for equipo in inventario:
        if equipo.nombre.upper() == dispositivo.nombre.upper():
            raise HTTPException(
                status_code=409,
                detail="El dispositivo ya existe"
            )

    inventario.append(dispositivo)
    return dispositivo


@app.put("/dispositivos/{nombre}")
async def reemplazar(nombre: str, datos: Dispositivo):
    equipo = None
    for dispositivo in inventario:
        if dispositivo.nombre.upper() == nombre.upper():
            equipo = dispositivo
            break

    if equipo is None:
        raise HTTPException(status_code=404, detail=f"No existe el equipo {nombre}")

    equipo.nombre = datos.nombre
    equipo.tipo = datos.tipo
    equipo.ip = datos.ip
    equipo.activo = datos.activo
    return equipo


@app.patch("/dispositivos/{nombre}")
async def modificar(nombre: str, datos: DispositivoActualizar):
    equipo = None
    for dispositivo in inventario:
        if dispositivo.nombre.upper() == nombre.upper():
            equipo = dispositivo
            break

    if equipo is None:
        raise HTTPException(status_code=404, detail=f"No existe el equipo {nombre}")

    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(equipo, campo, valor)

    return equipo


@app.delete("/dispositivos/{nombre}", status_code=204)
async def eliminar(nombre: str):
    for i, equipo in enumerate(inventario):
        if equipo.nombre.upper() == nombre.upper():
            inventario.pop(i)
            return Response(status_code=204)

    raise HTTPException(
        status_code=404,
        detail=f"No existe el equipo {nombre}"
    )

