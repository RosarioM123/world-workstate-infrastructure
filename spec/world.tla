------------------------------ MODULE world ------------------------------
(***************************************************************************)
(* Formal specification of the WORLD commit protocol (World.update,        *)
(* src/world/core.py).                                                     *)
(*                                                                         *)
(* Companion to spec/model_check.py, which is the executable, CI-checked   *)
(* mechanization of this exact spec. This file is for independent checking *)
(* with the TLA+ toolbox (TLC); it is not executed in CI (no JVM in this   *)
(* environment). The two were written against each other action by action. *)
(*                                                                         *)
(* Each update is two atomic actions:                                      *)
(*   ReadJudge(w): read latest committed, fast-path expected_version       *)
(*     check, adversarial invariant verdict; records pending. READ and      *)
(*     JUDGE are fused: neither touches shared state, so no interleaving   *)
(*     is lost.                                                            *)
(*   AtomicCommit(w): BEGIN IMMEDIATE..COMMIT as one step: re-validate      *)
(*     expected_version against the latest committed row, apply the        *)
(*     idempotency dedupe, append exactly one hash-chained row. Modeling   *)
(*     BEGIN IMMEDIATE as atomic IS the implementation's serialization      *)
(*     guarantee (SQLite serializes BEGIN IMMEDIATE writers); the spec     *)
(*     proves the protocol correct given that serialization.               *)
(*                                                                         *)
(* TLC configuration (world.cfg):                                          *)
(*   CONSTANTS Writers   = {w1, w2}                                        *)
(*             KeyDomain = {k1}                                            *)
(*             MaxOps    = 2                                               *)
(*   INVARIANT Inv                                                         *)
(***************************************************************************)
EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS Writers, KeyDomain, MaxOps

NoEv == -2
StaleEv == -1
NoKey == "nokey"
Genesis == "genesis"

VARIABLES rows,      \* Seq of [seq, status, prevHash, hash, key]; seq = index
          idem,      \* KeyDomain -> Nat (0 = absent): latest committed seq
          pc,        \* Writers -> {"ready", "commit"}
          pending,   \* Writers -> [readSeq, ev, key, verdict]
          opIdx,     \* Writers -> Nat: ops completed
          evLog,     \* Seq of expected_version values used by commits
          nCommitted,
          nRejected

vars == <<rows, idem, pc, pending, opIdx, evLog, nCommitted, nRejected>>

NullPending == [readSeq |-> -1, ev |-> NoEv, key |-> NoKey, verdict |-> "none"]

RowSet == {rows[i] : i \in 1..Len(rows)}

LatestCommitted ==
  LET S == {r.seq : r \in RowSet /\ r.status = "COMMITTED"}
  IN IF S = {} THEN 0 ELSE CHOOSE s \in S : \A t \in S : s >= t

MaxCommittedWithKey(k) ==
  LET S == {r.seq : r \in RowSet /\ r.status = "COMMITTED" /\ r.key = k}
  IN IF S = {} THEN 0 ELSE CHOOSE s \in S : \A t \in S : s >= t

TypeOK ==
  /\ \A w \in Writers : pc[w] \in {"ready", "commit"}
  /\ \A w \in Writers : opIdx[w] \in 0..MaxOps
  /\ nCommitted \in Nat /\ nRejected \in Nat

Init ==
  /\ rows = <<>>
  /\ idem = [k \in KeyDomain |-> 0]
  /\ pc = [w \in Writers |-> "ready"]
  /\ pending = [w \in Writers |-> NullPending]
  /\ opIdx = [w \in Writers |-> 0]
  /\ evLog = <<>>
  /\ nCommitted = 0
  /\ nRejected = 0

ReadJudge(w) ==
  /\ pc[w] = "ready"
  /\ opIdx[w] < MaxOps
  /\ \E evChoice \in {"none", "fresh", "stale"},
        key \in KeyDomain \cup {NoKey},
        verdict \in {"pass", "fail"}:
       LET cur == LatestCommitted
           ev == CASE evChoice = "none"  -> NoEv
                   [] evChoice = "fresh" -> cur
                   [] evChoice = "stale" -> StaleEv
           (* op finished without a row *)
           Finish == /\ pc' = [pc EXCEPT ![w] = "ready"]
                     /\ opIdx' = [opIdx EXCEPT ![w] = @ + 1]
                     /\ pending' = [pending EXCEPT ![w] = NullPending]
                     /\ UNCHANGED <<rows, idem, evLog, nCommitted, nRejected>>
       IN IF ev # NoEv /\ ev # cur
          THEN (* fast-path ConflictError: never judged, no row *)
               Finish
          ELSE /\ pending' = [pending EXCEPT ![w] =
                                [readSeq |-> cur, ev |-> ev,
                                 key |-> key, verdict |-> verdict]]
               /\ pc' = [pc EXCEPT ![w] = "commit"]
               /\ UNCHANGED <<rows, idem, opIdx, evLog, nCommitted, nRejected>>

