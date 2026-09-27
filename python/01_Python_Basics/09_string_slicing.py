a = "ABCDEF"
print(a[:3])
b = str(2)
print(type(b))
print(a[3:])
r = "asndHananket"
print(r[4:8])
print(r)
u = "Hello world"
print(u[1:4])
print(u[0:4])
avskye= "programming"
print(avskye[::2])
print(avskye[::3])
print(avskye[::-1])
print(avskye[-5:])
# : collon is used for slicing the string. It allows you to extract a portion of the string by specifying the start index, end index, and step size. The syntax for slicing is as follows:
# ==========================================================
# PYTHON SLICING - COMPLETE EXAMPLE
# String : "TAMILNADU"
# ==========================================================

# text = "TAMILNADU"

# # Index Positions
# #
# # Character :  T   A   M   I   L   N   A   D   U
# # Index     :  0   1   2   3   4   5   6   7   8
# #
# # Negative Index
# #
# # Character :  T   A   M   I   L   N   A   D   U
# # Index     : -9  -8  -7  -6  -5  -4  -3  -2  -1


# print("Original String :", text)
# print()


# # ==========================================================
# # 1. ACCESSING SINGLE CHARACTERS
# # ==========================================================

# print("text[0]  =", text[0])      # First Character
# print("text[1]  =", text[1])      # Second Character
# print("text[2]  =", text[2])      # Third Character
# print("text[3]  =", text[3])
# print("text[4]  =", text[4])
# print("text[5]  =", text[5])
# print("text[6]  =", text[6])
# print("text[7]  =", text[7])
# print("text[8]  =", text[8])

# print()


# # ==========================================================
# # 2. BASIC SLICING
# #
# # Syntax:
# # string[start : stop]
# #
# # start -> Included
# # stop  -> Excluded
# # ==========================================================

# print("text[0:3] =", text[0:3])   # T A M
# print("text[1:4] =", text[1:4])   # A M I
# print("text[2:5] =", text[2:5])   # M I L
# print("text[3:6] =", text[3:6])   # I L N
# print("text[4:7] =", text[4:7])   # L N A
# print("text[5:8] =", text[5:8])   # N A D
# print("text[6:9] =", text[6:9])   # A D U

# print()


# # ==========================================================
# # 3. START OMITTED
# #
# # Python starts from index 0
# # ==========================================================

# print("text[:1] =", text[:1])     # T
# print("text[:2] =", text[:2])     # TA
# print("text[:3] =", text[:3])     # TAM
# print("text[:4] =", text[:4])     # TAMI
# print("text[:5] =", text[:5])     # TAMIL
# print("text[:6] =", text[:6])     # TAMILN
# print("text[:7] =", text[:7])     # TAMILNA
# print("text[:8] =", text[:8])     # TAMILNAD
# print("text[:9] =", text[:9])     # TAMILNADU

# print()


# # ==========================================================
# # 4. STOP OMITTED
# #
# # Python goes till the end
# # ==========================================================

# print("text[0:] =", text[0:])     # TAMILNADU
# print("text[1:] =", text[1:])     # AMILNADU
# print("text[2:] =", text[2:])     # MILNADU
# print("text[3:] =", text[3:])     # ILNADU
# print("text[4:] =", text[4:])     # LNADU
# print("text[5:] =", text[5:])     # NADU
# print("text[6:] =", text[6:])     # ADU
# print("text[7:] =", text[7:])     # DU
# print("text[8:] =", text[8:])     # U

# print()


# # ==========================================================
# # 5. ENTIRE STRING
# # ==========================================================

# print("text[:] =", text[:])       # Complete String

# print()


# # ==========================================================
# # 6. STEP VALUE
# #
# # Syntax:
# # string[start : stop : step]
# # ==========================================================

# print("text[::1] =", text[::1])   # Every character
# print("text[::2] =", text[::2])   # Every 2nd character
# print("text[::3] =", text[::3])   # Every 3rd character
# print("text[::4] =", text[::4])   # Every 4th character

# print()


# # ==========================================================
# # 7. START + STOP + STEP
# # ==========================================================

# print("text[1:8:2] =", text[1:8:2])   # A I N D
# print("text[0:9:2] =", text[0:9:2])   # T M L A U
# print("text[2:9:2] =", text[2:9:2])   # M L A U
# print("text[0:9:3] =", text[0:9:3])   # T I A
# print("text[1:9:3] =", text[1:9:3])   # A L D

# print()


# # ==========================================================
# # 8. NEGATIVE INDEXING
# # ==========================================================

# print("text[-1] =", text[-1])     # U
# print("text[-2] =", text[-2])     # D
# print("text[-3] =", text[-3])     # A
# print("text[-4] =", text[-4])     # N
# print("text[-5] =", text[-5])     # L
# print("text[-6] =", text[-6])     # I
# print("text[-7] =", text[-7])     # M
# print("text[-8] =", text[-8])     # A
# print("text[-9] =", text[-9])     # T

# print()


# # ==========================================================
# # 9. NEGATIVE SLICING
# # ==========================================================

# print("text[-3:] =", text[-3:])       # ADU
# print("text[-5:] =", text[-5:])       # LNADU
# print("text[:-1] =", text[:-1])       # TAMILNAD
# print("text[:-2] =", text[:-2])       # TAMILNA
# print("text[-7:-2] =", text[-7:-2])   # MILNA

# print()


# # ==========================================================
# # 10. REVERSE STRING
# # ==========================================================

# print("text[::-1] =", text[::-1])     # Reverse String

# print()


# # ==========================================================
# # OUTPUT
# # ==========================================================
# #
# # Original String : TAMILNADU
# #
# # text[0]  = T
# # text[1]  = A
# # text[2]  = M
# # text[3]  = I
# # text[4]  = L
# # text[5]  = N
# # text[6]  = A
# # text[7]  = D
# # text[8]  = U
# #
# # text[0:3] = TAM
# # text[1:4] = AMI
# # text[2:5] = MIL
# # text[3:6] = ILN
# # text[4:7] = LNA
# # text[5:8] = NAD
# # text[6:9] = ADU
# #
# # text[:4] = TAMI
# # text[5:] = NADU
# # text[:]  = TAMILNADU
# #
# # text[::2] = TMLAU
# # text[::3] = TIA
# # text[1:8:2] = AIND
# #
# # text[-1] = U
# # text[-5] = L
# # text[-3:] = ADU
# # text[:-1] = TAMILNAD
# #
# # text[::-1] = UDANLIMAT
# #
# # ==========================================================
# # IMPORTANT NOTES
# # ==========================================================
# #
# # 1. Syntax:
# #       string[start : stop : step]
# #
# # 2. Start index is INCLUDED.
# #
# # 3. Stop index is EXCLUDED.
# #
# # 4. If start is omitted -> starts from index 0.
# #
# # 5. If stop is omitted -> goes till the end.
# #
# # 6. Step decides how many positions to jump.
# #
# # 7. Negative index starts counting from the end.
# #
# # 8. step = -1 reverses the string.
# #
# # 9. Remember:
# #
# #       0:3  -> 0,1,2
# #       NOT 0,1,2,3
# #
# # 10. Formula:
# #
# #       text[start:stop:step]
# #
# #       start ✔ Included
# #       stop  ❌ Excluded
# #       step  ➜ Jump size
# #
# # ==========================================================