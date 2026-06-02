# Why checkpoints in a Merkle DAG?

The key idea: Merkle integrity ≠ agreement on which history matters.
Checkpoints solve consensus, anchoring, and recovery problems—not just integrity.

Checkpoints give us official history (up to the root hash of the checkpoint).  
Only descendants of the checkpoint are valid, going forward.  
Instead of verifying the entire DAG, we can verify checkpoint signature.  Or to verify a post-checkpoint node, we can verify the path from the last checkpoint to the given node.  The complexity of verification drops from O(N) to O(log N), or a small traversal. 


Protection against replay: 
If someone presents an older DAG, and its root is different from 


Hi Ray, 

Thanks for these questions - it's probably obvious, but I have limited experience thinking about these and other essential/practical questions for our problem.  I'll give a first shot at answering them here, and see how these answers evolve.  

'm not 100% clear on where the MDAG is stored (nodes are distributed, but the DAG is centralized?)

I'm thinking that the DAG is logically global, in the sense that...
* the identity of a node is not tied to a particular machine, or container, or file structure, 
* all participants agree upon node identities (i.e., hashes), topology (e.g., parent relationships), checkpoint (Merkle) roots

The data might be physically distributed - different locations/containers might physically store different subsets of nodes.  But all of the fragments would be compatible pieces of the same global DAG structure.  So maybe I'm just saying what you said, with one modification - the nodes are distributed, but the DAG is not global.  


what it takes to checkpoint a node/file,

The feature of checkpointing was not something that we mentioned - or were asked for - explicitly, but it seems an important feature to have.  The key idea is that Merkle integrity (the guarantee that data and its history have not been altered, based solely on hash consistency) is not the same as agreement on which history matters.  Individual node hashes give us Merkle integrity; checkpoints solve consesus and anchor an agreed-upon history.  A checkpoint is not tied to a single file or node - it is a batch commitment over a set of events.  Which set of events one elects to checkpoint - on on what basis of frequency - is a really important design consideration.  

Anyway, if we have some subset of nodes/events we would like to checkpoint, e.g., we could select all of those with security level greater than or equal to some threshold, created within the last 24 hours - here's what we would do: 
* Collect nodes, and extract hashes from all of those nodes 
* Calculate the Merkle root hash of this node collection (This is a pairwise hash-of-hashes)
* Generate a new checkpoint hash on this Merkle Root AND the previous checkpoint hash
* Store this new hash, metadata of the node collection, and pointer to the previous checkpoint.  


One practical utility is that if we have a file, we can guarantee that all events involving that file are in a checkpoint - this guarantee is provided by a Merkle Proof.  

 if it's possible to graft these operations onto an existing black-box POSIX file system, or if we'd need the underlying filesystem's support for this system to provide meaningful provenance reports 
 
My level of abstraction is too high to answer this very important question!  I don't really know right now.  It would be great, it seems, if we could graft onto a POSIX system; is this what we would want? James, what do you think? 











Wednesday, April 29

Ray asks... " if the file system is a black box and we have no ability to ask it to do things for us during its operation (i.e., hooks), what would a completely user-driven version of this system look like?"

* How did we misunderstand Ray's question?  


* In a perfect world, where we could ask the file system to do things for us, what kinds of things would we ask it to do?  

* Alternatively, What does it mean for a system to be 'user-driven'? 

* 


James wrote... "we need to make a choice between being secure as possible and not chewing up too much CPU."  Can you explain this tradeoff?  

James wrote... "we assume that users are allowed to do whatever they want to "their" copy of the file -- and we only insert ourselves into the process when the user tries to "share" (or archive -- either term works) their changes."

If we have the utility to insert ourselves into the process when the user tries to share or archive their changes, why can't we insert ourselves into the process when the user tries to edit the document? 




Here's a statement: 

In the absence of filesystem hooks, the system shifts from tracking all file operations to tracking explicitly declared state transitions—such as commit, copy, or share events—at the points where data becomes externally visible to other users or system components.

True/False?




Demo system: 

* What would a small demo system look like?  
* What steps would be necessary to develop it? 
* Should we try to synthetically create a black-box file system?

* Ray's question: ""Is there some core MDAG principles we can develop to model the resource utilization and help us understand what level of checkpointing would be reasonable?"



