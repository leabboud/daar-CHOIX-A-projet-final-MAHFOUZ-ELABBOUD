from subprocess import call, run, check_output
c=run(["egrep", "-lr", "\"dar(tmouth|ling)\"", "Texts"],capture_output=True,text=True)
print(c.returncode)
