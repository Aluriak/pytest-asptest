% INPUT
% empty test: no input, no output
% INSATISFIABLE

% INPUT
p(1).
% OUTPUT
q(1).

% INPUT
p(1..2).
% OUTPUT
q(1).  % Note that there is two answer set, one for each q/1.
% OUTPUT
q(2).  % Hence the two OUTPUT blocks

% INPUT
p(1).
% STRICT OUTPUT
p(1). q(1).  % there is exactly these atoms. No less, no more

% INPUT
-p(1).  % contradict the program itself
% INSATISFIABLE
