"""Elf to Cypress bootable format"""
import os
import struct

import SCons.Util

INTVEC_AREA_SIZE = 0x100

I2CDEVSIZES = (0x100, 0x200, 0x400, 0x800, 0x1000, 0x2000, 0x4000, 0x4000)

def build_cyimg(target, source, env):
	hfi = open(SCons.Util.to_String(source[0]), "rb")
	ident, typ, mach, ver, entry, phoff, shoff, flags, ehsize, phentsize, phnum, shentsize, shnum, shstrndx = struct.unpack("<16sHHLLLLLHHHHHH", hfi.read(52))
	if ident[0:4]!="\x7FELF":
		print "Invalid ELF header"
		hfi.close()
		return 1
	if ident[4]!="\x01":
		print "Unknown ELF object type"
		hfi.close()
		return 1
	if not ident[5] in ("\x01", "\x02"):
		print "Invalid ELF endianness"
		hfi.close()
		return 1
	if ver!=1 or ident[6]!="\x01":
		print "Invalid ELF version"
		hfi.close()
		return 1
	if typ!=2:
		print "Not an executable ELF image"
		hfi.close()
		return 1
	if mach!=40:
		print "ELF machine type is not ARM"
		hfi.close()
		return 1

	i2cConf = env.get("CYI2CCONF", 0x1C)
	if not isinstance(i2cConf, (int, long)):
		hfi.close()
		print "CYI2CCONF must be a number"
		return 1
	i2cDevSize = I2CDEVSIZES[(i2cConf>>1) & 7]

	imgType = env.get("CYIMGTYPE", 0xB0)
	if not isinstance(imgType, (int, long)):
		hfi.close()
		print "CYIMGTYPE must be a number"
		return 1

	vecLoad = env.get("CYVECLOAD", False)
	if not isinstance(vecLoad, bool):
		hfi.close()
		print "CYVECLOAD must be boolean"
		return 1

	hfo = open(SCons.Util.to_String(target[0]), "wb")
	hfo.write("CY"+chr(i2cConf)+chr(imgType))

	checksum = 0
	for i in xrange(phnum):
		hfi.seek(phoff+i*phentsize)
		typ, offset, vaddr, paddr, filesize, memsize, flags, align = struct.unpack("<LLLLLLLL", hfi.read(32))
		if typ!=1: # PT_LOAD
			continue
		if (memsize & 3) or (filesize & 3):
			print "Warning: unaligned section size @%08X" % (vaddr)
		memSz = (memsize+3) // 4
		fileSz = (filesize+3) //4

		if not vecLoad and vaddr<INTVEC_AREA_SIZE:
			print "Note: removing %d bytes of intvec code. Use CYVECLOAD=True to retain this code" % (INTVEC_AREA_SIZE-vaddr)
			if fileSz <= ((INTVEC_AREA_SIZE-vaddr)//4):	# entire section is in INTVEC area, skip it
				continue
			else:
				offset += (INTVEC_AREA_SIZE-vaddr)
				memSz -= (INTVEC_AREA_SIZE-vaddr)//4
				fileSz -= (INTVEC_AREA_SIZE-vaddr)//4
				vaddr = INTVEC_AREA_SIZE

		hfi.seek(offset)
		while memSz:
			loadSz = min(memSz, i2cDevSize)
			memSz -= loadSz

			validSz = min(loadSz, fileSz)
			fileSz -= validSz

			hfo.write(struct.pack("<LL", loadSz, vaddr))
			vaddr += loadSz*4
			offset += loadSz*4

			while loadSz:
				readlen = min(validSz, 2048)
				writelen = min(loadSz, 2048)
				data = hfi.read(readlen*4)+"\x00\x00\x00\x00"*(2048-readlen)
				for j in xrange(readlen):
					checksum += struct.unpack("<L", data[j*4:j*4+4])[0]
				hfo.write(data[0:writelen*4])
				validSz -= min(writelen, readlen)
				loadSz -= writelen
	
	hfo.write(struct.pack("<LLL", 0, entry, checksum & 0xFFFFFFFF))
	hfo.close()
	hfi.close()
	return 0 # ok

def generate(env):
		 cyimg_builder = SCons.Builder.Builder(action=build_cyimg,
		 			suffix='.img',
		 			src_suffix='.elf')
		 env.Append(BUILDERS = {'CyImg' : cyimg_builder})

def exists(env):
	return True
