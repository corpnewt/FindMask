import binascii
from Scripts import utils

class Masks:
    def __init__(self, **kwargs):
        self.u  = utils.Utils("Find Mask")
        self.find = []

    def check_hex(self,text,error=False):
        try:
            if ":" in text:
                text = text.split(":")[1]
            if "//" in text:
                text = text.split("//")[0]
            return binascii.hexlify(binascii.unhexlify(text.replace(" ",""))).decode().upper()
        except Exception as e:
            if error:
                self.u.head("Hex Parsing Error")
                print("")
                print("Something went wrong parsing that hex data:")
                print("")
                print(" - Exception: {}".format(e))
                print("")
                self.u.grab("Press [enter] to return...")

    def main(self):
        while True:
            self.u.head("Find Mask")
            print("")
            print("Current Find Values:\n")
            if self.find:
                # Save a reference to the longest hex value to make sure we pad properly
                pad = max([len(hex(x)[2:]) for x in self.find])
                if pad % 2: pad += 1 # Ensure it's even as we're working with bytes
                # Walk the Find values and keep track of the XOR (exclusive or) between each element
                # in our list if the len is > 1
                bxor = 0
                xorl = []
                for i,x in enumerate(self.find,start=1):
                    h = hex(x)[2:].upper()
                    print(" {}. 0x{}".format(i,hex(x)[2:].upper().rjust(pad,"0")))
                    if len(self.find) > 1:
                        if bxor == 0:
                            bxor = x
                            continue # Skip the first as we're just setting the bxor value and have nothing to compare to
                        # Save the comparison to bitwise OR to keep track of changes
                        xorl.append(bxor ^ x)
                        bxor = x # Reset the bxor to the last seen value for the next comparison
                # Set bxor to the bitwise OR of all elements in our xorl list
                bxor = 0
                for x in xorl: bxor = bxor | x
                print("")
                # Save the number of bits we're adjusting and the number of total bits
                total_bits = int(pad/2*8)
                fuzzy_bits = "{0:b}".format(bxor).count("1")
                # Bitwise NOT the bxor value to invert the bits as masks are AND'd
                bnot = int("0x"+("F"*pad),16) - bxor # This is the mask
                # Bitwise AND the bnot with the first find value to get our final Find
                find = self.find[0] & bnot
                # Show the results
                print("Patch Values:\n\n Find: 0x{}".format(hex(find)[2:].upper().rjust(pad,"0")))
                print(" Mask: 0x{}".format(hex(bnot)[2:].upper().rjust(pad,"0")))
                print("\n {:,}/{:,} bits ignored".format(fuzzy_bits,total_bits))
            else:
                print(" - None.")
            print("")
            print("X. Clear All Find Values")
            print("Q. Quit")
            print("")
            print("Use r# to remove a specific Find value.  eg. r4 to remove the 4th.")
            print("")
            menu = self.u.grab("Please enter a new hexadecimal Find value:  ")
            if menu.lower() == "q": self.u.custom_quit()
            if menu.lower() == "x":
                self.find.clear()
                continue
            if menu.lower().startswith("r"):
                # Only removing a specific entry
                try:
                    r = int(menu[1:])-1
                    assert 0 <= r < len(self.find)
                    self.find.pop(r)
                except: pass
                continue
            # We should have a hex value to check here
            h = self.check_hex(menu,error=True)
            if not h: continue # Wasn't valid - try again
            # Got a valid value - let's add its int value to the find list
            hint = int(h,16)
            if not hint in self.find: # Only add if it isn't already in the list
                self.find.append(hint)

if __name__ == '__main__':
    if 2/3 == 0: input = raw_input
    m = Masks()
    m.main()
    '''while True:
        try:
            m.main()
        except Exception as e:
            print("An error occurred: {}".format(e))
            input("Press [enter] to continue...")'''
