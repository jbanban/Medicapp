from app.extensions import cache
from app.models.doctor import Doctor
from app.security.crypto import decrypt_value

@cache.memoize()
def get_doctor_cache(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    return {
        "doctor_id": doctor.doctor_id,
        "firstname": decrypt_value(doctor.firstname),
        "lastname": decrypt_value(doctor.lastname),
        "email": decrypt_value(doctor.email),
        "specialization": doctor.specialization

        "full_name": " ".join(filter(None, [
            decrypt_value(doctor.firstname),
            safe_decrypt(doctor.middlename),
            decrypt_value(doctor.lastname)
        ])),
        
        "profile_image": doctor.profile_image,
    }

def clear_doctor_cache(doctor_id):
    cache.delete_memoized(get_doctor_public_profile, doctor_id)