Answer to this question: Yes - we need to model checkpointing as a rate/batching/risk tradeoff problem.  Checkpointing is not just a mechanism—it’s a controllable parameter that governs the system’s performance–security tradeoff.

(1) Define core variables: 

λ: event rate (nodes/sec)
T: checkpoint interval (seconds)
N=λT: nodes per checkpoint
S: average node size (bytes)
H: hash cost per byte
C(N): cost to build a checkpoint
V(N): cost to verify an event
W=T: “consistency window” (uncommitted time)

(2) Model the core tradeoff.  Three competing objectives: 
(A) Computation cost (checkpointing): C(T) ~ O(\lamda T).  Larger T gives fewer checkpoints, lower compute cost.
(B) Verification cost (logarithmic): V(T) ~ O(log N).  System scales. 
(C) Risk/uncertainty.  Define consistency window: W = T.  This is the time for which events are not checkpointed, not globally committed, potentially unverifiable.  We can model risk as increasing with T: R(T) = \alpha T.  \alpha is a function of data sensitivity, threat model, rate of access. 

(3) combine into optimization problem: 
TC(T) = TotalCost(T) = a \lambda T + b log(\lambda T) + c T


Stronger: Adaptive Checkpointing. Instead of fixed T, define T = T(L), security level L; T.



Notes for 4/29/26 meeting: 

# Git the filesystem.  
All of the data is replicated completely on every node.  I have a complete version of the repository when I clone.  Inside of this, basically there's a big pool of sha1 sums that are floating around, and a particular sha1 sum will have refs to others.  Then outside of it, in another portion of the git directory, where this stuff is hidden, we have entry points: branches and tags.  
(Q: how is a tag an entry point?)

Every sha1 sum is also a file name: 1st 4 characters is broken into 2+2 characters; 

It just does normal coloring shemes to do garbage collection.  Color everthing white, go back... etc (???)

Git is also maintaining 'treeish' objects.  

# User driven: 
Means: in order for us to be made aware of some form of modifications to the file, whether its context, metadata, security profile, i.e., data or metadata, the user must perform an action. 

When the user decides to run the command ("I have modified the file; here's the file, or the modification, here's the data we need to know")
We also have to decide: 
Whether the changes / commit action - is it only on the local machine, or is it to be shared to a distributed location, local but pollable... we have to come up with all of the metadata stuff that protects the file - how are we distributing this at all?
RCS: local.  Make changes, check them in, validate them.  We create a new entry in our tree.  The file is committed and locked into its current state.  
Alternative: we have a central repository.  When we have a commit, perhaps as a single operation or double operation like git, we push our changes to our central repository, and anyone else with a copy of this file will no longer be able to push until they have pulled the changes I pushed, and merged the changes.  This is the CVS model.  In CVS, the remote storage area is the only place where the meta information is kept.  


James wrote... "we need to make a choice between being secure as possible and not chewing up too much CPU."  Can you explain this tradeoff?
James: 
"What i was tihging was: if we watned ot be really secure, we could write a program that to access a file, we could requiest through the program.  Then every 10 times a second, it looks at what we've done, and verifies that we have the right to do that.  But that chews up the CPU." 
Alternative: 
"We get a version of the file, we open file descriptor, we go on vacation for two weeks, and we still have access to the file."


At the checkout counter, we get the file, but we don't get to take the file away.  We are sent away to a booth.  Every time we hit save, the file is handed back and checked and verified for security.  IN a sense, the file never leaves the auspices of the checkout counter program.  

James: "What I like about that is, when I was suggesting FUSE, how do we prevent them from just copying it?  But if we have a system that we can only... we can stop them from using CP (copy). Or if the file is sharable, we can allow it. But we get to decide.  There's a lot to be said."


We developed and discussed the analogy of a 'checkout counter' as a layer sitting between the user and the black-box filesystem.  At one end of the control spectrum, this checkout counter keeps very careful track of everything that happens, does not let a file out of its sight.  It exists as an impermeable barrier between the user and the filesystem.  At the other end of the spectrum, our system is a kiosk off to the side of the room, and any participation in the Merkle DAG is completely user-driven.  

Implimentation: We will make Sunny Day assumptions for initial implimentation of demo system.  Still need to discuss... 

Demo system: 

* What would a small demo system look like?  
* What steps would be necessary to develop it? 





