"""The keys, as :h shows them."""

HELP = """\
movement
  j k ↓ ↑          line down / up (takes a count)
  C-d C-u          half page down / up
  C-f C-b space    page down / up
  C-e C-y          scroll the view
  gg G             first / last line, or line N with a count
  H M L            top / middle / bottom of the view
  zz zt zb         cursor line to middle / top / bottom
  h l  0 $         scroll sideways, back to the start, to the end
  :N               line N of the new file

files and hunks
  C-j C-k  J K     next / previous page: a commit message, or a file
  } {  ]c [c       next / previous hunk
  ]] [[  > <       next / previous commit
  . ,              next / previous file, past commit messages
  za               fold the current file
  + -              more / less context, by a count or 3 lines
  =  F             default context, toggle the full file
  zM zR            fold / unfold every file

tree
  Tab  C-w w       switch between tree and diff
  C-w h  C-w l     focus the tree / the diff
  t                show or hide the tree
  j k              move, opening files as you go
  l h              expand / collapse a directory
  Enter o          open the file and focus the diff

review (git review)
  c                comment on the line, on the file from its header,
                   or reply in a thread
  C                comment on the whole commit
  x                resolve the thread, or open it again
  M-a              approve the file whose page this is, or on a message
                   page the commit, or take it back (Alt+a)
  M-r              request changes, the same way (Alt+r)
  ]n [n            next / previous open thread
  zu               hide / show resolved threads
  in the prompt    Enter saves, C-e goes on in $EDITOR, Esc drops it

mouse
  click            move the cursor, open a file, fold a directory
  double-click     comment, as c
  wheel            scroll the pane under the pointer
  shift-drag       select text, as without the viewer

other
  / ?  n N         search forward / backward, next / previous match
  e                open $EDITOR at the cursor line
  r                rerun git, and read the comments again
  :h :help         this list
  q ZZ :q          quit
"""
