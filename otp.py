import random
def genotp():
    otp=''
    Caps=[chr(i) for i in range(ord('A'),ord('Z')+1)]
    sms=[chr(i) for i in range(ord('a'),ord('z')+1)]
    for i in  range(0,2):
        otp=otp+random.choice(Caps)  #otp='K'  #otp='K3i'+'M'
        otp=otp+str(random.randint(0,9)) #otp='K'+'3' #otp='K3'   'K3iM5'
        otp=otp+random.choice(sms)  #otp='K3'+'i'  #otp='K3i'  'K3iM5d'
    return otp
