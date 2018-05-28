######## Cypress FX3 ############

FX3Root = "C:/Electro/USB/CyFX/EZ-USB FX3 SDK/1.3"	# FX3 SDK installation root path
FX3SdkVersion = "1_3_3"

FX3Prefix="arm-none-eabi-"
FX3ASFlags = ["-Wall", "-c", "-mcpu=arm926ej-s", "-mthumb-interwork"]
FX3CCFlags = ["-Wall", "-mcpu=arm926ej-s", "-mthumb-interwork", "-ffunction-sections", "-fdata-sections",
				"-g", "-DTX_ENABLE_EVENT_TRACE", "-DDEBUG", "-DCYU3P_FX3=1", "-D__CYU3P_TX__=1"]
FX3LDFlags = ["-d", "--gc-sections", "--no-wchar-size-warning", "--entry", "CyU3PFirmwareEntry"]
FX3IncPath = FX3Root+"/fw_lib/"+FX3SdkVersion+"/inc"
FX3LibPath = FX3Root+"/fw_lib/"+FX3SdkVersion+"/fx3_"
FX3GnuLibPath = [FX3Root+"/ARM GCC/arm-none-eabi/lib", FX3Root+"/ARM GCC/lib/gcc/arm-none-eabi/4.8.1"] # adjust version if differs
FX3Libs = ["cyu3sport", "cyu3lpp", "cyfxapi", "cyu3threadx", "c", "gcc"] # "c", "gcc" must be last ! gcc bug ?

def FX3Env(CONFIG="release", ASMFLAGS=[], CCFLAGS=[], LINKFLAGS=[], LDSCRIPT=FX3Root+"/fw_build/fx3_fw/fx3_512k.ld", ARFLAGS=[], LIBS=[], CPPPATH=[], LIBPATH=[]):
	env = Environment(ENV = os.environ, tools=["gas", "gcc", "g++", "gnulink", "cyimg"], 
		AS=FX3Prefix+"as", AR=FX3Prefix+"ar", CC=FX3Prefix+"gcc", CXX=FX3Prefix+"g++", 
		LINK=FX3Prefix+"ld", RANLIB=FX3Prefix+"ranlib", PROGSUFFIX=".elf",
		ASMFLAGS=FX3ASFlags+ASMFLAGS, CCFLAGS=FX3CCFlags+CCFLAGS, LINKFLAGS=FX3LDFlags+["-T", LDSCRIPT]+LINKFLAGS, ARFLAGS=ARFLAGS, 
		LIBS=FX3Libs+LIBS, CPPPATH=[FX3IncPath]+CPPPATH, LIBPATH=[FX3LibPath+CONFIG]+FX3GnuLibPath+LIBPATH)
	return env
