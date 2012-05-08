# https://raw.github.com/asimihsan/crypto_example/master/src/utilities/crypto.py
# (https://github.com/asimihsan/crypto_example/blob/655694e0bea974813d2252a54e69478e272b1d1e/src/utilities/crypto.py)
# ---------------------------------------------------------------------------
# Copyright (c) 2012 Asim Ihsan (asim dot ihsan at gmail dot com)
# Distributed under the MIT/X11 software license, see the accompanying
# file license.txt or http://www.opensource.org/licenses/mit-license.php.
# ---------------------------------------------------------------------------

import os
import sys
import struct
import cStringIO as StringIO
import bz2

from Crypto.Cipher import AES
from Crypto.Hash import SHA256, HMAC
from Crypto.Protocol.KDF import PBKDF2

# ----------------------------------------------------------------------------
#   Constants.
# ----------------------------------------------------------------------------

# Length of salts in bytes.
salt_length_in_bytes = 16

# Hash function to use in general.
hash_function = SHA256

# PBKDF pseudo-random function. Used to mix a password and a salt.
# See Crypto\Protocol\KDF.py
pbkdf2_prf = lambda p, s: HMAC.new(p, s, hash_function).digest()

# PBKDF count, number of iterations.
pbkdf2_count = 1000

# PBKDF derived key length.
pbkdf2_dk_len = 32

# ----------------------------------------------------------------------------

class HMACIsNotValidException(Exception):
    pass

class InvalidFormatException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return repr(self.reason)

class CTRCounter:
    """ Callable class that returns an iterating counter for PyCrypto
    AES in CTR mode."""

    def __init__(self, nonce):
        """ Initialize the counter object.

        @nonce      An 8-byte binary string.
        """
        assert(len(nonce)==8)
        self.nonce = nonce
        self.cnt = 0

    def __call__(self):
        """ Return the next 16 byte counter, as a binary string. """
        right_half = struct.pack('>Q', self.cnt)
        self.cnt += 1
        return self.nonce + right_half

def encrypt_string(plaintext, key, compress=False):
    plaintext_obj = StringIO.StringIO(plaintext)
    ciphertext_obj = StringIO.StringIO()
    encrypt_file(plaintext_obj, key, ciphertext_obj, compress=compress)
    return ciphertext_obj.getvalue()

def decrypt_string(ciphertext, key):
    plaintext_obj = StringIO.StringIO()
    ciphertext_obj = StringIO.StringIO(ciphertext)
    decrypt_file(ciphertext_obj, key, plaintext_obj)
    return plaintext_obj.getvalue()

