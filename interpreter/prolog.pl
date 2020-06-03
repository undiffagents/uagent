appearsOn(D1,G) :- hasProperty(A,active),letter(D1),screen(G),task(A).
button(button).
hasProperty(target,correct).
hasProperty(distractor,incorrect).
hasProperty(A,active) :- isPartOf(I,A),subject(I),task(A).
hasProperty(S,unique) :- letter(S).
hasProperty(V,color) :- letter(V).
isPartOf(button,psychomotor-vigilance).
isPartOf(subject,psychomotor-vigilance).
isPartOf(screen,psychomotor-vigilance).
isPartOf(subject,psychomotor-vigilance).
letter(target).
press(I,C) :- appearsOn(F1,G),hasProperty(F1,correct),letter(F1),subject(I),button(C),screen(G).
subject(subject).
screen(screen).
task(psychomotor-vigilance).
target(distractor).

:- open("interpreter/reasonerFacts.txt",write, Stream),open("interpreter/groundRules.txt",write, Stream2),
forall((hasProperty(S,unique),letter(S)),(write(Stream2,letter(S)),write(Stream2," => "),write(Stream2,hasProperty(S,unique)),write(Stream2,"\n"),write(Stream,hasProperty(S,unique)),write(Stream,"\n"))),
forall((hasProperty(V,color),letter(V)),(write(Stream2,letter(V)),write(Stream2," => "),write(Stream2,hasProperty(V,color)),write(Stream2,"\n"),write(Stream,hasProperty(V,color)),write(Stream,"\n"))),
forall((hasProperty(A,active),isPartOf(I,A),subject(I),task(A)),(write(Stream2,isPartOf(I,A)),write(Stream2,","),write(Stream2,subject(I)),write(Stream2,","),write(Stream2,task(A)),write(Stream2," => "),write(Stream2,hasProperty(A,active)),write(Stream2,"\n"),write(Stream,hasProperty(A,active)),write(Stream,"\n"))),
forall((appearsOn(D1,G),hasProperty(A,active),letter(D1),screen(G),task(A)),(write(Stream2,hasProperty(A,active)),write(Stream2,","),write(Stream2,letter(D1)),write(Stream2,","),write(Stream2,screen(G)),write(Stream2,","),write(Stream2,task(A)),write(Stream2," => "),write(Stream2,appearsOn(D1,G)),write(Stream2,"\n"),write(Stream,appearsOn(D1,G)),write(Stream,"\n"))),
forall((press(I,C),appearsOn(F1,G),hasProperty(F1,correct),letter(F1),subject(I),button(C),screen(G)),(write(Stream2,appearsOn(F1,G)),write(Stream2,","),write(Stream2,hasProperty(F1,correct)),write(Stream2,","),write(Stream2,letter(F1)),write(Stream2,","),write(Stream2,subject(I)),write(Stream2,","),write(Stream2,button(C)),write(Stream2,","),write(Stream2,screen(G)),write(Stream2," => "),write(Stream2,press(I,C)),write(Stream2,"\n"),write(Stream,press(I,C)),write(Stream,"\n"))),
close(Stream),close(Stream2),halt.
