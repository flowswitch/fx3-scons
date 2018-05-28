"""Sample script that builds the cyfxusbspigpiomode project (included in FX3 SDK)"""
env = FX3Env(CONFIG="release")

sources = ["cyfx_gcc_startup.S", "cyfxusbspigpiomode.c", "cyfxusbenumdscr.c", "cyfxtx.c"]
env.Program("test", sources) # build test.elf
env.CyImg("test", "test") # convert test.elf to test.img - same as elf2img
