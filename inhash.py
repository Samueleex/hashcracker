import hashlib

word = "EthicalHackingForum"

hash_md5 = hashlib.md5(word.encode()).hexdigest()
print("MD5:", hash_md5)

hash_sha1 = hashlib.sha1(word.encode()).hexdigest()
print("SHA-1:", hash_sha1)

hash_sha256 = hashlib.sha256(word.encode()).hexdigest()
print("SHA-256:", hash_sha256)
