# import hashlib
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity

# def hash_password(password):
#     """Hash the password using SHA-256"""
#     return hashlib.sha256(password.encode()).hexdigest()

# def hash_to_vector(h):
#     """Convert hash string to numerical vector (ASCII values of characters)"""
#     return np.array([ord(c) for c in h.ljust(64, '0')[:64]])

# def verify_password_similarity(input_pwd, stored_hash, threshold=0.9):
#     """Compare SHA-256 hashes using cosine similarity (NOT secure for real use)"""
#     input_hash = hash_password(input_pwd)
#     vec1 = hash_to_vector(input_hash).reshape(1, -1)
#     vec2 = hash_to_vector(stored_hash).reshape(1, -1)
#     similarity = cosine_similarity(vec1, vec2)[0][0]
#     print(f"Cosine Similarity: {similarity}")
#     return similarity > threshold

# # Demo usage
# stored_hash = hash_password('Ilovessuet')
# print(f"Stored Hash: {stored_hash}")

# # Try with similar or different input
# is_verified = verify_password_similarity('imrankhan', stored_hash)
# print(f"Password Similarity Verified: {is_verified}")


import hashlib

def hash_password(password):
    """Hash the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password_similarity(input_pwd, stored_hash):
    """Verify password by comparing hashes directly"""
    return hash_password(input_pwd) == stored_hash

# # Example usage
# stored_hash = hash_password('Ilovessuet')
# print(f"Hashed Password: {stored_hash}")

# is_valid = verify_password_similarity('Ilovessuet', stored_hash)
# print(f"Password Verification: {is_valid}")
