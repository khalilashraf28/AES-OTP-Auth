# Cosine Similarity = (A.B) / (||A|| ||B||)


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
# is_verified = verify_password_similarity('asdfjaslkhasdfaslfhk', stored_hash)
# print(f"Password Similarity Verified: {is_verified}")


# import hashlib

# def hash_password(password):
#     """Hash the password using SHA-256"""
#     return hashlib.sha256(password.encode()).hexdigest()

# def verify_password_similarity(input_pwd, stored_hash):
#     """Verify password by comparing hashes directly"""
#     return hash_password(input_pwd) == stored_hash

# # Example usage
# stored_hash = hash_password('Ilovessuet')
# print(f"Hashed Password: {stored_hash}")

# is_valid = verify_password_similarity('Ilovessuet', stored_hash)
# print(f"Password Verification: {is_valid}")



import hashlib

def hash_password(password):
    """Turn a password into a SHA-256 hash (secret code)"""
    secret_code = hashlib.sha256(password.encode()).hexdigest()
    return secret_code

def verify_password_similarity(input_password, stored_hash, threshold=0.98):
    """Compare two passwords' hashes using cosine similarity (NOT secure for real use)"""
    # Step 1: Get the hash of the input password
    input_hash = hash_password(input_password)
    
    # Step 2: Turn both hashes into lists of numbers (like a picture of the code)
    vector1 = [ord(char) for char in input_hash[:64]]  # Numbers for input hash
    vector2 = [ord(char) for char in stored_hash[:64]]  # Numbers for stored hash
    
    # Step 3: Calculate dot product (how much the lists overlap)
    if len(vector1) != len(vector2):
        print("Error: Hashes are different lengths!")
        return False
    dot_product = 0
    for i in range(len(vector1)):
        dot_product += vector1[i] * vector2[i]  # Multiply and add
    
    # Step 4: Calculate magnitudes (sizes of the lists)
    mag1 = 0
    mag2 = 0
    for num in vector1:
        mag1 += num * num  # Square and add
    for num in vector2:
        mag2 += num * num  # Square and add
    mag1 = mag1 ** 0.5  # Square root
    mag2 = mag2 ** 0.5  # Square root
    
    # Step 5: Calculate cosine similarity
    if mag1 == 0 or mag2 == 0:
        print("Error: One of the lists is all zeros!")
        return False
    similarity = dot_product / (mag1 * mag2)
    
    # Step 6: Print result and check if similarity is above threshold
    print(f"Input Hash: {input_hash}")
    print(f"Stored Hash: {stored_hash}")
    print(f"Cosine Similarity: {similarity}")
    return similarity > threshold

# # Demo usage
# password1 = "Ilovessuet"
# password2 = "imrankhan"

# # Get the stored hash
# stored_hash = hash_password(password1)

# # Compare the passwords
# is_similar = verify_password_similarity(password2, stored_hash, threshold=0.98)
# print(f"Passwords are similar: {is_similar}")
