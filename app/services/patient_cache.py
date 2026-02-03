from app.extensions import cache
from app.models.patient import Patient
from app.security.crypto import decrypt_value, safe_decrypt

@cache.memoize()
def get_patient_cache(patient_id):
    patient = Patient.query.get(patient_id)

    return {
        "patient_id": patient.patient_id,
        "profile_image": patient.profile_image,
        "firstname": decrypt_value(patient.firstname),
        "lastname": decrypt_value(patient.lastname),
        "email": decrypt_value(patient.email),
        "phone": decrypt_value(patient.phone),

        "full_name": " ".join(filter(None, [
            decrypt_value(patient.firstname),
            safe_decrypt(patient.middlename),
            decrypt_value(patient.lastname)
        ])),
        
        "profile_image": patient.profile_image,
    }

def clear_patient_cache(patient_id):
    cache.delete_memoized(get_patient_cache, patient_id)
