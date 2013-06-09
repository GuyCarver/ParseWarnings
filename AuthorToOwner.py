#----------------------------------------------------------------------
# Copyright (c) 2013, Guy Carver
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
#     * The name of Guy Carver may not be used to endorse or promote products # derived#
#       from # this software without specific prior written permission.#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# FILE    AuthorToOwner.py
# BY      Guy Carver
# DATE    06/01/2013 12:21 PM
#----------------------------------------------------------------------

import sublime, sublime_plugin
import collections, re, os
import time
from Edit.edit import Edit

OwnerReg = re.compile(".*[oO]{1}wner.*", re.IGNORECASE|re.DOTALL)
AuthorReg = re.compile("(.*)[aA]{1}uthor(.*)", re.IGNORECASE|re.DOTALL)
OwnerReplace = "\\1OWNER\\2"
AuthorCheckList = []

def AuthorToOwner( vw ) :
  r = vw.extract_scope(1)
  if r.empty() == False :
    hdr = vw.substr(r)
#    print("searching " + hdr)
    #Search for owner and if not found search for Author.
    if OwnerReg.match(hdr) == None :
      found = AuthorReg.match(hdr)
      #If Author found replace with OWNER
      if found != None :
#        print("Found author " + found.group(2))
        newhdr = AuthorReg.sub(OwnerReplace, hdr)
        with Edit(vw) as edit:
          edit.replace(r, newhdr)
#        vw.run_command('save')

class AuthorOwnerListener( sublime_plugin.EventListener ) :
  def on_load_async( self, aView ) :
    global AuthorCheckList
    # print("Checklist has " + str(len(AuthorCheckList)))
    for v in AuthorCheckList :
      if v.file_name() == aView.file_name() :
        AuthorCheckList.remove(v)
        # print("Processing loaded file" + aView.file_name())
        AuthorToOwner(aView)
        return

    #This does not work because the view objects do not match.
    # try:
    #   i = AuthorCheckList.index(aView)
    #   AuthorCheckList.remove(aView)
    #   print "Processing loaded file" + aView.file_name()
    #   AuthorToOwner(aView)
    # except:
    #   print "not in list"

class AuthorOwnerCommand( sublime_plugin.TextCommand ) :

  def run( self, edit ) :
    global AuthorCheckList
    vw = self.view
    w = vw.window()

    for s in vw.sel() :
      lines = vw.lines(s)

      for line in lines :
        e = vw.substr(line).strip()
        newVW = w.open_file(e)

        if newVW.is_loading() :
          AuthorCheckList.append(newVW)
        else:
          AuthorToOwner(newVW)
