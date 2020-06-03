appearsOn(F1,G) :- hasProperty(A,active),letter(F1),screen(G),task(A).
button(button).
hasProperty(target,correct).
hasProperty(distractor,incorrect).
hasProperty(A,active) :- isPartOf(E,A),subject(E),task(A).
hasProperty(U,unique) :- letter(U).
hasProperty(X,color) :- letter(X).
isPartOf(button,visual-search).
isPartOf(subject,visual-search).
isPartOf(screen,visual-search).
letter(target).
press(E,C) :- appearsOn(H1,G),hasProperty(H1,correct),letter(H1),subject(E),button(C),screen(G).
something(target).
subject(subject).
screen(screen).
task(visual-search).
target(distractor).
target(distractor).

:- open("interpreter/reasonerFacts.txt",write, Stream),open("interpreter/groundRules.txt",write, Stream2),
forall((hasProperty(U,unique),letter(U)),(write(Stream2,letter(U)),write(Stream2," => "),write(Stream2,hasProperty(U,unique)),write(Stream2,"\n"),write(Stream,hasProperty(U,unique)),write(Stream,"\n"))),
forall((hasProperty(X,color),letter(X)),(write(Stream2,letter(X)),write(Stream2," => "),write(Stream2,hasProperty(X,color)),write(Stream2,"\n"),write(Stream,hasProperty(X,color)),write(Stream,"\n"))),
forall((hasProperty(A,active),isPartOf(E,A),subject(E),task(A)),(write(Stream2,isPartOf(E,A)),write(Stream2,","),write(Stream2,subject(E)),write(Stream2,","),write(Stream2,task(A)),write(Stream2," => "),write(Stream2,hasProperty(A,active)),write(Stream2,"\n"),write(Stream,hasProperty(A,active)),write(Stream,"\n"))),
forall((appearsOn(F1,G),hasProperty(A,active),letter(F1),screen(G),task(A)),(write(Stream2,hasProperty(A,active)),write(Stream2,","),write(Stream2,letter(F1)),write(Stream2,","),write(Stream2,screen(G)),write(Stream2,","),write(Stream2,task(A)),write(Stream2," => "),write(Stream2,appearsOn(F1,G)),write(Stream2,"\n"),write(Stream,appearsOn(F1,G)),write(Stream,"\n"))),
forall((press(E,C),appearsOn(H1,G),hasProperty(H1,correct),letter(H1),subject(E),button(C),screen(G)),(write(Stream2,appearsOn(H1,G)),write(Stream2,","),write(Stream2,hasProperty(H1,correct)),write(Stream2,","),write(Stream2,letter(H1)),write(Stream2,","),write(Stream2,subject(E)),write(Stream2,","),write(Stream2,button(C)),write(Stream2,","),write(Stream2,screen(G)),write(Stream2," => "),write(Stream2,press(E,C)),write(Stream2,"\n"),write(Stream,press(E,C)),write(Stream,"\n"))),
close(Stream),close(Stream2),halt.