def decrypt_file(ciphertext_file_obj,
                 key,
                 plaintext_file_obj,
                 chunk_size=4096):
    # ------------------------------------------------------------------------
    #   Unpack the header values from the ciphertext.
    # ------------------------------------------------------------------------
    header_format = ">HHHHHQ?H"
    header_size = struct.calcsize(header_format)
    header_string = ciphertext_file_obj.read(header_size)
    try:
        header = struct.unpack(header_format, header_string)
    except struct.error:
        raise InvalidFormatException("Header is invalid.")
    pbkdf2_count = header[0]
    pbkdf2_dk_len = header[1]
    password_salt_size = header[2]
    nonce_size = header[3]
    hmac_salt_size = header[4]
    ciphertext_size = header[5]
    compress = header[6]
    hmac_size = header[7]

    # ------------------------------------------------------------------------
    #   Unpack everything except the ciphertext and HMAC, which are the
    #   last two strings in the ciphertext file.
    # ------------------------------------------------------------------------
    encrypted_string_format = ''.join([">",
                                       "%ss" % (password_salt_size, ) ,
                                       "%ss" % (nonce_size, ),
                                       "%ss" % (hmac_salt_size, )])
    encrypted_string_size = struct.calcsize(encrypted_string_format)
    body_string = ciphertext_file_obj.read(encrypted_string_size)
    try:
        body = struct.unpack(encrypted_string_format, body_string)
    except struct.error:
        raise InvalidFormatException("Start of body is invalid.")
    password_salt = body[0]
    nonce = body[1]
    hmac_salt = body[2]
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   Prepare the HMAC with everything except the ciphertext.
    #
    #   Notice we do not HMAC the ciphertext_size, just like the encrypt
    #   stage.
    # ------------------------------------------------------------------------
    hmac_password_derived = PBKDF2(password = key,
                                   salt = hmac_salt,
                                   dkLen = pbkdf2_dk_len,
                                   count = pbkdf2_count,
                                   prf = pbkdf2_prf)
    elems_to_hmac = [str(pbkdf2_count),
                     str(pbkdf2_dk_len),
                     str(len(password_salt)),
                     password_salt,
                     str(len(nonce)),
                     nonce,
                     str(len(hmac_salt)),
                     hmac_salt]
    hmac_object = HMAC.new(key = hmac_password_derived,
                           msg = ''.join(elems_to_hmac),
                           digestmod = hash_function)
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   First pass: stream in the ciphertext object into the HMAC object
    #   and verify that the HMAC is correct.
    #
    #   Notice we don't need to decompress anything here even if compression
    #   is in use. We're using Encrypt-Then-MAC.
    # ------------------------------------------------------------------------
    ciphertext_file_pos = ciphertext_file_obj.tell()
    ciphertext_bytes_read = 0
    while True:
        bytes_remaining = ciphertext_size - ciphertext_bytes_read
        current_chunk_size = min(bytes_remaining, chunk_size)
        ciphertext_chunk = ciphertext_file_obj.read(current_chunk_size)
        if ciphertext_chunk == '':
            break
        ciphertext_bytes_read += len(ciphertext_chunk)
        hmac_object.update(ciphertext_chunk)
    if ciphertext_bytes_read != ciphertext_size:
        raise InvalidFormatException("first pass ciphertext_bytes_read %s != ciphertext_size %s" % (ciphertext_bytes_read, ciphertext_size))

    # the rest of the file is the HMAC.
    hmac = ciphertext_file_obj.read()
    if len(hmac) != hmac_size:
        raise InvalidFormatException("len(hmac) %s != hmac_size %s" % (len(hmac), hmac_size))

    hmac_calculated = hmac_object.digest()
    if hmac != hmac_calculated:
        raise HMACIsNotValidException
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   Second pass: stream in the ciphertext object and decrypt it into the
    #   plaintext object.
    # ------------------------------------------------------------------------
    cipher_password_derived = PBKDF2(password = key,
                                     salt = password_salt,
                                     dkLen = pbkdf2_dk_len,
                                     count = pbkdf2_count,
                                     prf = pbkdf2_prf)
    cipher_ctr = AES.new(key = cipher_password_derived,
                         mode = AES.MODE_CTR,
                         counter = CTRCounter(nonce))
    ciphertext_file_obj.seek(ciphertext_file_pos, os.SEEK_SET)
    ciphertext_bytes_read = 0
    if compress:
        decompressor = bz2.BZ2Decompressor()
    while True:
        bytes_remaining = ciphertext_size - ciphertext_bytes_read
        current_chunk_size = min(bytes_remaining, chunk_size)
        ciphertext_chunk = ciphertext_file_obj.read(current_chunk_size)
        end_of_file = ciphertext_chunk == ''
        ciphertext_bytes_read += len(ciphertext_chunk)
        plaintext_chunk = cipher_ctr.decrypt(ciphertext_chunk)
        if compress:
            try:
                decompressed = decompressor.decompress(plaintext_chunk)
            except EOFError:
                decompressed = ""
            plaintext_chunk = decompressed
        plaintext_file_obj.write(plaintext_chunk)
        if end_of_file:
            break
    if ciphertext_bytes_read != ciphertext_size:
        raise InvalidFormatException("second pass ciphertext_bytes_read %s != ciphertext_size %s" % (ciphertext_bytes_read, ciphertext_size))
    # ------------------------------------------------------------------------

