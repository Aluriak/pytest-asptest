ext(O):- rel(O,_) ; rel(O,A): int(A).
int(A):- rel(_,A) ; rel(O,A): ext(O).
