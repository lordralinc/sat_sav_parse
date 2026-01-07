import typing

from sat_sav_parse.models.object_reference import ObjectReference
from sat_sav_parse.models.properties.base import BaseProperty
from sat_sav_parse.models.properties.enums import PropertyTypeName

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer


__all__ = (
    "BoolProperty",
    "ByteProperty",
    "DoubleProperty",
    "EnumProperty",
    "FloatProperty",
    "Int8Property",
    "Int64Property",
    "IntProperty",
    "NameProperty",
    "ObjectProperty",
    "SoftObjectProperty",
    "StrProperty",
    "UInt32Property",
)


class BoolProperty(BaseProperty[bool]):
    type_name: typing.Literal[PropertyTypeName.BOOL] = PropertyTypeName.BOOL
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8_bool(self.payload)
        ser.add_u8(0)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        value = des.get_u8_bool()
        des.get_u8()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class ByteProperty(BaseProperty[int | str]):
    type_name: typing.Literal[PropertyTypeName.BYTE] = PropertyTypeName.BYTE
    index: int
    type: str

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_string(self.type)
        ser.add_u8(0)
        if isinstance(self.payload, str):
            ser.add_string(self.payload)
        else:
            ser.add_u8(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        _type = des.get_string()
        des.get_u8()
        value = des.get_u8() if _type == "None" else des.get_string()
        return cls(name=name, payload_size=payload_size, type=_type, index=index, payload=value)


class EnumProperty(BaseProperty[str]):
    type_name: typing.Literal[PropertyTypeName.ENUM] = PropertyTypeName.ENUM
    index: int
    type: str

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_string(self.type)
        ser.add_u8(0)
        ser.add_string(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        _type = des.get_string()
        des.get_u8()
        value = des.get_string()
        return cls(name=name, payload_size=payload_size, index=index, type=_type, payload=value)


class FloatProperty(BaseProperty[float]):
    type_name: typing.Literal[PropertyTypeName.FLOAT] = PropertyTypeName.FLOAT
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add_float(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get_float()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class DoubleProperty(BaseProperty[float]):
    type_name: typing.Literal[PropertyTypeName.DOUBLE] = PropertyTypeName.DOUBLE
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add_float(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get_double()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class IntProperty(BaseProperty[int]):
    type_name: typing.Literal[PropertyTypeName.INT] = PropertyTypeName.INT
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add_i32(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get_i32()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class Int8Property(BaseProperty[int]):
    type_name: typing.Literal[PropertyTypeName.INT8] = PropertyTypeName.INT8
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add_i8(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get_i8()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class UInt32Property(BaseProperty[int]):
    type_name: typing.Literal[PropertyTypeName.U_INT32] = PropertyTypeName.U_INT32
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add_u32(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get_u32()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class Int64Property(BaseProperty[int]):
    type_name: typing.Literal[PropertyTypeName.INT64] = PropertyTypeName.INT64
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add_i64(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get_i64()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class NameProperty(BaseProperty[str]):
    type_name: typing.Literal[PropertyTypeName.NAME] = PropertyTypeName.NAME
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add_string(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get_string()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class ObjectProperty(BaseProperty[ObjectReference]):
    type_name: typing.Literal[PropertyTypeName.OBJECT] = PropertyTypeName.OBJECT
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get(ObjectReference)
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class SoftObjectProperty(BaseProperty[tuple[ObjectReference, int]]):
    type_name: typing.Literal[PropertyTypeName.SOFT_OBJECT] = PropertyTypeName.SOFT_OBJECT
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add(self.payload[0])
        ser.add_u32(self.payload[1])

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = (des.get(ObjectReference), des.get_u32())
        return cls(name=name, payload_size=payload_size, index=index, payload=value)


class StrProperty(BaseProperty[str]):
    type_name: typing.Literal[PropertyTypeName.STR] = PropertyTypeName.STR
    index: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add(self.type_name)
        ser.add_u32(self.payload_size)
        ser.add_u32(self.index)
        ser.add_u8(0)
        ser.add_string(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()
        value = des.get_string()
        return cls(name=name, payload_size=payload_size, index=index, payload=value)
