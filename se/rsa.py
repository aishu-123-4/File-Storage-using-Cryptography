from math import sqrt
import random
from random import randint as rand

def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a % b)


def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return -1


def miller_rabin_test(a, s, d, n):
	atop = pow(a, d, n)
	if atop == 1:
		return True
	for _ in range(s - 1):
		if atop == n - 1:
			return True
		atop = ( atop * atop ) % n
	return atop == n - 1

def miller_rabin(n, confidence):
	d = n - 1
	s = 0
	while d % 2 == 0:
		d >>= 1
		s += 1

	for _ in range(confidence):
		a = 0
		while a == 0:
			a = random.randrange(n)
		if not miller_rabin_test(a, s, d, n):
			return False
	return True


def isprime(n):
    if n < 2:
        return False
    elif n == 2:
        return True
    else:
        for i in range(2, int(sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
    return True

def generate_keypair(nbits):
    primality_confidence = 20
    while 1:
        p = random.getrandbits(nbits)
        if miller_rabin(p, primality_confidence): 
            break
    while 1:
        q = random.getrandbits(nbits)
        if miller_rabin(q, primality_confidence):
            break

    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randrange(1, phi)
    g = gcd(e, phi)

    while True:
        e = random.randrange(1, phi)
        g = gcd(e, phi)
        d = mod_inverse(e, phi)
        if g == 1 and e != d:
            break


    return ((e, n), (d, n))

def generate_keypair_old(p, q, keysize):

    nMin = 1 << (keysize - 1)
    nMax = (1 << keysize) - 1
    primes = [2]
    start = 1 << (keysize // 2 - 1)
    stop = 1 << (keysize // 2 + 1)

    if start >= stop:
        return []

    for i in range(3, stop + 1, 2):
        for p in primes:
            if i % p == 0:
                break
        else:
            primes.append(i)

    while (primes and primes[0] < start):
        del primes[0]

    
    while primes:
        p = random.choice(primes)
        primes.remove(p)
        q_values = [q for q in primes if nMin <= p * q <= nMax]
        if q_values:
            q = random.choice(q_values)
            break
    print(p, q)
    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randrange(1, phi)
    g = gcd(e, phi)

    while True:
        e = random.randrange(1, phi)
        g = gcd(e, phi)
        d = mod_inverse(e, phi)
        if g == 1 and e != d:
            break

    return ((e, n), (d, n))


def encrypt(msg_plaintext, package):
    e, n = package
    msg_ciphertext = [str(pow(c, e, n)) for c in msg_plaintext]
    cypher = ";;;".join(msg_ciphertext)
    data = cypher.encode('utf-8')
    return data

def decrypt(msg_ciphertext, package):
    msg_ciphertext = msg_ciphertext.decode('utf-8').split(";;;")
    d, n = package
    msg_plaintext = [chr(pow(int(c), d, n)) for c in msg_ciphertext]
    msg = ''.join(msg_plaintext)
    data = msg.encode('utf-8')
    return data