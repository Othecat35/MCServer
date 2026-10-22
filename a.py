from typing import (
    Literal,
    Optional,
    TypeAlias,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

# ---------- Define the same Literal three ways ----------
type EnvModern = Literal["a", "b", "c"]  # PEP 695 (what you use)
EnvClassic: TypeAlias = Literal["a", "b", "c"]  # 3.10 style
inline = Literal["a", "b", "c"]  # plain value, no alias


def show(label, fn):
    try:
        print(f"{label:48} → {fn()!r}")
    except Exception as e:
        print(f"{label:48} → {type(e).__name__}: {e}")


print("=== PEP 695 `type` alias ===")
print(f"type(EnvModern) = {type(EnvModern)}")
show("get_args(EnvModern)", lambda: get_args(EnvModern))
show("EnvModern.__value__", lambda: EnvModern.__value__)
show("get_args(EnvModern.__value__)", lambda: get_args(EnvModern.__value__))
show("EnvModern.__value__.__args__", lambda: EnvModern.__value__.__args__)
show("EnvModern.__args__", lambda: EnvModern.__args__)
show("get_origin(EnvModern)", lambda: get_origin(EnvModern))
show("get_origin(EnvModern.__value__)", lambda: get_origin(EnvModern.__value__))
show(
    "frozenset(get_args(EnvModern.__value__))",
    lambda: frozenset(get_args(EnvModern.__value__)),
)
show("EnvModern.__parameters__", lambda: EnvModern.__parameters__)

print("\n=== Traditional `TypeAlias` ===")
print(f"type(EnvClassic) = {type(EnvClassic)}")
show("get_args(EnvClassic)", lambda: get_args(EnvClassic))
show("EnvClassic.__args__", lambda: EnvClassic.__args__)
show("get_origin(EnvClassic)", lambda: get_origin(EnvClassic))

print("\n=== Inline `Literal` ===")
print(f"type(inline) = {type(inline)}")
show("get_args(inline)", lambda: get_args(inline))
show("inline.__args__", lambda: inline.__args__)

print("\n=== Union / Optional (matters for NotRequired[X | None]) ===")
show("get_args(EnvModern | None)", lambda: get_args(EnvModern | None))
show("get_args(Union[EnvModern, None])", lambda: get_args(Union[EnvModern, None]))
show("get_args(Optional[EnvModern])", lambda: get_args(Optional[EnvModern]))
show("get_args(Union[EnvClassic, None])", lambda: get_args(Union[EnvClassic, None]))

type A = Literal["x", "y"]
type B = Literal["z"]
show("get_args(A | B)", lambda: get_args(A | B))
show("get_args(Union[A, B])", lambda: get_args(Union[A, B]))

print("\n=== get_type_hints (indirect path) ===")


def f(x: EnvModern) -> None: ...


try:
    hints = get_type_hints(f)
    print(f"hints['x'] = {hints['x']!r}")
    show("get_args(hints['x'])", lambda: get_args(hints["x"]))
except Exception as e:
    print(f"get_type_hints failed: {type(e).__name__}: {e}")
