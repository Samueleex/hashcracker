import json
import hashlib
import os
import sys
import time
import multiprocessing

class HashCracker:
    def __init__(self, wordlist_path=None, hashlist_path=None):
        self.start_time = time.time()
        self.wordlist_path = wordlist_path
        self.hashlist_path = hashlist_path
        self.unsolved_hashes = multiprocessing.Manager().list()
        self.unknown_hash_types = []
        self.sorted_hashes = { "md5": {"hashes": []}, "sha1": {"hashes": []}, "sha256": {"hashes": []} }

    def setup_paths(self):
        if self.wordlist_path is None or self.hashlist_path is None:
            config = self.load_config()
            self.wordlist_path = self.get_path_from_config(config, "wordlistpath")
            self.hashlist_path = self.get_path_from_config(config, "hashlistpath")

    def load_config(self):
        with open("config.json") as config_file:
            return json.load(config_file)

    def get_path_from_config(self, config, key):
        return config[key]

    def identify_hash_type(self, hsh):
        hash_types = {32: "md5", 40: "sha1", 64: "sha256"}
        return hash_types.get(len(hsh))

    def verify_file_locations(self):
        for file_path, file_type in ((self.wordlist_path, "wordlist"), (self.hashlist_path, "hashlist")):
            if not os.path.exists(file_path):
                print(f"ERROR: {file_type} not found at path '{file_path}'")
                sys.exit()

    def sort_hashes(self):
        for hsh in self.hashlist:
            hsh = hsh.strip()
            hash_type = self.identify_hash_type(hsh)
            if hash_type:
                self.sorted_hashes[hash_type]["hashes"].append(hsh)
            else:
                self.unknown_hash_types.append(hsh)
        print("Sorted hashes")

    def load_hashes(self):
        self.setup_paths()
        self.verify_file_locations()
        with open(self.hashlist_path) as f:
            self.hashlist = f.readlines()
        self.sort_hashes()
        print("Loaded hashes")

    def make_hash(self, word, algorithm):
        hash_function = getattr(hashlib, algorithm)
        return hash_function(word.encode("utf-8")).hexdigest()
    
    def crack_hashes(self, algorithm):
        hashlist = self.sorted_hashes[algorithm]["hashes"]
        start_time = self.start_time
        with open(self.wordlist_path, encoding="utf-8", errors="ignore") as wordlist:
            for word in wordlist:
                word = word.rstrip()
                current_hash = self.make_hash(word, algorithm)
                if current_hash in hashlist:
                    hashlist.remove(current_hash)
                    elapsed_time = round(time.time() - start_time, 2)
                    print(f"{current_hash[0:15]}... : {word} ({elapsed_time}s)")
                    if not hashlist:
                        break
        self.unsolved_hashes.extend(hashlist)

    def display_unknown_unsolved_hashes(self):
        if self.unsolved_hashes:
            print("\n--UNSOLVED HASHES--")
            for unsolved_hash in self.unsolved_hashes:
                print(unsolved_hash)
        if self.unknown_hash_types:
            print("\n--UNKNOWN HASH TYPES--")
            for unknown_hash in self.unknown_hash_types:
                print(unknown_hash) 

    def crack(self):
        hash_processes = []
        for algorithm in self.sorted_hashes:
            if self.sorted_hashes[algorithm]["hashes"]:
                hash_process = multiprocessing.Process(target=self.crack_hashes, args=(algorithm,))
                hash_processes.append(hash_process)

        for hash_process in hash_processes:
            hash_process.start()

        for hash_process in hash_processes:
            hash_process.join()

        self.display_unknown_unsolved_hashes()

if __name__ == "__main__":
    cracker = HashCracker()
    cracker.load_hashes()
    cracker.crack()

