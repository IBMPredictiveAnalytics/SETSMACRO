#/***********************************************************************
# * Licensed Materials - Property of IBM 
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2014
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp. 
# ************************************************************************/

# version: 1.1.1
# author: JKP, IBM SPSS

# history
# 15-jul-2014 syntax control of name separator character

import random, codecs, textwrap
import spss
from spssaux import  _isseq, getSpssMajorVersion
from extension import Template, Syntax, processcmd

def SetMacroFromVariableSets(setnames=None, macroname=None, fail=False, outfile=None, sep=" "):
    """Define a macro consisting of all the variables in the specified variable sets.  Return set of variables.
    
    setnames is a string or sequence of variable set names to include.  These are not case sensitive.
    The union of the names will be returned in an arbitrary order.  If not specified, all sets are included
    macroname is the name to assign to the macro.  If not specified no macro is created.
    fail specifies whether or not to raise an exception if any set in the list is not found.
    By default, sets not found are ignored.
    sep is the separator string to use between variables
    if outfile is specified, the variable names are written to that file.  If a macroname is given,
    the names are written with the syntax that defines the macro.
    For version 16 or later, the file is utf-8.  For earlier versions it is written as plain text.
    
    The (Python) set of variables defined in the sets is returned."""
    
    if setnames is not None and not _isseq(setnames):
        setnames = setnames.split()
    randomtag = "_SS_" + str(random.randint(0,999999999))
    spss.CreateXPathDictionary(randomtag)
    variables = set()
    try:
        if setnames is None:
            setvars = spss.EvaluateXPath(randomtag, "/", """//variableSetVariable/@name""")
            if setvars == [] and fail:
                raise ValueError("No set variables found")
            else:
                variables = set(setvars)
        else:
            setnames = [n.lower() for n in setnames]   # requested names in lower case
            dssetnames = spss.EvaluateXPath(randomtag, "/", """//variableSet/@name""")   #available names, actual case
            dssetnamesdict = dict ([(n.lower(), n) for n in dssetnames])  # key is lowercase, value is actual case
            for name in setnames:
                # retrieve requested names by actual case
                setvars = spss.EvaluateXPath(randomtag, "/", 
                    """/dictionary/variableSet[@name="%s"]/variableSetVariable/@name""" % dssetnamesdict.get(name, ""))
                if setvars == [] and fail:
                    raise ValueError("Variable set name not found: %s" % name)
                variables.update(set(setvars))
    finally:
        spss.DeleteXPathHandle(randomtag)
        
    # separator must contain whitespace or textwrap will not work properly
    if not (" " in sep or "\t" in sep):
        sep = " " + sep + " "
    if not macroname is None:
        tw = textwrap.wrap(sep.join(variables), 80, break_long_words=False)
        spss.SetMacroValue(macroname, "\n".join(tw))
    if not outfile is None:
        if getSpssMajorVersion() >=16:   # write a utf-8 file
            f = codecs.open(outfile, "wb", encoding="utf_8_sig")
        else:
            f = open(outfile, "w")
        if not macroname is None:
            f.write("DEFINE %s ()\n" % macroname)
        tw = textwrap.wrap(sep.join(variables), 80, break_long_words=False)
        f.writelines([t + "\n" for t in tw])
        if not macroname is None:
            f.write("!ENDDEFINE.\n")
        f.close()

    return variables

helptext = r"""SETSMACRO [SETS=list of variable set names]
[MACRONAME=name] [FAIL={NO*|YES}] [SEPARATOR="string"]
[/SAVE OUTFILE=filespecification]
[/HELP].

Create macro variable for one or more variable sets.

SETS specifies a list of set names to retrieve.  The list is not case sensitive.
If it is omitted, all sets are retrieved.

MACRONAME optionally gives a name for a macro whose value will be all the variable names
in the sets retrieved.  Duplicate variables names are ignored.

SEPARATOR specifies the character(s) to be used between names
and defaults to a blank.

FAIL specifies whether to raise an error if any requested set is not found.  By default, no error
is raised.

OUTFILE can specify a filename to receive the list of variables found in the sets retrieved.
If MACRONAME is specified, it will contain the syntax for defining the macro.  Otherwise it
holds just the names.

/HELP prints this help and does nothing else.

"""

def Run(args):
        """Execute the SETSMACRO command"""

        args = args[args.keys()[0]]
        ###print args   #debug
        oobj = Syntax([
                Template("SETS", subc="",  ktype="literal", var="setnames", islist=True),
                Template("MACRONAME", subc="",  ktype="varname", var="macroname", islist=False),
                Template("SEPARATOR", subc="", ktype="literal", var="sep"),
                Template("FAIL", subc="",  ktype="bool", var="fail", islist=False),
                Template("OUTFILE", subc="SAVE",  ktype="literal", var="outfile", islist=False),
                Template("HELP", subc="", ktype="bool")])

        # A HELP subcommand overrides all else
        if args.has_key("HELP"):
            #print helptext
            helper()
        else:
                processcmd(oobj, args, SetMacroFromVariableSets)

def helper():
    """open html help in default browser window
    
    The location is computed from the current module name"""
    
    import webbrowser, os.path
    
    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "markdown.html"
    
    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print("Help file not found:" + helpspec)
try:    #override
    from extension import helper
except:
    pass