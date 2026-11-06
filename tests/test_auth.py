from src.auth import _hash,verify
def test_password_hash_roundtrip():
    h=_hash('CorrectHorseBatteryStaple!'); assert verify('CorrectHorseBatteryStaple!',h); assert not verify('wrong',h)