def encrypt_file(plaintext_file_obj,
                 key,
                 ciphertext_file_obj,
                 chunk_size = 4096,
                 compress = False):
    # ------------------------------------------------------------------------
    #   Prepare input key.
    # ------------------------------------------------------------------------
    password_salt = os.urandom(salt_length_in_bytes)
    cipher_password_derived = PBKDF2(password = key,
                                     salt = password_salt,
                                     dkLen = pbkdf2_dk_len,
                                     count = pbkdf2_count,
                                     prf = pbkdf2_prf)
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   Prepare cipher object.
    # ------------------------------------------------------------------------
    nonce_size = 8
    nonce = os.urandom(nonce_size)
    cipher_ctr = AES.new(key = cipher_password_derived,
                         mode = AES.MODE_CTR,
                         counter = CTRCounter(nonce))
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   Prepare HMAC object, and hash what we have so far.
    #
    #   Notice that we do not HMAC the size of the ciphertext. We don't
    #   know how big it'll be until we compress it, if we do, and we can't
    #   compress it without reading it into memory. So let the HMAC of
    #   the ciphertext itself do.
    # ------------------------------------------------------------------------
    hmac_salt = os.urandom(salt_length_in_bytes)
    hmac_password_derived = PBKDF2(password = key,
                                   salt = hmac_salt,
                                   dkLen = pbkdf2_dk_len,
                                   count = pbkdf2_count,
                                   prf = pbkdf2_prf)
    elems_to_hmac = [str(pbkdf2_count),
                     str(pbkdf2_dk_len),
                     str(len(password_salt)),
                     password_salt,
                     str(len(nonce)),
                     nonce,
                     str(len(hmac_salt)),
                     hmac_salt]
    hmac_object = HMAC.new(key = hmac_password_derived,
                           msg = ''.join(elems_to_hmac),
                           digestmod = hash_function)
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   Write in what we have so far into the output, ciphertext file.
    #
    #   Given that the plaintext may be compressed we don't know what
    #   it's final length will be without compressing it, and we can't
    #   do this without reading it all into memory. Hence let's
    #   put 0 as the ciphertext length for now and fill it in after.
    # ------------------------------------------------------------------------
    header_format = ''.join([">",
                             "H",                               # PBKDF2 count
                             "H",                               # PBKDF2 derived key length
                             "H",                               # Length of password salt
                             "H",                               # Length of CTR nonce
                             "H",                               # Length of HMAC salt
                             "Q",                               # Length of ciphertext
                             "?",                               # Is compression used?
                             "H",                               # Length of HMAC
                             "%ss" % (len(password_salt), ) ,   # Password salt
                             "%ss" % (nonce_size, ),            # CTR nonce
                             "%ss" % (len(hmac_salt), )])       # HMAC salt
    header = struct.pack(header_format,
                         pbkdf2_count,
                         pbkdf2_dk_len,
                         len(password_salt),
                         len(nonce),
                         len(hmac_salt),
                         0,                                     # This is the ciphertext size, wrong for now.
                         compress,
                         hmac_object.digest_size,
                         password_salt,
                         nonce,
                         hmac_salt)
    ciphertext_file_obj.write(header)
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   Stream in the input file and stream out ciphertext into the
    #   ciphertext file.
    # ------------------------------------------------------------------------
    ciphertext_size = 0
    if compress:
        compressor = bz2.BZ2Compressor()
    while True:
        plaintext_chunk = plaintext_file_obj.read(chunk_size)
        end_of_file = plaintext_chunk == ''
        if compress:
            if end_of_file:
                compressed = compressor.flush()
            else:
                compressed = compressor.compress(plaintext_chunk)
            plaintext_chunk = compressed
        ciphertext_chunk = cipher_ctr.encrypt(plaintext_chunk)
        ciphertext_size += len(ciphertext_chunk)
        ciphertext_file_obj.write(ciphertext_chunk)
        hmac_object.update(ciphertext_chunk)
        if end_of_file:
            break
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   Write the HMAC to the ciphertext file.
    # ------------------------------------------------------------------------
    hmac = hmac_object.digest()
    ciphertext_file_obj.write(hmac)
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    #   Go back to the header and update the ciphertext size.
    #
    #   Notice that we capture the header such that the last unpacked
    #   element of the struct is the unsigned long long of the ciphertext
    #   length.
    # ------------------------------------------------------------------------

    # Read in.
    ciphertext_file_obj.seek(0, os.SEEK_SET)
    header_format = ">HHHHHQ"
    header_size = struct.calcsize(header_format)
    header = ciphertext_file_obj.read(header_size)

    # Modify.
    header_elems = list(struct.unpack(header_format, header))
    header_elems[-1] = ciphertext_size

    # Write out.
    header = struct.pack(header_format, *header_elems)
    ciphertext_file_obj.seek(0, os.SEEK_SET)
    ciphertext_file_obj.write(header)
    # ------------------------------------------------------------------------