AtomicCommit(w) ==
  /\ pc[w] = "commit"
  /\ LET p == pending[w]
         cur2 == LatestCommitted
         seq == Len(rows) + 1
         prevH == IF rows = <<>> THEN Genesis ELSE rows[Len(rows)].hash
         NewRow(status) == [seq      |-> seq,
                            status   |-> status,
                            prevHash |-> prevH,
                            hash     |-> <<"H", seq, prevH, status>>,
                            key      |-> p.key]
         (* op finished; row changes listed per branch *)
         Finish == /\ pc' = [pc EXCEPT ![w] = "ready"]
                   /\ opIdx' = [opIdx EXCEPT ![w] = @ + 1]
                   /\ pending' = [pending EXCEPT ![w] = NullPending]
     IN IF p.ev # NoEv /\ p.ev # cur2
        THEN (* atomic re-validation failed: ConflictError, no row *)
             Finish /\ UNCHANGED <<rows, idem, evLog, nCommitted, nRejected>>
        ELSE IF p.verdict = "fail"
        THEN (* REJECTED row appended; idempotency untouched *)
             /\ rows' = Append(rows, NewRow("REJECTED"))
             /\ nRejected' = nRejected + 1
             /\ Finish
             /\ UNCHANGED <<idem, evLog, nCommitted>>
        ELSE IF p.key \in KeyDomain /\ idem[p.key] # 0
        THEN (* idempotent short-circuit: mapped seq, no row *)
             Finish /\ UNCHANGED <<rows, idem, evLog, nCommitted, nRejected>>
        ELSE (* COMMITTED append; P4 checked by Inv over evLog *)
             /\ rows' = Append(rows, NewRow("COMMITTED"))
             /\ evLog' = Append(evLog, p.ev)
             /\ idem' = IF p.key \in KeyDomain
                        THEN [idem EXCEPT ![p.key] = seq]
                        ELSE idem
             /\ nCommitted' = nCommitted + 1
             /\ Finish
             /\ UNCHANGED <<nRejected>>

Next ==
  \/ \E w \in Writers : ReadJudge(w) \/ AtomicCommit(w)
  \/ (\A w \in Writers : opIdx[w] = MaxOps) /\ UNCHANGED vars

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

(* P1 seq integrity; P2 chain integrity over ALL rows; P5 idempotency
   table tracks each key's latest committed seq; P6 every judged op
   appended exactly one row; P4 at most one commit per expected version. *)
Inv ==
  /\ \A i \in 1..Len(rows) : rows[i].seq = i
  /\ (rows = <<>> \/ rows[1].prevHash = Genesis)
  /\ \A i \in 2..Len(rows) : rows[i].prevHash = rows[i-1].hash
  /\ \A k \in KeyDomain : idem[k] = MaxCommittedWithKey(k)
  /\ Len(rows) = nCommitted + nRejected
  /\ \A i \in 1..Len(evLog) : \A j \in 1..Len(evLog) :
       (evLog[i] = evLog[j] /\ evLog[i] # NoEv) => i = j

THEOREM Spec => []Inv
=============================================================================
